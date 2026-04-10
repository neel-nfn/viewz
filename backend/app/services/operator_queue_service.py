from __future__ import annotations

import uuid
from typing import Any

from psycopg.types.json import Jsonb

from app.db.pg import get_conn
from app.services.state_machine_service import assert_transition
from app.services.workflow_event_service import log_event


def _serialize_job(row: dict[str, Any]) -> dict[str, Any]:
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


def _serialize_item(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(row["id"]),
        "operator_job_id": str(row["operator_job_id"]),
        "research_submission_id": str(row["research_submission_id"]) if row.get("research_submission_id") else None,
        "asset_id": str(row["asset_id"]) if row.get("asset_id") else None,
        "script_line_id": str(row["script_line_id"]) if row.get("script_line_id") else None,
        "status": row["status"],
        "source_url": row.get("source_url") or "",
        "requested_start_time": row.get("requested_start_time"),
        "requested_end_time": row.get("requested_end_time"),
        "normalized_filename": row.get("normalized_filename") or "",
        "storage_provider": row.get("storage_provider") or "local_stub",
        "storage_path": row.get("storage_path") or "",
        "checksum": row.get("checksum"),
        "error_message": row.get("error_message") or "",
        "retry_count": int(row.get("retry_count") or 0),
        "max_retries": int(row.get("max_retries") or 0),
        "last_retry_at": row.get("last_retry_at"),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "completed_at": row.get("completed_at"),
    }


def create_job(
    *,
    org_id: str,
    job_type: str,
    requested_by: str | None,
    assigned_to: str | None = None,
    storage_provider: str = "local_stub",
    input_payload_json: dict[str, Any] | None = None,
    conn=None,
):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            job_id = str(uuid.uuid4())
            cur.execute(
                """
                insert into operator_jobs
                    (id, org_id, job_type, status, requested_by, assigned_to, storage_provider, input_payload_json)
                values
                    (%s, %s, %s, %s, %s, %s, %s, %s)
                returning id as job_id, org_id, job_type, status, requested_by, assigned_to,
                          total_items, processed_items, failed_items, storage_provider,
                          input_payload_json, result_payload_json, error_message, locked_by, locked_at, created_at, updated_at, completed_at
                """,
                (
                    job_id,
                    org_id,
                    job_type,
                    "QUEUED",
                    requested_by,
                    assigned_to,
                    storage_provider,
                    Jsonb(input_payload_json or {}),
                ),
            )
            job = _serialize_job(cur.fetchone())
            log_event(
                entity_type="operator_jobs",
                entity_id=job_id,
                action="create",
                from_status=None,
                to_status="QUEUED",
                payload={"job_type": job_type, "storage_provider": storage_provider},
                actor_id=requested_by,
                conn=conn,
            )
            if owns_conn:
                db.commit()
            return job
    except Exception:
        if owns_conn:
            db.rollback()
        raise
    finally:
        if owns_conn:
            db.close()


def add_job_item(
    *,
    operator_job_id: str,
    research_submission_id: str | None,
    asset_id: str | None,
    script_line_id: str | None,
    source_url: str,
    requested_start_time: float | None,
    requested_end_time: float | None,
    normalized_filename: str,
    storage_provider: str = "local_stub",
    storage_path: str = "",
    checksum: str | None = None,
    conn=None,
):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            item_id = str(uuid.uuid4())
            cur.execute(
                """
                insert into operator_job_items
                    (id, operator_job_id, research_submission_id, asset_id, script_line_id, status,
                     source_url, requested_start_time, requested_end_time, normalized_filename,
                     storage_provider, storage_path, checksum)
                values
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                returning id, operator_job_id, research_submission_id, asset_id, script_line_id, status,
                          source_url, requested_start_time, requested_end_time, normalized_filename,
                          storage_provider, storage_path, checksum, error_message, retry_count, max_retries, last_retry_at, created_at, updated_at, completed_at
                """,
                (
                    item_id,
                    operator_job_id,
                    research_submission_id,
                    asset_id,
                    script_line_id,
                    "PENDING",
                    source_url or "",
                    requested_start_time,
                    requested_end_time,
                    normalized_filename,
                    storage_provider,
                    storage_path,
                    checksum,
                ),
            )
            item = _serialize_item(cur.fetchone())
            log_event(
                entity_type="operator_job_items",
                entity_id=item_id,
                action="enqueue",
                from_status=None,
                to_status="PENDING",
                payload={"operator_job_id": operator_job_id},
                conn=conn,
            )
            refresh_job_counters(operator_job_id, conn=db)
            if owns_conn:
                db.commit()
            return item
    except Exception:
        if owns_conn:
            db.rollback()
        raise
    finally:
        if owns_conn:
            db.close()


