import re
from typing import Any

from app.db.pg import get_conn
from app.services.workflow_event_service import log_event


def _tokenize(value: str) -> set[str]:
    tokens = {token for token in re.findall(r"[a-z0-9]+", (value or "").lower()) if len(token) > 2}
    return tokens


def try_auto_match(script_line_id: str, org_id: str, conn=None) -> dict[str, Any]:
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                select id, script_id, line_number, raw_text, status, suggested_asset_id, suggested_match_confidence, suggestion_notes
                from script_lines
                where id = %s
                """,
                (script_line_id,),
            )
            line = cur.fetchone()
            if not line:
                raise ValueError("Script line not found")

            line_tokens = _tokenize(line.get("raw_text") or "")
            if not line_tokens:
                return {"script_line_id": script_line_id, "matched": False}

            cur.execute(
                """
                select id, source_url, filename, start_time, end_time
                from assets
                where org_id = %s and status = 'READY'
                order by created_at desc
                """,
                (org_id,),
            )
            assets = cur.fetchall()

            best = None
            best_score = 0.0
            for asset in assets:
                haystack = f"{asset.get('source_url') or ''} {asset.get('filename') or ''}".lower()
                asset_tokens = _tokenize(haystack)
                overlap = len(line_tokens & asset_tokens)
                if overlap == 0:
                    continue
                score = overlap / max(1, len(line_tokens))
                if score > best_score:
                    best = asset
                    best_score = score

            if not best:
                return {"script_line_id": script_line_id, "matched": False}

            notes = f"Auto-match score {best_score:.2f}"
            cur.execute(
                """
                update script_lines
                set suggested_asset_id = %s,
                    suggested_match_confidence = %s,
                    suggestion_notes = %s,
                    status = case
                        when %s >= 0.35 then 'READY_FOR_LINK'
                        else status
                    end,
                    updated_at = now()
                where id = %s
                returning id, suggested_asset_id, suggested_match_confidence, suggestion_notes, status
                """,
                (best["id"], best_score, notes, best_score, script_line_id),
            )
            updated = cur.fetchone()
            log_event(
                entity_type="script_lines",
                entity_id=script_line_id,
                action="auto_match",
                from_status=line.get("status"),
                to_status=updated.get("status") if updated else line.get("status"),
                payload={"suggested_asset_id": best["id"], "confidence": best_score},
                conn=conn,
            )
            if owns_conn:
                db.commit()
            return {
                "script_line_id": script_line_id,
                "matched": True,
                "suggested_asset_id": str(best["id"]),
                "suggested_match_confidence": best_score,
                "suggestion_notes": notes,
            }
    except Exception:
        if owns_conn:
            db.rollback()
        raise
    finally:
        if owns_conn:
            db.close()
