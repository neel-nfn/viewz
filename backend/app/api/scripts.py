from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user, get_current_user_org
from app.db.pg import get_conn
from app.schemas.phase1_schemas import CreateScriptRequest, CreateScriptResponse, ScriptDetailResponse, ScriptLineResponse
from app.services.script_service import create_script, get_script, get_script_lines
from app.utils.org import resolve_org_id

router = APIRouter(prefix="/api/v1", tags=["scripts"])


@router.post("/scripts", response_model=CreateScriptResponse)
def post_script(
    payload: CreateScriptRequest,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    org_id = resolve_org_id(org.get("org_id"))
    user_id = user.get("id") or user.get("user_id") or user.get("sub") or "unknown"
    try:
        with get_conn() as conn:
            result = create_script(
                org_id=org_id,
                title=payload.title,
                source_text=payload.source_text,
                created_by=user_id,
                status=payload.status,
                conn=conn,
            )
            conn.commit()
            return {
                "script_id": str(result["script"]["id"]),
                "title": result["script"]["title"],
                "status": result["script"]["status"],
                "lines_created": len(result["lines"]),
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scripts/{script_id}", response_model=ScriptDetailResponse)
def get_script_detail(
    script_id: str,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    org_id = resolve_org_id(org.get("org_id"))
    try:
        result = get_script(script_id, org_id)
        if not result:
            raise HTTPException(status_code=404, detail="Script not found")
        return {
            "script_id": str(result["script"]["id"]),
            "title": result["script"]["title"],
            "source_text": result["script"]["source_text"],
            "status": result["script"]["status"],
            "lines": [
                {
                    "id": str(line["id"]),
                    "script_id": str(line["script_id"]),
                    "line_number": line["line_number"],
                    "raw_text": line["raw_text"],
                    "status": line["status"],
                    "matched_asset_id": str(line["matched_asset_id"]) if line.get("matched_asset_id") else None,
                    "research_request_id": str(line["research_request_id"]) if line.get("research_request_id") else None,
                    "created_at": line["created_at"],
                    "updated_at": line["updated_at"],
                }
                for line in result["lines"]
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scripts/{script_id}/lines", response_model=list[ScriptLineResponse])
def get_script_lines_endpoint(
    script_id: str,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    org_id = resolve_org_id(org.get("org_id"))
    try:
        script = get_script(script_id, org_id)
        if not script:
            raise HTTPException(status_code=404, detail="Script not found")
        lines = get_script_lines(script_id)
        return [
            {
                "id": str(line["id"]),
                "script_id": str(line["script_id"]),
                "line_number": line["line_number"],
                "raw_text": line["raw_text"],
                "status": line["status"],
                "matched_asset_id": str(line["matched_asset_id"]) if line.get("matched_asset_id") else None,
                "research_request_id": str(line["research_request_id"]) if line.get("research_request_id") else None,
                "created_at": line["created_at"],
                "updated_at": line["updated_at"],
            }
            for line in lines
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
