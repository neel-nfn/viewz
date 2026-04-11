from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user, get_current_user_org
from app.db.pg import get_conn
from app.schemas.phase4_schemas import (
    StorageObjectListResponse,
    StorageObjectRecord,
    StorageProviderTestRequest,
    StorageProviderTestResponse,
)
from app.services.storage_provider_service import compute_storage_key, get_storage_provider
from app.utils.org import resolve_org_id

router = APIRouter(prefix="/api/v1/storage", tags=["storage"])


@router.post("/test-provider", response_model=StorageProviderTestResponse)
def post_test_provider(
    payload: StorageProviderTestRequest,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    org_id = resolve_org_id(org.get("org_id"))
    try:
        provider = get_storage_provider(payload.provider)
        preview_key = compute_storage_key(org_id, "probe", payload.object_name, prefix="test")
        preview_url = provider.get_object_url(preview_key)
        healthy = payload.provider == "local_stub" or provider.object_exists(preview_key)
        message = "ok" if healthy else "provider not reachable or not configured"
        return {
            "provider": payload.provider,
            "healthy": healthy,
            "preview_key": preview_key,
            "preview_url": preview_url,
            "message": message,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/objects", response_model=StorageObjectListResponse)
def get_storage_objects(
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    org_id = resolve_org_id(org.get("org_id"))
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                """
                select
                    so.id as storage_object_id,
                    so.org_id,
                    so.asset_id,
                    so.provider,
                    so.bucket_or_drive_id,
                    so.object_key,
                    so.public_url,
                    so.mime_type,
                    so.byte_size,
                    so.checksum,
                    so.metadata_json,
                    so.created_at,
                    so.updated_at,
                    a.filename as asset_filename,
                    a.status as asset_status
                from storage_objects so
                left join assets a on a.id = so.asset_id
                where so.org_id = %s
                order by so.created_at desc
                """,
                (org_id,),
            )
            rows = cur.fetchall()
            return {
                "items": [
                    {
                        "storage_object_id": str(row["storage_object_id"]),
                        "org_id": str(row["org_id"]),
                        "asset_id": str(row["asset_id"]) if row.get("asset_id") else None,
                        "provider": row["provider"],
                        "bucket_or_drive_id": row.get("bucket_or_drive_id"),
                        "object_key": row["object_key"],
                        "public_url": row.get("public_url"),
                        "mime_type": row.get("mime_type"),
                        "byte_size": int(row["byte_size"]) if row.get("byte_size") is not None else None,
                        "checksum": row.get("checksum"),
                        "metadata_json": row.get("metadata_json") or {},
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"],
                    }
                    for row in rows
                ]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
