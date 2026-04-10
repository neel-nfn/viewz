from __future__ import annotations

import hashlib
import uuid
from typing import Any

from app.db.pg import get_conn
from app.services.workflow_event_service import log_event


def compute_checksum(file_bytes: bytes | None) -> str | None:
    if file_bytes is None:
        return None
    digest = hashlib.sha256()
    digest.update(file_bytes)
    return digest.hexdigest()


def register_fingerprint(asset_id: str, fingerprint_type: str, fingerprint_value: str, actor_id: str | None = None, conn=None):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            fingerprint_id = str(uuid.uuid4())
            cur.execute(
                """
                insert into asset_fingerprints (id, asset_id, fingerprint_type, fingerprint_value)
                values (%s, %s, %s, %s)
                on conflict (asset_id, fingerprint_type, fingerprint_value) do nothing
                returning id, asset_id, fingerprint_type, fingerprint_value, created_at
                """,
                (fingerprint_id, asset_id, fingerprint_type, fingerprint_value),
            )
            row = cur.fetchone()
            if row:
                log_event(
                    entity_type="asset_fingerprints",
                    entity_id=str(row["id"]),
                    action="register",
                    from_status=None,
                    to_status=None,
                    payload={"asset_id": asset_id, "fingerprint_type": fingerprint_type},
                    actor_id=actor_id,
                    conn=conn,
                )
            return row
    finally:
        if owns_conn:
            db.close()


def register_asset_checksum(asset_id: str, checksum: str | None, actor_id: str | None = None, conn=None):
    if not checksum:
        return None
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                update assets
                set checksum = %s,
                    updated_at = now()
                where id = %s
                returning id, checksum
                """,
                (checksum, asset_id),
            )
            row = cur.fetchone()
            if row:
                log_event(
                    entity_type="assets",
                    entity_id=asset_id,
                    action="checksum",
                    from_status=None,
                    to_status=None,
                    payload={"checksum": checksum},
                    actor_id=actor_id,
                    conn=conn,
                )
            return row
    finally:
        if owns_conn:
            db.close()


def detect_duplicate_asset(
    org_id: str,
    asset_id: str | None = None,
    checksum: str | None = None,
    fingerprint_type: str | None = None,
    fingerprint_value: str | None = None,
    conn=None,
) -> dict[str, Any]:
    owns_conn = conn is None
    db = conn or get_conn()
    duplicates: list[dict[str, Any]] = []
    try:
        with db.cursor() as cur:
            if checksum:
                cur.execute(
                    """
                    select id, filename, source_url, storage_object_id, checksum
                    from assets
                    where org_id = %s and checksum = %s
                      and (%s::uuid is null or id <> %s)
                    order by created_at asc
                    """,
                    (org_id, checksum, asset_id, asset_id),
                )
                duplicates.extend(cur.fetchall())

            if fingerprint_type and fingerprint_value:
                cur.execute(
                    """
                    select a.id, a.filename, a.source_url, a.storage_object_id, af.fingerprint_type, af.fingerprint_value
                    from asset_fingerprints af
                    join assets a on a.id = af.asset_id
                    where a.org_id = %s
                      and af.fingerprint_type = %s
                      and af.fingerprint_value = %s
                      and (%s::uuid is null or a.id <> %s)
                    order by a.created_at asc
                    """,
                    (org_id, fingerprint_type, fingerprint_value, asset_id, asset_id),
                )
                duplicates.extend(cur.fetchall())

        seen = set()
        filtered = []
        for duplicate in duplicates:
            duplicate_id = str(duplicate["id"])
            if duplicate_id in seen:
                continue
            seen.add(duplicate_id)
            filtered.append(
                {
                    "asset_id": duplicate_id,
                    "filename": duplicate.get("filename"),
                    "source_url": duplicate.get("source_url"),
                    "storage_object_id": str(duplicate.get("storage_object_id")) if duplicate.get("storage_object_id") else None,
                }
            )

        return {
            "duplicate": bool(filtered),
            "duplicates": filtered,
            "duplicate_asset_id": filtered[0]["asset_id"] if filtered else None,
            "duplicate_storage_object_id": filtered[0]["storage_object_id"] if filtered else None,
        }
    finally:
        if owns_conn:
            db.close()


def register_asset_integrity(
    *,
    asset_id: str,
    org_id: str,
    checksum: str | None,
    filename: str | None,
    source_url: str | None,
    actor_id: str | None = None,
    conn=None,
) -> dict[str, Any]:
    checksum_row = register_asset_checksum(asset_id, checksum, actor_id=actor_id, conn=conn)
    if checksum:
        register_fingerprint(asset_id, "sha256", checksum, actor_id=actor_id, conn=conn)
    if filename:
        register_fingerprint(asset_id, "filename", filename.lower(), actor_id=actor_id, conn=conn)
    if source_url:
        register_fingerprint(asset_id, "source_url", source_url.lower(), actor_id=actor_id, conn=conn)

    duplicate_info = detect_duplicate_asset(
        org_id,
        asset_id=asset_id,
        checksum=checksum,
        fingerprint_type="filename",
        fingerprint_value=(filename or "").lower() if filename else None,
        conn=conn,
    )
    if not duplicate_info["duplicate"] and checksum:
        duplicate_info = detect_duplicate_asset(
            org_id,
            asset_id=asset_id,
            checksum=checksum,
            fingerprint_type="source_url",
            fingerprint_value=(source_url or "").lower() if source_url else None,
            conn=conn,
        )

    return {
        "checksum": checksum_row["checksum"] if checksum_row else checksum,
        "duplicates": duplicate_info["duplicates"],
        "duplicate": duplicate_info["duplicate"],
        "duplicate_asset_id": duplicate_info["duplicate_asset_id"],
        "duplicate_storage_object_id": duplicate_info["duplicate_storage_object_id"],
    }


def get_asset_integrity(asset_id: str, conn=None):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                select id, org_id, checksum, storage_object_id, filename, source_url, storage_provider, storage_path, public_url, byte_size, mime_type, status
                from assets
                where id = %s
                """,
                (asset_id,),
            )
            asset = cur.fetchone()
            if not asset:
                return None

            cur.execute(
                """
                select id, asset_id, fingerprint_type, fingerprint_value, created_at
                from asset_fingerprints
                where asset_id = %s
                order by created_at asc
                """,
                (asset_id,),
            )
            fingerprints = cur.fetchall()

            cur.execute(
                """
                select id, org_id, asset_id, provider, bucket_or_drive_id, object_key, public_url, mime_type, byte_size, checksum, metadata_json, created_at, updated_at
                from storage_objects
                where asset_id = %s
                order by created_at desc
                """,
                (asset_id,),
            )
            storage_objects = cur.fetchall()

            duplicate_info = detect_duplicate_asset(
                str(asset["org_id"]),
                asset_id=asset_id,
                checksum=asset.get("checksum"),
                fingerprint_type="filename",
                fingerprint_value=(asset.get("filename") or "").lower() if asset.get("filename") else None,
                conn=db,
            )

            return {
                "asset_id": str(asset["id"]),
                "checksum": asset.get("checksum"),
                "fingerprints": fingerprints,
                "storage_objects": storage_objects,
                "duplicates": duplicate_info["duplicates"],
            }
    finally:
        if owns_conn:
            db.close()
