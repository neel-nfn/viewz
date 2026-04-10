from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user, get_current_user_org
from app.db.pg import get_conn
from app.schemas.phase1_schemas import LinkAssetRequest, LinkAssetResponse
from app.services.linking_service import link_asset_to_line
from app.utils.org import resolve_org_id

router = APIRouter(prefix="/api/v1/line", tags=["linking"])


@router.post("/link-asset", response_model=LinkAssetResponse)
def post_link_asset(
    payload: LinkAssetRequest,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    _ = resolve_org_id(org.get("org_id"))
    try:
        with get_conn() as conn:
            if not payload.asset_id:
                raise HTTPException(status_code=400, detail="asset_id is required")
            link = link_asset_to_line(
                script_line_id=payload.script_line_id,
                asset_id=payload.asset_id,
                selected_start=payload.selected_start,
                duration=payload.duration,
                conn=conn,
            )
            conn.commit()
            return {
                "link_id": str(link["id"]),
                "script_line_id": str(link["script_line_id"]),
                "asset_id": str(link["asset_id"]),
                "selected_start": link["selected_start"],
                "duration": link["duration"],
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