def refresh_job_counters(operator_job_id: str, conn=None):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                select
                    count(*) as total_items,
                    count(*) filter (where status in ('STORED', 'SKIPPED')) as processed_items,
                    count(*) filter (where status = 'FAILED') as failed_items
                from operator_job_items
                where operator_job_id = %s
                """,
                (operator_job_id,),
            )
            counts = cur.fetchone() or {}
            cur.execute(
                """
                update operator_jobs
                set total_items = %s,
                    processed_items = %s,
                    failed_items = %s,
                    updated_at = now()
                where id = %s
                returning id, org_id, job_type, status, requested_by, assigned_to, total_items, processed_items, failed_items, storage_provider, input_payload_json, result_payload_json, error_message, locked_by, locked_at, created_at, updated_at, completed_at
                """,
                (
                    int(counts.get("total_items") or 0),
                    int(counts.get("processed_items") or 0),
                    int(counts.get("failed_items") or 0),
                    operator_job_id,
                ),
            )
            return _serialize_job(cur.fetchone())
    finally:
        if owns_conn:
            db.close()


def start_job(operator_job_id: str, actor_id: str | None = None, conn=None):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                select id, org_id, status
                from operator_jobs
                where id = %s
                """,
                (operator_job_id,),
            )
            job = cur.fetchone()
            if not job:
                raise ValueError("Operator job not found")
            assert_transition("operator_jobs", job.get("status"), "IN_PROGRESS")
            cur.execute(
                """
                update operator_jobs
                set status = %s,
                    locked_by = %s,
                    locked_at = now(),
                    updated_at = now()
                where id = %s
                returning id, org_id, job_type, status, requested_by, assigned_to, total_items, processed_items, failed_items, storage_provider, input_payload_json, result_payload_json, error_message, locked_by, locked_at, created_at, updated_at, completed_at
                """,
                ("IN_PROGRESS", actor_id, operator_job_id),
            )
            updated = _serialize_job(cur.fetchone())
            log_event(
                entity_type="operator_jobs",
                entity_id=operator_job_id,
                action="start",
                from_status=job.get("status"),
                to_status="IN_PROGRESS",
                payload={},
                actor_id=actor_id,
                conn=conn,
            )
            if owns_conn:
                db.commit()
            return updated
    except Exception:
        if owns_conn:
            db.rollback()
        raise
    finally:
        if owns_conn:
            db.close()


def advance_item_status(operator_job_item_id: str, next_status: str, actor_id: str | None = None, error_message: str | None = None, conn=None):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                select id, operator_job_id, status, error_message
                from operator_job_items
                where id = %s
                """,
                (operator_job_item_id,),
            )
            item = cur.fetchone()
            if not item:
                raise ValueError("Operator job item not found")
            assert_transition("operator_job_items", item.get("status"), next_status)
            cur.execute(
                """
                update operator_job_items
                set status = %s,
                    error_message = %s,
                    completed_at = case when %s in ('STORED', 'FAILED', 'SKIPPED') then now() else completed_at end,
                    updated_at = now()
                where id = %s
                returning id, operator_job_id, research_submission_id, asset_id, script_line_id, status,
                          source_url, requested_start_time, requested_end_time, normalized_filename,
                          storage_provider, storage_path, checksum, error_message, retry_count, max_retries, last_retry_at, created_at, updated_at, completed_at
                """,
                (next_status, error_message or "", next_status, operator_job_item_id),
            )
            updated = _serialize_item(cur.fetchone())
            log_event(
                entity_type="operator_job_items",
                entity_id=operator_job_item_id,
                action="transition",
                from_status=item.get("status"),
                to_status=next_status,
                payload={"error_message": error_message or ""},
                actor_id=actor_id,
                conn=conn,
            )
            refresh_job_counters(str(item["operator_job_id"]), conn=db)
            if owns_conn:
                db.commit()
            return updated
    except Exception:
        if owns_conn:
            db.rollback()
        raise
    finally:
        if owns_conn:
            db.close()


def list_jobs(org_id: str, conn=None):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                select
                    id as job_id,
                    org_id,
                    job_type,
                    status,
                    requested_by,
                    assigned_to,
                    total_items,
                    processed_items,
                    failed_items,
                    storage_provider,
                    input_payload_json,
                    result_payload_json,
                    error_message,
                    locked_by,
                    locked_at,
                    created_at,
                    updated_at,
                    completed_at
                from operator_jobs
                where org_id = %s
                order by created_at desc
                """,
                (org_id,),
            )
            return [_serialize_job(row) for row in cur.fetchall()]
    finally:
        if owns_conn:
            db.close()


