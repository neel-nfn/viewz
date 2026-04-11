from urllib.parse import urlparse
import uuid

from app.db.pg import get_conn
from app.services.state_machine_service import assert_transition
from app.services.workflow_event_service import log_event


def _is_valid_url(value: str) -> bool:
    try:
        parsed = urlparse(value or "")
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def validate_asset(asset_id: str, validation_type: str = "manual", notes: str = "", actor_id: str | None = None, conn=None):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                select id, org_id, research_submission_id, source_url, start_time, end_time, filename, status
                from assets
                where id = %s
                """,
                (asset_id,),
            )
            asset = cur.fetchone()
            if not asset:
                raise ValueError("Asset not found")

            cur.execute(
                """
                select sl.id, sl.status
                from script_lines sl
                join research_requests rr on rr.script_line_id = sl.id
                join research_submissions rs on rs.research_request_id = rr.id
                where rs.id = %s
                """,
                (asset.get("research_submission_id"),),
            )
            line = cur.fetchone()
            if not line:
                raise ValueError("Originating script line not found")

            result = "PASS"
            reason = notes or ""
            if not _is_valid_url(asset.get("source_url")):
                result = "FAIL"
                reason = reason or "Invalid source URL"
            elif asset.get("end_time") is None or asset.get("start_time") is None:
                result = "FAIL"
                reason = reason or "Missing time range"
            elif float(asset.get("end_time")) <= float(asset.get("start_time")):
                result = "FAIL"
                reason = reason or "Duration must be positive"
            else:
                cur.execute(
                    """
                    select id
                    from assets
                    where org_id = %s
                      and id <> %s
                      and source_url = %s
                      and start_time = %s
                      and end_time = %s
                    limit 1
                    """,
                    (asset["org_id"], asset_id, asset["source_url"], asset["start_time"], asset["end_time"]),
                )
                duplicate = cur.fetchone()
                if duplicate:
                    result = "FAIL"
                    reason = reason or "Duplicate asset detected"

            next_status = "READY" if result == "PASS" else "REJECTED"
            assert_transition("assets", asset.get("status"), next_status)
            cur.execute(
                """
                update assets
                set status = %s
                where id = %s
                """,
                (next_status, asset_id),
            )
            cur.execute(
                """
                insert into asset_validation_logs
                    (id, asset_id, validation_type, result, notes, validated_by)
                values (%s, %s, %s, %s, %s, %s)
                """,
                (str(uuid.uuid4()), asset_id, validation_type, result, reason, actor_id),
            )
            if next_status == "READY":
                assert_transition("script_lines", line.get("status"), "READY_FOR_LINK")
                cur.execute(
                    """
                    update script_lines sl
                    set status = %s,
                        suggested_asset_id = %s,
                        suggested_match_confidence = %s,
                        suggestion_notes = %s,
                        updated_at = now()
                    from research_requests rr
                    join research_submissions rs on rs.research_request_id = rr.id
                    where rr.script_line_id = sl.id
                      and rs.id = %s
                      and sl.status <> 'LINKED'
                    """,
                    ("READY_FOR_LINK", asset_id, 1.0, "Validated asset ready for linking", asset.get("research_submission_id")),
                )
            log_event(
                entity_type="assets",
                entity_id=asset_id,
                action="validate",
                from_status=asset.get("status"),
                to_status=next_status,
                payload={"validation_type": validation_type, "result": result, "notes": reason},
                actor_id=actor_id,
                conn=conn,
            )
            if owns_conn:
                db.commit()
            return {"asset_id": asset_id, "result": result, "notes": reason, "status": next_status}
    except Exception:
        if owns_conn:
            db.rollback()
        raise
    finally:
        if owns_conn:
            db.close()
