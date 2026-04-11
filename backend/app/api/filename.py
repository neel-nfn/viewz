from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user, get_current_user_org
from app.db.pg import get_conn
from app.schemas.phase4_schemas import (
    ActiveFilenameRuleResponse,
    FilenamePreviewRequest,
    FilenamePreviewResponse,
    FilenameValidateRequest,
    FilenameValidateResponse,
)
from app.services.filename_service import (
    ensure_active_filename_rule,
    list_filename_rules,
    preview_filename,
    validate_filename,
)
from app.utils.org import resolve_org_id

router = APIRouter(prefix="/api/v1/filename", tags=["filename"])


@router.get("/rules")
def get_filename_rules(
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    org_id = resolve_org_id(org.get("org_id"))
    try:
        with get_conn() as conn:
            rules = list_filename_rules(org_id, conn=conn)
            return {
                "items": [
                    {
                        "rule_id": str(rule["id"]),
                        "org_id": str(rule["org_id"]),
                        "rule_name": rule["rule_name"],
                        "pattern_template": rule["pattern_template"],
                        "is_active": bool(rule["is_active"]),
                        "created_at": rule["created_at"],
                        "updated_at": rule["updated_at"],
                    }
                    for rule in rules
                ]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rules/active", response_model=ActiveFilenameRuleResponse)
def get_active_filename_rule_endpoint(
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    org_id = resolve_org_id(org.get("org_id"))
    try:
        with get_conn() as conn:
            rule = ensure_active_filename_rule(org_id, conn=conn)
            conn.commit()
            return {
                "rule_id": str(rule["id"]),
                "rule_name": rule["rule_name"],
                "pattern_template": rule["pattern_template"],
                "is_active": bool(rule["is_active"]),
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preview", response_model=FilenamePreviewResponse)
def post_filename_preview(
    payload: FilenamePreviewRequest,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    org_id = resolve_org_id(org.get("org_id"))
    try:
        with get_conn() as conn:
            result = preview_filename(payload.model_dump(), org_id=org_id, conn=conn)
            conn.commit()
            rule = result["rule"]
            return {
                "rule_id": str(rule["id"]) if rule.get("id") else None,
                "rule_name": rule["rule_name"],
                "pattern_template": rule["pattern_template"],
                "normalized_filename": result["normalized_filename"],
                "is_valid": result["is_valid"],
                "reasons": result["reasons"],
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate", response_model=FilenameValidateResponse)
def post_filename_validate(
    payload: FilenameValidateRequest,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    org_id = resolve_org_id(org.get("org_id"))
    try:
        with get_conn() as conn:
            result = validate_filename(payload.candidate_filename, payload.model_dump(), org_id=org_id, conn=conn)
            conn.commit()
            rule = result["rule"]
            return {
                "rule_id": str(rule["id"]) if rule.get("id") else None,
                "rule_name": rule["rule_name"],
                "pattern_template": rule["pattern_template"],
                "candidate_filename": result["candidate_filename"],
                "is_valid": result["is_valid"],
                "reasons": result["reasons"],
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
