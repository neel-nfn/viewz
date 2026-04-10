from __future__ import annotations

import hashlib
import os
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import httpx

from app.db.pg import get_conn


LOCAL_STORAGE_ROOT = Path(os.getenv("VIEWZ_LOCAL_STORAGE_ROOT", "/tmp/viewz-storage"))
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
SUPABASE_STORAGE_BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "viewz-assets")


def compute_checksum(file_bytes: bytes | None) -> str | None:
    if file_bytes is None:
        return None
    digest = hashlib.sha256()
    digest.update(file_bytes)
    return digest.hexdigest()


def compute_storage_key(org_id: str, asset_id: str, normalized_filename: str, prefix: str = "assets") -> str:
    safe_name = re.sub(r"[^a-z0-9._-]+", "-", (normalized_filename or "asset").lower())
    return f"{prefix}/{org_id}/{asset_id}/{safe_name}"


class BaseStorageProvider(ABC):
    name: str

    @abstractmethod
    def put_object(
        self,
        *,
        object_key: str,
        content_bytes: bytes | None,
        mime_type: str | None = None,
        bucket_or_drive_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_object_url(self, object_key: str, bucket_or_drive_id: str | None = None) -> str:
        raise NotImplementedError

    @abstractmethod
    def object_exists(self, object_key: str, bucket_or_drive_id: str | None = None) -> bool:
        raise NotImplementedError


class LocalStubStorageProvider(BaseStorageProvider):
    name = "local_stub"

    def __init__(self):
        LOCAL_STORAGE_ROOT.mkdir(parents=True, exist_ok=True)

    def _local_path(self, object_key: str) -> Path:
        return LOCAL_STORAGE_ROOT / object_key

    def put_object(
        self,
        *,
        object_key: str,
        content_bytes: bytes | None,
        mime_type: str | None = None,
        bucket_or_drive_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        strict_mode: bool = True,
    ) -> dict[str, Any]:
        payload = content_bytes or b""
        path = self._local_path(object_key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        return {
            "success": True,
            "provider": self.name,
            "bucket_or_drive_id": bucket_or_drive_id or "local",
            "object_key": object_key,
            "public_url": self.get_object_url(object_key, bucket_or_drive_id),
            "mime_type": mime_type,
            "byte_size": len(payload),
            "checksum": compute_checksum(payload),
            "metadata_json": metadata or {},
        }

    def get_object_url(self, object_key: str, bucket_or_drive_id: str | None = None) -> str:
        return f"local://{object_key}"

    def object_exists(self, object_key: str, bucket_or_drive_id: str | None = None) -> bool:
        return self._local_path(object_key).exists()


class SupabaseStorageProvider(BaseStorageProvider):
    name = "supabase"

    def __init__(self):
        self.supabase_url = SUPABASE_URL
        self.service_key = SUPABASE_SERVICE_KEY
        self.bucket = SUPABASE_STORAGE_BUCKET

    def _configured(self) -> bool:
        return bool(self.supabase_url and self.service_key)

    def put_object(
        self,
        *,
        object_key: str,
        content_bytes: bytes | None,
        mime_type: str | None = None,
        bucket_or_drive_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        strict_mode: bool = True,
    ) -> dict[str, Any]:
        if not self._configured():
            raise RuntimeError("Supabase storage is not configured")

        bucket = bucket_or_drive_id or self.bucket
        public_url = self.get_object_url(object_key, bucket)
        payload = content_bytes or b""
        upload_url = f"{self.supabase_url}/storage/v1/object/{bucket}/{object_key}"

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    upload_url,
                    content=payload,
                    headers={
                        "apikey": self.service_key,
                        "Authorization": f"Bearer {self.service_key}",
                        "Content-Type": mime_type or "application/octet-stream",
                        "x-upsert": "true",
                    },
                )
                response.raise_for_status()
        except Exception as exc:
            if strict_mode:
                raise RuntimeError(f"Supabase upload failed for {object_key}: {exc}") from exc
            return {
                "success": False,
                "provider": self.name,
                "bucket_or_drive_id": bucket,
                "object_key": object_key,
                "public_url": public_url,
                "mime_type": mime_type,
                "byte_size": len(payload),
                "checksum": compute_checksum(payload),
                "metadata_json": metadata or {},
                "error": str(exc),
            }

        return {
            "success": True,
            "provider": self.name,
            "bucket_or_drive_id": bucket,
            "object_key": object_key,
            "public_url": public_url,
            "mime_type": mime_type,
            "byte_size": len(payload),
            "checksum": compute_checksum(payload),
            "metadata_json": metadata or {},
        }

    def get_object_url(self, object_key: str, bucket_or_drive_id: str | None = None) -> str:
        bucket = bucket_or_drive_id or self.bucket
        if not self.supabase_url:
            return f"supabase://{bucket}/{object_key}"
        return f"{self.supabase_url}/storage/v1/object/public/{bucket}/{object_key}"

    def object_exists(self, object_key: str, bucket_or_drive_id: str | None = None) -> bool:
        if not self._configured():
            return False
        url = self.get_object_url(object_key, bucket_or_drive_id)
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.head(url)
                return response.status_code < 400
        except Exception:
            return False


def get_storage_provider(provider: str | None) -> BaseStorageProvider:
    if (provider or "local_stub").lower() == "supabase":
        return SupabaseStorageProvider()
    return LocalStubStorageProvider()


def provider_test_status(provider: str) -> dict[str, Any]:
    storage = get_storage_provider(provider)
    return {
        "provider": storage.name,
        "healthy": storage.object_exists("healthcheck/probe.txt") if storage.name == "supabase" else True,
        "message": "ok" if storage.name == "local_stub" else ("configured" if isinstance(storage, SupabaseStorageProvider) and storage._configured() else "not configured"),
    }


def record_storage_object(
    *,
    org_id: str,
    asset_id: str | None,
    provider: str,
    bucket_or_drive_id: str | None,
    object_key: str,
    public_url: str | None,
    mime_type: str | None,
    byte_size: int | None,
    checksum: str | None,
    metadata_json: dict[str, Any] | None,
    conn=None,
):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        import uuid
        from psycopg.types.json import Jsonb

        with db.cursor() as cur:
            storage_object_id = str(uuid.uuid4())
            cur.execute(
                """
                insert into storage_objects
                    (id, org_id, asset_id, provider, bucket_or_drive_id, object_key, public_url, mime_type, byte_size, checksum, metadata_json)
                values
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                returning id, org_id, asset_id, provider, bucket_or_drive_id, object_key, public_url, mime_type, byte_size, checksum, metadata_json, created_at, updated_at
                """,
                (
                    storage_object_id,
                    org_id,
                    asset_id,
                    provider,
                    bucket_or_drive_id,
                    object_key,
                    public_url,
                    mime_type,
                    byte_size,
                    checksum,
                    Jsonb(metadata_json or {}),
                ),
            )
            return cur.fetchone()
    finally:
        if owns_conn:
            db.close()
