from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user, get_current_user_org
from app.db.pg import get_conn
from app.schemas.phase1_schemas import AssetListItem, AssetResponse, AssetValidationRequest, AssetValidationResponse, CreateAssetFromSubmissionRequest
from app.schemas.phase4_schemas import AssetFingerprintRequest, AssetFingerprintResponse, AssetIntegrityResponse
from app.services.asset_ingest_service import create_asset_from_submission
from app.services.asset_integrity_service import detect_duplicate_asset, get_asset_integrity, register_fingerprint
from app.services.asset_validation_service import validate_asset
from app.utils.org import resolve_org_id

router = APIRouter(prefix="/api/v1/assets", tags=["assets"])


@router.post("/from-submission", response_model=AssetResponse)
def post_asset_from_submission(
    payload: CreateAssetFromSubmissionRequest,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    _ = resolve_org_id(org.get("org_id"))
    try:
        with get_conn() as conn:
            asset = create_asset_from_submission(payload.research_submission_id, conn=conn)
            conn.commit()
            return {
                "asset_id": str(asset["id"]),
                "org_id": str(asset["org_id"]),
                "source_url": asset["source_url"],
                "start_time": asset["start_time"],
                "end_time": asset["end_time"],
                "filename": asset["filename"],
                "status": asset["status"],
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{asset_id}/fingerprint", response_model=AssetFingerprintResponse)
def post_asset_fingerprint(
    asset_id: str,
    payload: AssetFingerprintRequest,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    org_id = resolve_org_id(org.get("org_id"))
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                """
                select id, org_id, filename, source_url, checksum
                from assets
                where id = %s and org_id = %s
                """,
                (asset_id, org_id),
            )
            asset = cur.fetchone()
            if not asset:
                raise HTTPException(status_code=404, detail="Asset not found")

            fingerprint_value = payload.fingerprint_value
            if not fingerprint_value:
                if payload.fingerprint_type == "sha256":
                    fingerprint_value = asset.get("checksum")
                elif payload.fingerprint_type == "filename":
                    fingerprint_value = (asset.get("filename") or "").lower()
                else:
                    fingerprint_value = (asset.get("source_url") or "").lower()
            if not fingerprint_value:
                raise HTTPException(status_code=400, detail="Unable to infer fingerprint value")

            register_fingerprint(asset_id, payload.fingerprint_type, fingerprint_value, conn=conn)
            duplicate_info = detect_duplicate_asset(
                org_id,
                asset_id=asset_id,
                fingerprint_type=payload.fingerprint_type,
                fingerprint_value=fingerprint_value,
                conn=conn,
            )
            conn.commit()
            return {
                "asset_id": asset_id,
                "fingerprint_type": payload.fingerprint_type,
                "fingerprint_value": fingerprint_value,
                "duplicate": duplicate_info["duplicate"],
                "duplicate_asset_id": duplicate_info["duplicate_asset_id"],
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{asset_id}/integrity", response_model=AssetIntegrityResponse)
def get_asset_integrity_endpoint(
    asset_id: str,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    org_id = resolve_org_id(org.get("org_id"))
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                """
                select id, org_id
                from assets
                where id = %s and org_id = %s
                """,
                (asset_id, org_id),
            )
            asset = cur.fetchone()
            if not asset:
                raise HTTPException(status_code=404, detail="Asset not found")
            summary = get_asset_integrity(asset_id, conn=conn)
            if not summary:
                raise HTTPException(status_code=404, detail="Asset integrity not found")
            return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
def list_assets(
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    org_id = resolve_org_id(org.get("org_id"))
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                """
                select
                    a.id as asset_id,
                    a.org_id,
                    a.research_submission_id,
                    a.source_url,
                    a.start_time,
                    a.end_time,
                    a.filename,
                    a.status,
                    avl_count.validation_count
                from assets a
                left join lateral (
                    select result, notes, created_at
                    from asset_validation_logs avl
                    where avl.asset_id = a.id
                    order by created_at desc
                    limit 1
                ) avl on true
                left join lateral (
                    select count(*) as validation_count
                    from asset_validation_logs avl2
                    where avl2.asset_id = a.id
                ) avl_count on true
                where a.org_id = %s
                order by a.created_at desc
                """,
                (org_id,),
            )
            rows = cur.fetchall()
            return {
                "items": [
                    {
                        "asset_id": str(row["asset_id"]),
                        "org_id": str(row["org_id"]),
                        "research_submission_id": str(row["research_submission_id"]) if row.get("research_submission_id") else None,
                        "source_url": row["source_url"],
                        "start_time": row["start_time"],
                        "end_time": row["end_time"],
                        "filename": row["filename"],
                        "status": row["status"],
                        "validation_count": int(row.get("validation_count") or 0),
                        "last_validation_result": row.get("result"),
                        "last_validation_notes": row.get("notes"),
                    }
                    for row in rows
                ]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate", response_model=AssetValidationResponse)
def post_asset_validation(
    payload: AssetValidationRequest,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    _ = resolve_org_id(org.get("org_id"))
    user_id = user.get("id") or user.get("user_id") or user.get("sub") or "unknown"
    try:
        with get_conn() as conn:
            result = validate_asset(
                asset_id=payload.asset_id,
                validation_type=payload.validation_type,
                notes=payload.notes,
                actor_id=user_id,
                conn=conn,
            )
            conn.commit()
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
