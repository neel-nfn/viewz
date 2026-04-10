import uuid

from app.db.pg import get_conn
from app.services.state_machine_service import assert_transition
from app.services.workflow_event_service import log_event


def submit_research(
    research_request_id: str,
    source_url: str,
    start_time: float,
    end_time: float,
    relevance_type: str,
    notes: str = "",
    conn=None,
):
    if not source_url:
        raise ValueError("source_url is required")
    if start_time is None:
        raise ValueError("start_time is required")
    if end_time is None:
        raise ValueError("end_time is required")
    if not relevance_type:
        raise ValueError("relevance_type is required")
    if end_time < start_time:
        raise ValueError("end_time must be greater than or equal to start_time")

    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                insert into research_submissions
                    (id, research_request_id, source_url, start_time, end_time, relevance_type, notes, status)
                values
                    (%s, %s, %s, %s, %s, %s, %s, %s)
                returning id, research_request_id, source_url, start_time, end_time, relevance_type, notes, status, created_at, updated_at
                """,
                (
                    str(uuid.uuid4()),
                    research_request_id,
                    source_url,
                    start_time,
                    end_time,
                    relevance_type,
                    notes or "",
                    "PENDING_REVIEW",
                ),
            )
            submission = cur.fetchone()
            cur.execute(
                """
                select status, script_line_id
                from research_requests
                where id = %s
                """,
                (research_request_id,),
            )
            request = cur.fetchone()
            if not request:
                raise ValueError("Research request not found")
            assert_transition("research_requests", request.get("status"), "SUBMITTED")

            cur.execute(
                """
                select status
                from script_lines
                where id = %s
                """,
                (request["script_line_id"],),
            )
            line = cur.fetchone()
            if not line:
                raise ValueError("Script line not found")
            assert_transition("script_lines", line.get("status"), "RESEARCH_IN_PROGRESS")

            cur.execute(
                """
                update research_requests
                set status = %s,
                    updated_at = now()
                where id = %s
                """,
                ("SUBMITTED", research_request_id),
            )
            cur.execute(
                """
                update script_lines
                set status = %s,
                    updated_at = now()
                where id = %s
                """,
                ("RESEARCH_IN_PROGRESS", request["script_line_id"]),
            )
            log_event(
                entity_type="research_submissions",
                entity_id=str(submission["id"]),
                action="submit",
                from_status="PENDING_REVIEW",
                to_status="PENDING_REVIEW",
                payload={"research_request_id": research_request_id},
                conn=conn,
            )
            if owns_conn:
                db.commit()
            return submission
    except Exception:
        if owns_conn:
            db.rollback()
        raise
    finally:
        if owns_conn:
            db.close()
