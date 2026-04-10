from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path
from typing import Any

from app.db.pg import get_conn
from app.services.asset_ingest_service import create_asset_from_submission
from app.services.asset_integrity_service import (
    compute_checksum,
    detect_duplicate_asset,
    register_asset_integrity,
)
from app.services.downloader_service import download_and_extract
from app.services.filename_service import build_normalized_filename, ensure_active_filename_rule, validate_filename
from app.services.linking_service import link_asset_to_line
from app.services.operator_queue_service import (
    advance_item_status,
    create_job_from_submissions,
    get_job,
    refresh_job_counters,
    start_job,
)
from app.services.storage_provider_service import (
    compute_storage_key,
    get_storage_provider,
    record_storage_object,
)
from app.services.workflow_event_service import log_event


def create_operator_job_from_approved_submissions(
    *,
    org_id: str,
    requested_by: str | None,
    assigned_to: str | None = None,
    storage_provider: str = "local_stub",
    submission_ids: list[str] | None = None,
    conn=None,
):
    return create_job_from_submissions(
        org_id=org_id,
        requested_by=requested_by,
        assigned_to=assigned_to,
        storage_provider=storage_provider,
        submission_ids=submission_ids,
        conn=conn,
    )


def _load_job_item_context(operator_job_item_id: str, org_id: str, conn=None):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                select
                    oji.id as operator_job_item_id,
                    oji.operator_job_id,
                    oji.research_submission_id,
                    oji.asset_id,
                    oji.script_line_id,
                    oji.status as item_status,
                    oji.source_url,
                    oji.requested_start_time,
                    oji.requested_end_time,
                    oji.normalized_filename,
                    oji.storage_provider as item_storage_provider,
                    oji.storage_path,
                    oji.checksum,
                    oji.error_message,
                    oj.org_id,
                    oj.status as job_status,
                    oj.job_type,
                    oj.storage_provider as job_storage_provider,
                    oj.requested_by,
                    oj.assigned_to,
                    oj.input_payload_json,
                    oj.result_payload_json,
                    rr.keyword,
                    rr.status as request_status,
                    sl.line_number,
                    sl.raw_text,
                    s.title as script_title,
                    a.filename as asset_filename,
                    a.status as asset_status,
                    a.storage_provider,
                    a.storage_path as asset_storage_path,
                    a.public_url,
                    a.byte_size,
                    a.mime_type,
                    a.checksum as asset_checksum,
                    a.storage_object_id,
                    lal.id as line_asset_link_id,
                    lal.asset_id as linked_asset_id,
                    lal.selected_start,
                    lal.duration
                from operator_job_items oji
                join operator_jobs oj on oj.id = oji.operator_job_id
                left join research_submissions rs on rs.id = oji.research_submission_id
                left join research_requests rr on rr.id = rs.research_request_id
                left join script_lines sl on sl.id = oji.script_line_id
                left join scripts s on s.id = sl.script_id
                left join assets a on a.id = oji.asset_id
                left join line_asset_links lal on lal.script_line_id = sl.id
                where oji.id = %s and oj.org_id = %s
                """,
                (operator_job_item_id, org_id),
            )
            row = cur.fetchone()
            return row
    finally:
        if owns_conn:
            db.close()


def process_operator_job_item(
    *,
    operator_job_id: str,
    operator_job_item_id: str,
    org_id: str,
    actor_id: str | None = None,
    storage_provider: str | None = None,
    simulate: bool = False,
    conn=None,
):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            context = _load_job_item_context(operator_job_item_id, org_id, conn=db)
            if not context:
                raise ValueError("Operator job item not found")
            if str(context.get("operator_job_id")) != str(operator_job_id):
                raise ValueError("Operator job item does not belong to this job")
            if context.get("job_status") != "IN_PROGRESS":
                raise ValueError("Operator job must be started before processing items")
            if context.get("item_status") in {"STORED", "SKIPPED"}:
                return _bundle_from_item(operator_job_item_id, org_id, conn=db, dedupe={})

            if context.get("item_status") not in {"PENDING", "FAILED"}:
                raise ValueError(f"Cannot process item in status {context.get('item_status')}")

            cur.execute(
                """
                update operator_job_items
                set status = %s,
                    error_message = %s,
                    updated_at = now()
                where id = %s
                """,
                ("PROCESSING", "", operator_job_item_id),
            )
            log_event(
                entity_type="operator_job_items",
                entity_id=operator_job_item_id,
                action="processing",
                from_status=context.get("item_status"),
                to_status="PROCESSING",
                payload={"simulate": simulate},
                actor_id=actor_id,
                conn=conn,
            )

            asset_id = context.get("asset_id")
            if not asset_id:
                if not context.get("research_submission_id"):
                    raise ValueError("Operator job item is missing an asset and research submission")
                asset = create_asset_from_submission(str(context["research_submission_id"]), conn=db)
                asset_id = str(asset["id"])
                cur.execute(
                    """
                    update operator_job_items
                    set asset_id = %s,
                        updated_at = now()
                    where id = %s
                    """,
                    (asset_id, operator_job_item_id),
                )
                context = _load_job_item_context(operator_job_item_id, org_id, conn=db)

            if (context.get("asset_status") or "").upper() == "REJECTED":
                raise ValueError("Rejected assets cannot be ingested")

            if context.get("storage_object_id") or context.get("line_asset_link_id") or context.get("linked_asset_id") == asset_id:
                cur.execute(
                    """
                    update operator_job_items
                    set status = %s,
                        storage_provider = %s,
                        storage_path = %s,
                        checksum = %s,
                        completed_at = now(),
                        updated_at = now()
                    where id = %s
                    """,
                    (
                        "SKIPPED",
                        context.get("storage_provider") or context.get("item_storage_provider") or "local_stub",
                        context.get("asset_storage_path") or "",
                        context.get("asset_checksum"),
                        operator_job_item_id,
                    ),
                )
                log_event(
                    entity_type="operator_job_items",
                    entity_id=operator_job_item_id,
                    action="skipped_existing",
                    from_status="PROCESSING",
                    to_status="SKIPPED",
                    payload={"asset_id": asset_id, "storage_object_id": str(context.get("storage_object_id")) if context.get("storage_object_id") else None},
                    actor_id=actor_id,
                    conn=conn,
                )
                refresh_job_counters(context["operator_job_id"], conn=db)
                if owns_conn:
                    db.commit()
                return _bundle_from_item(operator_job_item_id, org_id, conn=db, dedupe={"duplicate": True})

            start_time = float(context.get("requested_start_time") or 0.0)
            end_time = float(context.get("requested_end_time") or start_time)
            downloaded_path = None
            try:
                downloaded_path = download_and_extract(context.get("source_url") or "", start_time, end_time)
                clip_path = Path(downloaded_path)
                if not clip_path.exists() or clip_path.stat().st_size <= 0:
                    raise RuntimeError("Downloaded clip is missing or empty")

                clip_bytes = clip_path.read_bytes()
                checksum = compute_checksum(clip_bytes)

                rule = ensure_active_filename_rule(org_id, conn=db)
                candidate = context.get("normalized_filename") or build_normalized_filename(
                    {
                        "script_title": context.get("script_title"),
                        "line_number": context.get("line_number"),
                        "keyword": context.get("keyword"),
                        "asset_id": asset_id,
                        "source_url": context.get("source_url"),
                        "extension": "mp4",
                    },
                    rule=rule,
                )["normalized_filename"]

                filename_check = validate_filename(
                    candidate,
                    {
                        "script_title": context.get("script_title"),
                        "line_number": context.get("line_number"),
                        "keyword": context.get("keyword"),
                        "asset_id": asset_id,
                        "source_url": context.get("source_url"),
                        "extension": "mp4",
                    },
                    rule=rule,
                    org_id=org_id,
                    conn=db,
                )
                if not filename_check["is_valid"]:
                    error_message = "; ".join(filename_check["reasons"])
                    cur.execute(
                        """
                        update operator_job_items
                        set status = %s,
                            error_message = %s,
                            retry_count = retry_count + 1,
                            last_retry_at = now(),
                            completed_at = now(),
                            updated_at = now()
                        where id = %s
                        """,
                        ("FAILED", error_message, operator_job_item_id),
                    )
                    cur.execute(
                        """
                        update assets
                        set status = %s,
                            updated_at = now()
                        where id = %s
                        """,
                        ("REJECTED", asset_id),
                    )
                    log_event(
                        entity_type="operator_job_items",
                        entity_id=operator_job_item_id,
                        action="failed",
                        from_status="PROCESSING",
                        to_status="FAILED",
                        payload={"error_message": error_message},
                        actor_id=actor_id,
                        conn=conn,
                    )
                    refresh_job_counters(context["operator_job_id"], conn=db)
                    if owns_conn:
                        db.commit()
                    raise ValueError(error_message)

                selected_provider = storage_provider or context.get("item_storage_provider") or context.get("job_storage_provider") or "local_stub"
                storage = get_storage_provider(selected_provider)
                storage_key = compute_storage_key(org_id, asset_id, candidate, prefix="operator")

                cur.execute(
                    """
                    select id, org_id, asset_id, provider, bucket_or_drive_id, object_key, public_url, mime_type, byte_size, checksum, metadata_json
                    from storage_objects
                    where org_id = %s and provider = %s and object_key = %s
                    limit 1
                    """,
                    (org_id, selected_provider, storage_key),
                )
                existing_storage = cur.fetchone()
                if existing_storage:
                    cur.execute(
                        """
                        update assets
                        set storage_provider = %s,
                            storage_path = %s,
                            public_url = %s,
                            checksum = %s,
                            byte_size = %s,
                            mime_type = %s,
                            storage_object_id = %s,
                            status = %s,
                            updated_at = now()
                        where id = %s
                        """,
                        (
                            existing_storage.get("provider") or selected_provider,
                            existing_storage.get("object_key") or storage_key,
                            existing_storage.get("public_url"),
                            existing_storage.get("checksum"),
                            existing_storage.get("byte_size"),
                            existing_storage.get("mime_type"),
                            existing_storage["id"],
                            "READY",
                            asset_id,
                        ),
                    )
                    cur.execute(
                        """
                        update operator_job_items
                        set storage_provider = %s,
                            storage_path = %s,
                            checksum = %s,
                            status = %s,
                            completed_at = now(),
                            updated_at = now()
                        where id = %s
                        """,
                        (
                            existing_storage.get("provider") or selected_provider,
                            existing_storage.get("object_key") or storage_key,
                            existing_storage.get("checksum"),
                            "SKIPPED",
                            operator_job_item_id,
                        ),
                    )
                    log_event(
                        entity_type="operator_job_items",
                        entity_id=operator_job_item_id,
                        action="skipped_existing_storage",
                        from_status="PROCESSING",
                        to_status="SKIPPED",
                        payload={"storage_object_id": str(existing_storage["id"])},
                        actor_id=actor_id,
                        conn=conn,
                    )
                    refresh_job_counters(context["operator_job_id"], conn=db)
                    if owns_conn:
                        db.commit()
                    return _bundle_from_item(operator_job_item_id, org_id, conn=db, dedupe={"duplicate": True})

                filename_payload = {
                    "script_title": context.get("script_title"),
                    "line_number": context.get("line_number"),
                    "keyword": context.get("keyword"),
                    "asset_id": asset_id,
                    "source_url": context.get("source_url"),
                    "extension": "mp4",
                }
                filename_check = validate_filename(candidate, filename_payload, rule=rule, org_id=org_id, conn=db)
                if not filename_check["is_valid"]:
                    error_message = "; ".join(filename_check["reasons"])
                    raise ValueError(error_message)

                clip_bytes = clip_path.read_bytes()
                upload = storage.put_object(
                    object_key=storage_key,
                    content_bytes=clip_bytes,
                    mime_type="video/mp4",
                    bucket_or_drive_id=None,
                    metadata={
                        "operator_job_item_id": operator_job_item_id,
                        "asset_id": asset_id,
                        "source_url": context.get("source_url"),
                        "start_time": start_time,
                        "end_time": end_time,
                    },
                    strict_mode=True,
                )
                if not upload.get("success"):
                    raise RuntimeError(upload.get("error") or "Upload failed")

                storage_object = record_storage_object(
                    org_id=org_id,
                    asset_id=asset_id,
                    provider=upload["provider"],
                    bucket_or_drive_id=upload.get("bucket_or_drive_id"),
                    object_key=upload["object_key"],
                    public_url=upload.get("public_url"),
                    mime_type=upload.get("mime_type"),
                    byte_size=upload.get("byte_size"),
                    checksum=upload.get("checksum"),
                    metadata_json=upload.get("metadata_json") or {},
                    conn=db,
                )
                integrity = register_asset_integrity(
                    asset_id=asset_id,
                    org_id=org_id,
                    checksum=upload.get("checksum"),
                    filename=candidate,
                    source_url=context.get("source_url"),
                    actor_id=actor_id,
                    conn=db,
                )

                if integrity.get("duplicate") and integrity.get("duplicate_asset_id") and integrity.get("duplicate_asset_id") != asset_id:
                    cur.execute(
                        """
                        update assets
                        set storage_provider = %s,
                            storage_path = %s,
                            public_url = %s,
                            checksum = %s,
                            byte_size = %s,
                            mime_type = %s,
                            storage_object_id = %s,
                            status = %s,
                            updated_at = now()
                        where id = %s
                        """,
                        (
                            upload["provider"],
                            upload["object_key"],
                            upload.get("public_url"),
                            upload.get("checksum"),
                            upload.get("byte_size"),
                            upload.get("mime_type"),
                            storage_object["id"],
                            "READY",
                            asset_id,
                        ),
                    )
                else:
                    cur.execute(
                        """
                        update assets
                        set storage_provider = %s,
                            storage_path = %s,
                            public_url = %s,
                            checksum = %s,
                            byte_size = %s,
                            mime_type = %s,
                            storage_object_id = %s,
                            status = %s,
                            updated_at = now()
                        where id = %s
                        """,
                        (
                            upload["provider"],
                            upload["object_key"],
                            upload.get("public_url"),
                            upload.get("checksum"),
                            upload.get("byte_size"),
                            upload.get("mime_type"),
                            storage_object["id"],
                            "READY",
                            asset_id,
                        ),
                    )

                try:
                    if context.get("line_asset_link_id") is None and context.get("script_line_id"):
                        selected_start = float(context.get("requested_start_time") or 0.0)
                        duration = max(0.0, float(context.get("requested_end_time") or selected_start) - selected_start)
                        if duration > 0:
                            link_asset_to_line(
                                script_line_id=str(context["script_line_id"]),
                                asset_id=asset_id,
                                selected_start=selected_start,
                                duration=duration,
                                conn=db,
                            )
                except Exception as link_exc:
                    log_event(
                        entity_type="assets",
                        entity_id=asset_id,
                        action="link_deferred",
                        from_status=context.get("asset_status"),
                        to_status="READY",
                        payload={"error_message": str(link_exc)},
                        actor_id=actor_id,
                        conn=conn,
                    )

                cur.execute(
                    """
                    update operator_job_items
                    set storage_provider = %s,
                        storage_path = %s,
                        checksum = %s,
                        status = %s,
                        completed_at = now(),
                        updated_at = now()
                    where id = %s
                    """,
                    (
                        upload["provider"],
                        upload["object_key"],
                        upload.get("checksum"),
                        "STORED",
                        operator_job_item_id,
                    ),
                )
                log_event(
                    entity_type="operator_job_items",
                    entity_id=operator_job_item_id,
                    action="stored",
                    from_status="PROCESSING",
                    to_status="STORED",
                    payload={"storage_object_id": str(storage_object["id"]), "checksum": upload.get("checksum")},
                    actor_id=actor_id,
                    conn=conn,
                )
                log_event(
                    entity_type="assets",
                    entity_id=asset_id,
                    action="register_storage",
                    from_status=context.get("asset_status"),
                    to_status="READY",
                    payload={"storage_object_id": str(storage_object["id"]), "checksum": upload.get("checksum")},
                    actor_id=actor_id,
                    conn=conn,
                )
                refresh_job_counters(context["operator_job_id"], conn=db)
                if owns_conn:
                    db.commit()
                return _bundle_from_item(operator_job_item_id, org_id, conn=db, dedupe=integrity)
            finally:
                if downloaded_path:
                    try:
                        clip_cleanup = Path(downloaded_path)
                        if clip_cleanup.exists():
                            clip_cleanup.unlink()
                        if clip_cleanup.parent.exists():
                            shutil.rmtree(clip_cleanup.parent, ignore_errors=True)
                    except Exception:
                        pass
    except Exception as e:
        try:
            db.rollback()
        except Exception:
            pass
        try:
            context = _load_job_item_context(operator_job_item_id, org_id, conn=db)
            if context:
                with db.cursor() as cur:
                    cur.execute(
                        """
                        update operator_job_items
                        set status = %s,
                            error_message = %s,
                            retry_count = retry_count + 1,
                            last_retry_at = now(),
                            completed_at = now(),
                            updated_at = now()
                        where id = %s
                        returning id
                        """,
                        ("FAILED", str(e), operator_job_item_id),
                    )
                    if context.get("asset_id"):
                        cur.execute(
                            """
                            update assets
                            set status = %s,
                                updated_at = now()
                            where id = %s
                            """,
                            ("REJECTED", context["asset_id"]),
                        )
                    refresh_job_counters(context["operator_job_id"], conn=db)
                    db.commit()
        except Exception:
            try:
                db.rollback()
            except Exception:
                pass
        raise
    finally:
        if owns_conn:
            db.close()


def _bundle_from_item(operator_job_item_id: str, org_id: str, conn=None, dedupe: dict[str, Any] | None = None):
    job = get_job_for_item(operator_job_item_id, org_id, conn=conn)
    item = get_item(operator_job_item_id, org_id, conn=conn)
    return {"job": job, "job_item": item, "dedupe": dedupe or {}}


def get_item(operator_job_item_id: str, org_id: str, conn=None):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
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
                where id = %s
                """,
                (operator_job_item_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
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
    finally:
        if owns_conn:
            db.close()


def get_job_for_item(operator_job_item_id: str, org_id: str, conn=None):
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
                    created_at,
                    updated_at,
                    completed_at
                from operator_jobs
                where id = (
                    select operator_job_id
                    from operator_job_items
                    where id = %s
                ) and org_id = %s
                """,
                (operator_job_item_id, org_id),
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
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "completed_at": row.get("completed_at"),
            }
    finally:
        if owns_conn:
            db.close()
