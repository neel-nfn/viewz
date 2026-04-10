import re
import uuid
from typing import Optional

from app.db.pg import get_conn


def split_into_lines(source_text: str) -> list[str]:
    text = (source_text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not text:
        return []

    lines: list[str] = []
    for block in text.split("\n"):
        block = block.strip()
        if not block:
            continue
        pieces = re.split(r"(?<=[.!?])\s+", block)
        for piece in pieces:
            cleaned = piece.strip()
            if cleaned:
                lines.append(cleaned)

    return lines or [text]


def create_script(
    org_id: str,
    title: str,
    source_text: str,
    created_by: str,
    status: str = "DRAFT",
    conn=None,
):
    script_id = str(uuid.uuid4())
    lines = split_into_lines(source_text)

    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                insert into scripts (id, org_id, title, source_text, status, created_by)
                values (%s, %s, %s, %s, %s, %s)
                returning id, org_id, title, source_text, status, created_by, created_at, updated_at
                """,
                (script_id, org_id, title, source_text, status, created_by),
            )
            script_row = cur.fetchone()

            inserted_lines = []
            for idx, raw_text in enumerate(lines, start=1):
                line_id = str(uuid.uuid4())
                cur.execute(
                    """
                    insert into script_lines (id, script_id, line_number, raw_text, status)
                    values (%s, %s, %s, %s, %s)
                    returning id, script_id, line_number, raw_text, status, matched_asset_id, research_request_id, created_at, updated_at
                    """,
                    (line_id, script_id, idx, raw_text, "NEEDS_RESEARCH"),
                )
                inserted_lines.append(cur.fetchone())

            if owns_conn:
                db.commit()

            return {
                "script": script_row,
                "lines": inserted_lines,
            }
    except Exception:
        if owns_conn:
            db.rollback()
        raise
    finally:
        if owns_conn:
            db.close()


def get_script(script_id: str, org_id: str, conn=None):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                select id, org_id, title, source_text, status, created_by, created_at, updated_at
                from scripts
                where id = %s and org_id = %s
                """,
                (script_id, org_id),
            )
            script = cur.fetchone()
            if not script:
                return None

            cur.execute(
                """
                select id, script_id, line_number, raw_text, status, matched_asset_id, research_request_id, created_at, updated_at
                from script_lines
                where script_id = %s
                order by line_number asc
                """,
                (script_id,),
            )
            lines = cur.fetchall()
            return {"script": script, "lines": lines}
    finally:
        if owns_conn:
            db.close()


def get_script_lines(script_id: str, conn=None):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                select id, script_id, line_number, raw_text, status, matched_asset_id, research_request_id, created_at, updated_at
                from script_lines
                where script_id = %s
                order by line_number asc
                """,
                (script_id,),
            )
            return cur.fetchall()
    finally:
        if owns_conn:
            db.close()