def get_job(operator_job_id: str, org_id: str, conn=None):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                select
                    id as job_id,
                    org_id,
                    job_type,
                    status,
                    requested_by,
                    assigned_to,
                    total_items,
                    processed_items,
                    failed_items,
                    storage_provider,
                    input_payload_json,
                    result_payload_json,
                    error_message,
                    locked_by,
                    locked_at,
                    created_at,
                    updated_at,
                    completed_at
                from operator_jobs
                where id = %s and org_id = %s
                """,
                (operator_job_id, org_id),
            )
            job = cur.fetchone()
            if not job:
                return None
            cur.execute(
                """
                select
                    id,
                    operator_job_id,
                    research_submission_id,
                    asset_id,
                    script_line_id,
                    status,
                    source_url,
                    requested_start_time,
                    requested_end_time,
                    normalized_filename,
                    storage_provider,
                    storage_path,
                    checksum,
                    error_message,
                    retry_count,
                    max_retries,
                    last_retry_at,
                    created_at,
                    updated_at,
                    completed_at
                from operator_job_items
                where operator_job_id = %s
                order by created_at asc
                """,
                (operator_job_id,),
            )
            items = [_serialize_item(row) for row in cur.fetchall()]
            payload = _serialize_job(job)
            payload["items"] = items
            return payload
    finally:
        if owns_conn:
            db.close()


def complete_job(operator_job_id: str, actor_id: str | None = None, conn=None):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                select id, org_id, status
                from operator_jobs
                where id = %s
                """,
                (operator_job_id,),
            )
            job = cur.fetchone()
            if not job:
                raise ValueError("Operator job not found")

            cur.execute(
                """
                select
                    count(*) as total_items,
                    count(*) filter (where status in ('STORED', 'SKIPPED')) as processed_items,
                    count(*) filter (where status = 'FAILED') as failed_items,
                    count(*) filter (where status = 'FAILED' and retry_count < max_retries) as retryable_failed_items,
                    count(*) filter (where status = 'PROCESSING') as processing_items,
                    count(*) filter (where status = 'PENDING') as pending_items
                from operator_job_items
                where operator_job_id = %s
                """,
                (operator_job_id,),
            )
            counts = cur.fetchone() or {}
            total = int(counts.get("total_items") or 0)
            processed = int(counts.get("processed_items") or 0)
            failed = int(counts.get("failed_items") or 0)
            retryable_failed_items = int(counts.get("retryable_failed_items") or 0)
            pending = int(counts.get("pending_items") or 0)
            processing = int(counts.get("processing_items") or 0)

            if processing:
                raise ValueError("Cannot complete a job with items still processing")
            if retryable_failed_items:
                raise ValueError("Cannot complete a job with retryable failures outstanding")
            if total == 0:
                next_status = "COMPLETED"
            elif failed == 0 and processed == total:
                next_status = "COMPLETED"
            elif processed > 0 and (processed + failed == total):
                next_status = "PARTIAL_SUCCESS"
            elif failed == total:
                next_status = "FAILED"
            elif pending > 0:
                next_status = "PARTIAL_SUCCESS" if processed > 0 or failed > 0 else "FAILED"
            else:
                next_status = "PARTIAL_SUCCESS"

            assert_transition("operator_jobs", job.get("status"), next_status)
            cur.execute(
                """
                update operator_jobs
                set status = %s,
                    total_items = %s,
                    processed_items = %s,
                    failed_items = %s,
                    result_payload_json = %s,
                    locked_by = null,
                    locked_at = null,
                    completed_at = case when %s in ('COMPLETED', 'PARTIAL_SUCCESS', 'FAILED', 'CANCELLED') then now() else completed_at end,
                    updated_at = now()
                where id = %s
                returning id as job_id, org_id, job_type, status, requested_by, assigned_to, total_items, processed_items, failed_items, storage_provider, input_payload_json, result_payload_json, error_message, locked_by, locked_at, created_at, updated_at, completed_at
                """,
                (
                    next_status,
                    total,
                    processed,
                    failed,
                    Jsonb({"total_items": total, "processed_items": processed, "failed_items": failed}),
                    next_status,
                    operator_job_id,
                ),
            )
            updated = _serialize_job(cur.fetchone())
            log_event(
                entity_type="operator_jobs",
                entity_id=operator_job_id,
                action="complete",
                from_status=job.get("status"),
                to_status=next_status,
                payload={"total_items": total, "processed_items": processed, "failed_items": failed},
                actor_id=actor_id,
                conn=conn,
            )
            if owns_conn:
                db.commit()
            return updated
    except Exception:
        if owns_conn:
            db.rollback()
        raise
    finally:
        if owns_conn:
            db.close()


