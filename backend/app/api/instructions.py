from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user, get_current_user_org
from app.db.pg import get_conn
from app.schemas.phase1_schemas import (
    EditorInstructionResponse,
    GenerateInstructionRequest,
    InstructionVersionResponse,
    UpdateInstructionRequest,
)
from app.services.instruction_engine_service import (
    generate_instruction,
    get_instruction_for_line,
    update_instruction,
)
from app.utils.org import resolve_org_id

router = APIRouter(prefix="/api/v1/instructions", tags=["instructions"])


def _serialize_bundle(bundle: dict) -> dict:
    instruction = bundle["instruction"]
    versions = bundle.get("versions") or []
    return {
        "instruction_id": str(instruction["instruction_id"]),
        "script_line_id": str(instruction["script_line_id"]),
        "asset_id": str(instruction["asset_id"]),
        "script_title": instruction["script_title"],
        "line_number": instruction["line_number"],
        "raw_text": instruction["raw_text"],
        "asset_filename": instruction["asset_filename"],
        "clip_start": float(instruction["clip_start"]),
        "clip_duration": float(instruction["clip_duration"]),
        "transition": instruction["transition"],
        "motion": instruction["motion"],
        "text_overlay": instruction["text_overlay"],
        "sound_design": instruction["sound_design"],
        "effects": instruction["effects"],
        "status": instruction["status"],
        "instruction_json": instruction["instruction_json"],
        "instruction_text": instruction["instruction_text"],
        "created_at": instruction["created_at"],
        "updated_at": instruction["updated_at"],
        "versions": [
            {
                "id": str(version["id"]),
                "instruction_id": str(version["instruction_id"]),
                "version": int(version["version"]),
                "instruction_json": version["instruction_json"],
                "created_at": version["created_at"],
            }
            for version in versions
        ],
    }


@router.post("/generate", response_model=EditorInstructionResponse)
def post_generate_instruction(
    payload: GenerateInstructionRequest,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    org_id = resolve_org_id(org.get("org_id"))
    user_id = user.get("id") or user.get("user_id") or user.get("sub") or "unknown"
    try:
        with get_conn() as conn:
            bundle = generate_instruction(
                script_line_id=payload.script_line_id,
                org_id=org_id,
                actor_id=user_id,
                conn=conn,
            )
            conn.commit()
            return _serialize_bundle(bundle)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{script_line_id}", response_model=EditorInstructionResponse)
def get_instruction(
    script_line_id: str,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    org_id = resolve_org_id(org.get("org_id"))
    try:
        with get_conn() as conn:
            bundle = get_instruction_for_line(script_line_id, org_id, conn=conn)
            if not bundle:
                raise HTTPException(status_code=404, detail="Instruction not found")
            return _serialize_bundle(bundle)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update", response_model=EditorInstructionResponse)
def post_update_instruction(
    payload: UpdateInstructionRequest,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    _ = resolve_org_id(org.get("org_id"))
    user_id = user.get("id") or user.get("user_id") or user.get("sub") or "unknown"
    try:
        with get_conn() as conn:
            result = update_instruction(
                instruction_id=payload.instruction_id,
                org_id=org_id,
                instruction_json=payload.instruction_json,
                instruction_text=payload.instruction_text,
                status=payload.status,
                actor_id=user_id,
                conn=conn,
            )
            conn.commit()
            return _serialize_bundle(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
