import uuid

from app.db.pg import get_conn
from app.services.filename_service import build_normalized_filename, ensure_active_filename_rule
from app.services.state_machine_service import assert_transition
from app.services.workflow_event_service import log_event


def create_asset_from_submission(research_submission_id: str, conn=None):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                select
                    id, org_id, research_submission_id, source_url, start_time, end_time, filename, status, storage_object_id
                from assets
                where research_submission_id = %s
                order by created_at asc
                limit 1
                """,
                (research_submission_id,),
            )
            existing_asset = cur.fetchone()
            if existing_asset:
                return existing_asset

            cur.execute(
                """
                select
                    rs.id as submission_id,
                    rs.status as submission_status,
                    rs.source_url,
                    rs.start_time,
                    rs.end_time,
                    rs.relevance_type,
                    rs.notes,
                    rr.org_id,
                    rr.keyword,
                    sl.line_number,
                    s.title as script_title
                from research_submissions rs
                join research_requests rr on rr.id = rs.research_request_id
                join script_lines sl on sl.id = rr.script_line_id
                join scripts s on s.id = sl.script_id
                where rs.id = %s
                """,
                (research_submission_id,),
            )
            submission = cur.fetchone()
            if not submission:
                raise ValueError("Research submission not found")
            assert_transition("research_submissions", submission.get("submission_status"), "APPROVED")

            rule = ensure_active_filename_rule(str(submission["org_id"]), conn=db)
            asset_id = str(uuid.uuid4())
            preview = build_normalized_filename(
                {
                    "script_title": submission.get("script_title"),
                    "line_number": submission.get("line_number"),
                    "keyword": submission.get("keyword"),
                    "asset_id": asset_id,
                    "extension": "mp4",
                    "source_url": submission.get("source_url"),
                },
                rule=rule,
            )
            filename = preview["normalized_filename"]
            cur.execute(
                """
                insert into assets (id, org_id, research_submission_id, source_url, start_time, end_time, filename, status)
                values (%s, %s, %s, %s, %s, %s, %s, %s)
                returning id, org_id, research_submission_id, source_url, start_time, end_time, filename, status, created_at
                """,
                (
                    asset_id,
                    submission["org_id"],
                    submission["submission_id"],
                    submission["source_url"],
                    submission["start_time"],
                    submission["end_time"],
                    filename,
                    "PENDING_VALIDATION",
                ),
            )
            asset = cur.fetchone()
            log_event(
                entity_type="assets",
                entity_id=str(asset["id"]),
                action="create_from_submission",
                from_status=None,
                to_status="PENDING_VALIDATION",
                payload={"research_submission_id": research_submission_id},
                conn=conn,
            )
            if owns_conn:
                db.commit()
            return asset
    except Exception:
        if owns_conn:
            db.rollback()
        raise
    finally:
        if owns_conn:
            db.close()
