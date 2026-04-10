import uuid

from app.db.pg import get_conn
from psycopg.types.json import Jsonb


def log_event(
    entity_type: str,
    entity_id: str,
    action: str,
    from_status: str | None,
    to_status: str | None,
    payload: dict | None = None,
    actor_id: str | None = None,
    conn=None,
):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                insert into workflow_events
                    (id, entity_type, entity_id, action, from_status, to_status, payload_jsonb, actor_id)
                values
                    (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    str(uuid.uuid4()),
                    entity_type,
                    entity_id,
                    action,
                    from_status,
                    to_status,
                    Jsonb(payload or {}),
                    actor_id,
                ),
            )
            if owns_conn:
                db.commit()
    finally:
        if owns_conn:
            db.close()
