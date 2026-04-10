import uuid

from app.db.pg import get_conn
from app.services.state_machine_service import assert_transition
from app.services.workflow_event_service import log_event


def generate_requests_for_script(script_id: str, org_id: str, assigned_to: str | None = None, conn=None):
    owns_conn = conn is None
    db = conn or get_conn()
    created = []
    skipped = 0
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                select id, script_id, line_number, raw_text, status, matched_asset_id, research_request_id
                from script_lines
                where script_id = %s
                order by line_number asc
                """,
                (script_id,),
            )
            lines = cur.fetchall()

            for line in lines:
                if line.get("status") != "NEEDS_RESEARCH":
                    skipped += 1
                    continue
                if line.get("matched_asset_id"):
                    skipped += 1
                    continue

                if line.get("research_request_id"):
                    skipped += 1
                    continue

                request_id = str(uuid.uuid4())
                keyword = (line.get("raw_text") or "").strip()[:240] or f"line-{line.get('line_number')}"
                request_status = "IN_PROGRESS" if assigned_to else "PENDING"
                next_line_status = "RESEARCH_IN_PROGRESS" if assigned_to else "NEEDS_RESEARCH"
                assert_transition("research_requests", "PENDING", request_status)
                assert_transition("script_lines", line.get("status"), next_line_status)
                cur.execute(
                    """
                    insert into research_requests (id, script_line_id, org_id, keyword, status, assigned_to)
                    values (%s, %s, %s, %s, %s, %s)
                    returning id, script_line_id, org_id, keyword, status, assigned_to, created_at, updated_at
                    """,
                    (request_id, line["id"], org_id, keyword, request_status, assigned_to),
                )
                request = cur.fetchone()
                cur.execute(
                    """
                    update script_lines
                    set status = %s,
                        research_request_id = %s,
                        updated_at = now()
                    where id = %s
                    """,
                    (next_line_status, request_id, line["id"]),
                )
                log_event(
                    entity_type="research_requests",
                    entity_id=request_id,
                    action="generate",
                    from_status="PENDING",
                    to_status=request_status,
                    payload={"script_line_id": line["id"], "keyword": keyword},
                    conn=conn,
                )
                created.append(request)

            if owns_conn:
                db.commit()
            return {"created": created, "created_count": len(created), "skipped_count": skipped}
    except Exception:
        if owns_conn:
            db.rollback()
        raise
    finally:
        if owns_conn:
            db.close()


def list_research_requests(org_id: str, conn=None):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                select
                    rr.id as research_request_id,
                    rr.script_line_id,
                    rr.org_id,
                    rr.keyword,
                    rr.status,
                    rr.assigned_to,
                    rr.created_at,
                    rr.updated_at,
                    sl.line_number,
                    sl.raw_text,
                    sl.suggested_asset_id,
                    sl.suggested_match_confidence,
                    sl.suggestion_notes,
                    s.title as script_title,
                    s.id as script_id,
                    sub.id as submission_id,
                    sub.source_url,
                    sub.start_time,
                    sub.end_time,
                    sub.relevance_type,
                    sub.notes,
                    sub.status as submission_status,
                    sub.created_at as submission_created_at,
                    sub.updated_at as submission_updated_at
                from research_requests rr
                join script_lines sl on sl.id = rr.script_line_id
                join scripts s on s.id = sl.script_id
                left join lateral (
                    select *
                    from research_submissions rs
                    where rs.research_request_id = rr.id
                    order by rs.created_at desc
                    limit 1
                ) sub on true
                where rr.org_id = %s
                order by rr.created_at desc
                """,
                (org_id,),
            )
            return cur.fetchall()
    finally:
        if owns_conn:
            db.close()