def create_job_from_submissions(
    *,
    org_id: str,
    requested_by: str | None,
    assigned_to: str | None = None,
    storage_provider: str = "local_stub",
    submission_ids: list[str] | None = None,
    conn=None,
):
    from app.services.filename_service import build_normalized_filename, ensure_active_filename_rule
    from app.services.asset_ingest_service import create_asset_from_submission

    owns_conn = conn is None
    db = conn or get_conn()
    try:
        job = create_job(
            org_id=org_id,
            job_type="INGEST",
            requested_by=requested_by,
            assigned_to=assigned_to,
            storage_provider=storage_provider,
            input_payload_json={"submission_ids": submission_ids or []},
            conn=db,
        )

        with db.cursor() as cur:
            params = [org_id]
            where_clause = ["rr.org_id = %s", "rs.status = 'APPROVED'"]
            if submission_ids:
                where_clause.append("rs.id = any(%s)")
                params.append(submission_ids)
            cur.execute(
                f"""
                select
                    rs.id as research_submission_id,
                    rs.source_url,
                    rs.start_time,
                    rs.end_time,
                    rs.status as submission_status,
                    rr.script_line_id,
                    rr.keyword,
                    sl.line_number,
                    sl.raw_text,
                    s.title as script_title,
                    s.org_id,
                    a.id as asset_id,
                    a.status as asset_status,
                    a.filename
                from research_submissions rs
                join research_requests rr on rr.id = rs.research_request_id
                join script_lines sl on sl.id = rr.script_line_id
                join scripts s on s.id = sl.script_id
                left join assets a on a.research_submission_id = rs.id
                where {" and ".join(where_clause)}
                order by rs.created_at asc
                """,
                tuple(params) if len(params) > 1 else (params[0],),
            )
            rows = cur.fetchall()

        created_items = []
        skipped = 0
        rule = ensure_active_filename_rule(org_id, conn=db)
        for row in rows:
            asset_id = row.get("asset_id")
            if not asset_id:
                asset = create_asset_from_submission(str(row["research_submission_id"]), conn=db)
                asset_id = str(asset["id"])
                asset_filename = asset["filename"]
            else:
                asset_filename = row.get("filename") or ""
            if (row.get("asset_status") or "").upper() == "READY":
                skipped += 1
                continue
            preview = build_normalized_filename(
                {
                    "script_title": row.get("script_title"),
                    "line_number": row.get("line_number"),
                    "keyword": row.get("keyword"),
                    "asset_id": asset_id,
                    "extension": "mp4",
                    "source_url": row.get("source_url"),
                },
                rule=rule,
            )
            item = add_job_item(
                operator_job_id=job["job_id"],
                research_submission_id=str(row["research_submission_id"]),
                asset_id=asset_id,
                script_line_id=str(row["script_line_id"]),
                source_url=row.get("source_url") or "",
                requested_start_time=row.get("start_time"),
                requested_end_time=row.get("end_time"),
                normalized_filename=preview["normalized_filename"],
                storage_provider=storage_provider,
                storage_path="",
                checksum=None,
                conn=db,
            )
            created_items.append(item)

        refresh_job_counters(job["job_id"], conn=db)
        with db.cursor() as cur:
            cur.execute(
                """
                update operator_jobs
                set input_payload_json = %s,
                    total_items = %s,
                    updated_at = now()
                where id = %s
                """,
                (Jsonb({"submission_ids": submission_ids or [], "skipped": skipped}), len(created_items), job["job_id"]),
            )
        job["total_items"] = len(created_items)
        job["processed_items"] = 0
        job["failed_items"] = 0
        job["input_payload_json"] = {"submission_ids": submission_ids or [], "skipped": skipped}
        return {"job": job, "items": created_items, "skipped": skipped}
    except Exception:
        if owns_conn:
            db.rollback()
        raise
    finally:
        if owns_conn:
            db.close()


