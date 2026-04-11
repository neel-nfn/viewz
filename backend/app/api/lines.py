from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user, get_current_user_org
from app.db.pg import get_conn
from app.schemas.phase1_schemas import AutoMatchRequest, AutoMatchResponse
from app.services.simple_match_service import try_auto_match
from app.utils.org import resolve_org_id

router = APIRouter(prefix="/api/v1", tags=["lines"])


@router.post("/lines/auto-match", response_model=AutoMatchResponse)
def post_auto_match(
    payload: AutoMatchRequest,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    org_id = resolve_org_id(org.get("org_id"))
    try:
        with get_conn() as conn:
            result = try_auto_match(payload.script_line_id, org_id=org_id, conn=conn)
            conn.commit()
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
