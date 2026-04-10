import uuid

from app.db.pg import get_conn
from app.services.state_machine_service import assert_transition
from app.services.workflow_event_service import log_event


def link_asset_to_line(
    script_line_id: str,
    asset_id: str,
    selected_start: float,
    duration: float,
    conn=None,
):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                select id, status, suggested_asset_id
                from script_lines
                where id = %s
                """,
                (script_line_id,),
            )
            line = cur.fetchone()
            if not line:
                raise ValueError("Script line not found")
            if line.get("status") != "READY_FOR_LINK":
                raise ValueError("Script line must be READY_FOR_LINK before linking")
            assert_transition("script_lines", line.get("status"), "LINKED")
            cur.execute(
                """
                select id, status
                from assets
                where id = %s
                """,
                (asset_id,),
            )
            asset = cur.fetchone()
            if not asset:
                raise ValueError("Asset not found")
            if asset.get("status") != "READY":
                raise ValueError("Asset must be READY before linking")
            cur.execute(
                """
                insert into line_asset_links (id, script_line_id, asset_id, selected_start, duration)
                values (%s, %s, %s, %s, %s)
                on conflict (script_line_id)
                do update set
                    asset_id = excluded.asset_id,
                    selected_start = excluded.selected_start,
                    duration = excluded.duration
                returning id, script_line_id, asset_id, selected_start, duration, created_at
                """,
                (str(uuid.uuid4()), script_line_id, asset_id, selected_start, duration),
            )
            link = cur.fetchone()
            cur.execute(
                """
                update script_lines
                set matched_asset_id = %s,
                    status = %s,
                    updated_at = now()
                where id = %s
                """,
                (asset_id, "LINKED", script_line_id),
            )
            log_event(
                entity_type="script_lines",
                entity_id=script_line_id,
                action="link_asset",
                from_status=line.get("status"),
                to_status="LINKED",
                payload={"asset_id": asset_id, "selected_start": selected_start, "duration": duration},
                conn=conn,
            )
            if owns_conn:
                db.commit()
            return link
    except Exception:
        if owns_conn:
            db.rollback()
        raise
    finally:
        if owns_conn:
            db.close()