def retry_failed_items(operator_job_id: str, actor_id: str | None = None, backoff_seconds: int = 5, conn=None):
    from datetime import datetime

    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                select id, org_id, status
                from operator_jobs
                where id = %s
                """,
                (operator_job_id,),
            )
            job = cur.fetchone()
            if not job:
                raise ValueError("Operator job not found")

            cur.execute(
                """
                select id, retry_count, max_retries, last_retry_at
                from operator_job_items
                where operator_job_id = %s and status = 'FAILED'
                order by created_at asc
                """,
                (operator_job_id,),
            )
            rows = cur.fetchall()
            retried = 0
            skipped = 0
            now = datetime.utcnow()
            for row in rows:
                retry_count = int(row.get("retry_count") or 0)
                max_retries = int(row.get("max_retries") or 0)
                if retry_count >= max_retries:
                    skipped += 1
                    continue
                last_retry_at = row.get("last_retry_at")
                if last_retry_at is not None:
                    elapsed = (now - last_retry_at.replace(tzinfo=None) if getattr(last_retry_at, "tzinfo", None) is not None else now - last_retry_at).total_seconds()
                    required_wait = retry_count * backoff_seconds
                    if elapsed < required_wait:
                        skipped += 1
                        continue

                cur.execute(
                    """
                    update operator_job_items
                    set status = %s,
                        error_message = %s,
                        completed_at = null,
                        updated_at = now()
                    where id = %s
                    returning id
                    """,
                    ("PENDING", "", row["id"]),
                )
                updated = cur.fetchone()
                if updated:
                    retried += 1
                    log_event(
                        entity_type="operator_job_items",
                        entity_id=str(row["id"]),
                        action="retry",
                        from_status="FAILED",
                        to_status="PENDING",
                        payload={"retry_count": retry_count, "max_retries": max_retries},
                        actor_id=actor_id,
                        conn=conn,
                    )

            refresh_job_counters(operator_job_id, conn=db)
            if retried:
                assert_transition("operator_jobs", job.get("status"), "QUEUED")
                cur.execute(
                    """
                    update operator_jobs
                    set status = %s,
                        locked_by = null,
                        locked_at = null,
                        completed_at = null,
                        updated_at = now()
                    where id = %s
                    returning id, org_id, job_type, status, requested_by, assigned_to, total_items, processed_items, failed_items, storage_provider, input_payload_json, result_payload_json, error_message, locked_by, locked_at, created_at, updated_at, completed_at
                    """,
                    ("QUEUED", operator_job_id),
                )
                _ = cur.fetchone()
                log_event(
                    entity_type="operator_jobs",
                    entity_id=operator_job_id,
                    action="retry_queue",
                    from_status=job.get("status"),
                    to_status="QUEUED",
                    payload={"retried_items": retried, "skipped_items": skipped},
                    actor_id=actor_id,
                    conn=conn,
                )
            if owns_conn:
                db.commit()
            return {"job_id": operator_job_id, "status": "QUEUED", "retried_items": retried, "skipped_items": skipped}
    except Exception:
        if owns_conn:
            db.rollback()
        raise
    finally:
        if owns_conn:
            db.close()
