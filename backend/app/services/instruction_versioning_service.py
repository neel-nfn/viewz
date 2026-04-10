from __future__ import annotations

import uuid
from typing import Any

from app.db.pg import get_conn
from psycopg.types.json import Jsonb


def get_next_instruction_version(instruction_id: str, conn=None) -> int:
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                select coalesce(max(version), 0) + 1 as next_version
                from instruction_versions
                where instruction_id = %s
                """,
                (instruction_id,),
            )
            row = cur.fetchone()
            return int(row["next_version"] if row else 1)
    finally:
        if owns_conn:
            db.close()


def save_instruction_version(instruction_id: str, version: int, instruction_json: dict[str, Any], conn=None):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            version_id = str(uuid.uuid4())
            cur.execute(
                """
                insert into instruction_versions (id, instruction_id, version, instruction_json)
                values (%s, %s, %s, %s)
                returning id, instruction_id, version, instruction_json, created_at
                """,
                (version_id, instruction_id, version, Jsonb(instruction_json)),
            )
            return cur.fetchone()
    finally:
        if owns_conn:
            db.close()


def list_instruction_versions(instruction_id: str, conn=None):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                select id, instruction_id, version, instruction_json, created_at
                from instruction_versions
                where instruction_id = %s
                order by version asc
                """,
                (instruction_id,),
            )
            return cur.fetchall()
    finally:
        if owns_conn:
            db.close()
