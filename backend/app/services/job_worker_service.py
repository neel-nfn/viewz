from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.db.pg import get_conn
from app.services.operator_ingest_service import process_operator_job_item
from app.services.operator_queue_service import complete_job, get_job, list_jobs
from app.services.workflow_event_service import log_event


LOCK_TTL_SECONDS = int(__import__("os").getenv("VIEWZ_WORKER_LOCK_TTL_SECONDS", "300"))
POLL_INTERVAL_SECONDS = float(__import__("os").getenv("VIEWZ_WORKER_POLL_SECONDS", "2"))
RETRY_BACKOFF_SECONDS = int(__import__("os").getenv("VIEWZ_WORKER_RETRY_BACKOFF_SECONDS", "5"))


@dataclass
class WorkerRuntime:
    worker_id: str | None = None
    running: bool = False
    thread: threading.Thread | None = None
    stop_event: threading.Event = field(default_factory=threading.Event)
    current_job_id: str | None = None
    current_item_id: str | None = None
    last_poll_at: datetime | None = None
    last_error: str | None = None
    started_at: datetime | None = None


_RUNTIME = WorkerRuntime()
_RUNTIME_LOCK = threading.Lock()


def _now() -> datetime:
    return datetime.utcnow()


def _claim_next_job(worker_id: str, conn=None) -> dict[str, Any] | None:
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                with candidate as (
                    select id
                    from operator_jobs
                    where status in ('QUEUED', 'IN_PROGRESS')
                      and (locked_at is null or locked_at < now() - (%s * interval '1 second'))
                    order by case when status = 'QUEUED' then 0 else 1 end, created_at asc
                    for update skip locked
                    limit 1
                )
                update operator_jobs oj
                set status = 'IN_PROGRESS',
                    locked_by = %s,
                    locked_at = now(),
                    updated_at = now()
                from candidate
                where oj.id = candidate.id
                returning oj.id as job_id, oj.org_id, oj.job_type, oj.status, oj.requested_by, oj.assigned_to,
                          oj.total_items, oj.processed_items, oj.failed_items, oj.storage_provider,
                          oj.input_payload_json, oj.result_payload_json, oj.error_message, oj.locked_by, oj.locked_at,
                          oj.created_at, oj.updated_at, oj.completed_at
                """,
                (LOCK_TTL_SECONDS, worker_id),
            )
            row = cur.fetchone()
            if not row:
                return None
            return {
                "job_id": str(row["job_id"]),
                "org_id": str(row["org_id"]),
                "job_type": row["job_type"],
                "status": row["status"],
                "requested_by": str(row["requested_by"]) if row.get("requested_by") else None,
                "assigned_to": str(row["assigned_to"]) if row.get("assigned_to") else None,
                "total_items": int(row.get("total_items") or 0),
                "processed_items": int(row.get("processed_items") or 0),
                "failed_items": int(row.get("failed_items") or 0),
                "storage_provider": row["storage_provider"],
                "input_payload_json": row.get("input_payload_json") or {},
                "result_payload_json": row.get("result_payload_json") or {},
                "error_message": row.get("error_message") or "",
                "locked_by": str(row["locked_by"]) if row.get("locked_by") else None,
                "locked_at": row.get("locked_at"),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "completed_at": row.get("completed_at"),
            }
    finally:
        if owns_conn:
            db.close()


def _touch_job_lock(job_id: str, worker_id: str, conn=None) -> None:
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                update operator_jobs
                set locked_at = now(),
                    locked_by = %s,
                    updated_at = now()
                where id = %s
                """,
                (worker_id, job_id),
            )
            if owns_conn:
                db.commit()
    finally:
        if owns_conn:
            db.close()


def _item_retry_due(item: dict[str, Any]) -> bool:
    retry_count = int(item.get("retry_count") or 0)
    if retry_count <= 0:
        return True
    last_retry_at = item.get("last_retry_at")
    if not last_retry_at:
        return True
    elapsed = (_now() - last_retry_at.replace(tzinfo=None) if getattr(last_retry_at, "tzinfo", None) is not None else _now() - last_retry_at).total_seconds()
    return elapsed >= retry_count * RETRY_BACKOFF_SECONDS


