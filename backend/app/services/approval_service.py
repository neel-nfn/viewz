import uuid

from app.db.pg import get_conn
from app.services.asset_ingest_service import create_asset_from_submission
from app.services.state_machine_service import assert_transition
from app.services.workflow_event_service import log_event


def approve_submission(research_submission_id: str, actor_id: str | None = None, conn=None):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                select rs.id, rs.research_request_id, rs.status,
                       rr.script_line_id, rr.status as request_status,
                       sl.status as line_status
                from research_submissions rs
                join research_requests rr on rr.id = rs.research_request_id
                join script_lines sl on sl.id = rr.script_line_id
                where rs.id = %s
                """,
                (research_submission_id,),
            )
            submission = cur.fetchone()
            if not submission:
                raise ValueError("Research submission not found")

            assert_transition("research_submissions", submission.get("status"), "APPROVED")
            assert_transition("research_requests", submission.get("request_status"), "APPROVED")
            assert_transition("script_lines", submission.get("line_status"), "RESEARCH_IN_PROGRESS")

            cur.execute(
                """
                update research_submissions
                set status = %s,
                    updated_at = now()
                where id = %s
                returning id, research_request_id, status
                """,
                ("APPROVED", research_submission_id),
            )

            cur.execute(
                """
                update research_requests
                set status = %s,
                    updated_at = now()
                where id = %s
                """,
                ("APPROVED", submission["research_request_id"]),
            )

            asset = create_asset_from_submission(research_submission_id, conn=conn)
            cur.execute(
                """
                update script_lines
                set status = %s,
                    updated_at = now()
                where id = %s
                returning status
                """,
                ("RESEARCH_IN_PROGRESS", submission["script_line_id"]),
            )
            log_event(
                entity_type="research_submissions",
                entity_id=research_submission_id,
                action="approve",
                from_status=submission.get("status"),
                to_status="APPROVED",
                payload={"asset_id": str(asset["id"])},
                actor_id=actor_id,
                conn=conn,
            )
            if owns_conn:
                db.commit()
            return {"submission_id": research_submission_id, "asset_id": str(asset["id"]), "status": "APPROVED"}
    except Exception:
        if owns_conn:
            db.rollback()
        raise
    finally:
        if owns_conn:
            db.close()


def reject_submission(research_submission_id: str, actor_id: str | None = None, conn=None):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                select rs.id, rs.research_request_id, rs.status,
                       rr.script_line_id, rr.status as request_status,
                       sl.status as line_status
                from research_submissions rs
                join research_requests rr on rr.id = rs.research_request_id
                join script_lines sl on sl.id = rr.script_line_id
                where rs.id = %s
                """,
                (research_submission_id,),
            )
            submission = cur.fetchone()
            if not submission:
                raise ValueError("Research submission not found")

            assert_transition("research_submissions", submission.get("status"), "REJECTED")
            assert_transition("research_requests", submission.get("request_status"), "REJECTED")
            assert_transition("script_lines", submission.get("line_status"), "NEEDS_RESEARCH")

            cur.execute(
                """
                update research_submissions
                set status = %s,
                    updated_at = now()
                where id = %s
                """,
                ("REJECTED", research_submission_id),
            )
            cur.execute(
                """
                update research_requests
                set status = %s,
                    updated_at = now()
                where id = %s
                """,
                ("REJECTED", submission["research_request_id"]),
            )
            cur.execute(
                """
                update script_lines
                set status = %s,
                    research_request_id = null,
                    matched_asset_id = null,
                    suggested_asset_id = null,
                    suggested_match_confidence = null,
                    suggestion_notes = null,
                    updated_at = now()
                where id = %s
                """,
                ("NEEDS_RESEARCH", submission["script_line_id"]),
            )
            log_event(
                entity_type="research_submissions",
                entity_id=research_submission_id,
                action="reject",
                from_status=submission.get("status"),
                to_status="REJECTED",
                actor_id=actor_id,
                conn=conn,
            )
            if owns_conn:
                db.commit()
            return {"submission_id": research_submission_id, "status": "REJECTED"}
    except Exception:
        if owns_conn:
            db.rollback()
        raise
    finally:
        if owns_conn:
            db.close()