def _seconds_until_retry(item: dict[str, Any]) -> float:
    retry_count = int(item.get("retry_count") or 0)
    if retry_count <= 0:
        return 0.0
    last_retry_at = item.get("last_retry_at")
    if not last_retry_at:
        return 0.0
    elapsed = (_now() - last_retry_at.replace(tzinfo=None) if getattr(last_retry_at, "tzinfo", None) is not None else _now() - last_retry_at).total_seconds()
    return max(0.0, retry_count * RETRY_BACKOFF_SECONDS - elapsed)


def _job_terminal(job: dict[str, Any]) -> bool:
    for item in job.get("items", []):
        if item["status"] in {"PENDING", "PROCESSING"}:
            return False
        if item["status"] == "FAILED" and int(item.get("retry_count") or 0) < int(item.get("max_retries") or 0):
            return False
    return True


def _process_job(job_id: str, org_id: str, worker_id: str, stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        with get_conn() as conn:
            job = get_job(job_id, org_id, conn=conn)
            if not job:
                return

            progress_made = False
            next_wait = POLL_INTERVAL_SECONDS
            for item in job.get("items", []):
                if stop_event.is_set():
                    return
                if item["status"] in {"STORED", "SKIPPED"}:
                    continue
                if item["status"] == "FAILED":
                    if int(item.get("retry_count") or 0) >= int(item.get("max_retries") or 0):
                        continue
                    if not _item_retry_due(item):
                        next_wait = min(next_wait, _seconds_until_retry(item))
                        continue
                elif item["status"] == "PENDING" and not _item_retry_due(item):
                    next_wait = min(next_wait, _seconds_until_retry(item))
                    continue

                progress_made = True
                try:
                    with _RUNTIME_LOCK:
                        _RUNTIME.current_item_id = item["id"]
                    process_operator_job_item(
                        operator_job_id=job_id,
                        operator_job_item_id=item["id"],
                        org_id=org_id,
                        actor_id=worker_id,
                        storage_provider=job.get("storage_provider"),
                        simulate=False,
                        conn=conn,
                    )
                    _touch_job_lock(job_id, worker_id, conn=conn)
                except Exception as exc:
                    log_event(
                        entity_type="operator_jobs",
                        entity_id=job_id,
                        action="item_error",
                        from_status=job["status"],
                        to_status=job["status"],
                        payload={"operator_job_item_id": item["id"], "error_message": str(exc)},
                        actor_id=worker_id,
                        conn=conn,
                    )
                    _touch_job_lock(job_id, worker_id, conn=conn)
                finally:
                    with _RUNTIME_LOCK:
                        _RUNTIME.current_item_id = None

            refreshed_job = get_job(job_id, org_id, conn=conn)
            if refreshed_job and _job_terminal(refreshed_job):
                complete_job(job_id, actor_id=worker_id, conn=conn)
                log_event(
                    entity_type="operator_jobs",
                    entity_id=job_id,
                    action="worker_complete",
                    from_status=refreshed_job["status"],
                    to_status=refreshed_job["status"],
                    payload={},
                    actor_id=worker_id,
                    conn=conn,
                )
                return

            if not progress_made:
                wait_for = max(1.0, next_wait)
            else:
                wait_for = 0.2

        if stop_event.is_set():
            return
        time.sleep(wait_for)


def _worker_loop(worker_id: str, stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        with _RUNTIME_LOCK:
            _RUNTIME.last_poll_at = _now()
        claimed_job = None
        with get_conn() as conn:
            claimed_job = _claim_next_job(worker_id, conn=conn)
            if claimed_job:
                log_event(
                    entity_type="operator_jobs",
                    entity_id=claimed_job["job_id"],
                    action="worker_claim",
                    from_status="QUEUED",
                    to_status="IN_PROGRESS",
                    payload={"worker_id": worker_id},
                    actor_id=worker_id,
                    conn=conn,
                )
                conn.commit()

        if not claimed_job:
            time.sleep(POLL_INTERVAL_SECONDS)
            continue

        with _RUNTIME_LOCK:
            _RUNTIME.current_job_id = claimed_job["job_id"]
        try:
            _process_job(claimed_job["job_id"], claimed_job["org_id"], worker_id, stop_event)
        except Exception as exc:
            with _RUNTIME_LOCK:
                _RUNTIME.last_error = str(exc)
        finally:
            with _RUNTIME_LOCK:
                _RUNTIME.current_job_id = None
                _RUNTIME.current_item_id = None


def start_worker() -> dict[str, Any]:
    status: dict[str, Any]
    with _RUNTIME_LOCK:
        if _RUNTIME.running and _RUNTIME.thread and _RUNTIME.thread.is_alive():
            status = {}
        else:
            _RUNTIME.worker_id = str(uuid.uuid4())
            _RUNTIME.running = True
            _RUNTIME.stop_event = threading.Event()
            _RUNTIME.started_at = _now()
            thread = threading.Thread(target=_worker_loop, args=(_RUNTIME.worker_id, _RUNTIME.stop_event), daemon=True)
            _RUNTIME.thread = thread
            thread.start()
            status = {}

    return get_worker_status()


def stop_worker() -> dict[str, Any]:
    with _RUNTIME_LOCK:
        _RUNTIME.running = False
        if _RUNTIME.stop_event:
            _RUNTIME.stop_event.set()
        thread = _RUNTIME.thread
    if thread and thread.is_alive():
        thread.join(timeout=5.0)
    with _RUNTIME_LOCK:
        _RUNTIME.thread = None
    return get_worker_status()


def get_worker_status(org_id: str | None = None) -> dict[str, Any]:
    with _RUNTIME_LOCK:
        runtime_snapshot = {
            "worker_id": _RUNTIME.worker_id,
            "running": bool(_RUNTIME.running and _RUNTIME.thread and _RUNTIME.thread.is_alive()),
            "current_job_id": _RUNTIME.current_job_id,
            "current_item_id": _RUNTIME.current_item_id,
            "last_poll_at": _RUNTIME.last_poll_at,
            "poll_interval_seconds": POLL_INTERVAL_SECONDS,
            "message": _RUNTIME.last_error or "",
        }

    with get_conn() as conn, conn.cursor() as cur:
        if org_id:
            cur.execute(
                """
                select count(*) as queue_size
                from operator_jobs
                where org_id = %s
                  and status in ('QUEUED', 'IN_PROGRESS')
                """,
                (org_id,),
            )
            queue_size = int((cur.fetchone() or {}).get("queue_size") or 0)

            cur.execute(
                """
                select count(*) as failed_item_count
                from operator_job_items oji
                join operator_jobs oj on oj.id = oji.operator_job_id
                where oj.org_id = %s and oji.status = 'FAILED'
                """,
                (org_id,),
            )
            failed_item_count = int((cur.fetchone() or {}).get("failed_item_count") or 0)
        else:
            cur.execute(
                """
                select count(*) as queue_size
                from operator_jobs
                where status in ('QUEUED', 'IN_PROGRESS')
                """
            )
            queue_size = int((cur.fetchone() or {}).get("queue_size") or 0)

            cur.execute(
                """
                select count(*) as failed_item_count
                from operator_job_items
                where status = 'FAILED'
                """
            )
            failed_item_count = int((cur.fetchone() or {}).get("failed_item_count") or 0)

    with get_conn() as conn:
        active_jobs = list_jobs(org_id, conn=conn) if org_id else []
    active_jobs = [job for job in active_jobs if job["status"] in {"QUEUED", "IN_PROGRESS"}]

    runtime_snapshot.update(
        {
            "queue_size": queue_size,
            "active_job_count": len(active_jobs),
            "failed_item_count": failed_item_count,
            "active_jobs": active_jobs,
        }
    )
    return runtime_snapshot
