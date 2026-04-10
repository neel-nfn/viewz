from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.api.deps import get_current_user, get_current_user_org
from app.services import integration_service
from app.utils.org import resolve_org_id

router = APIRouter(prefix="/api/v1/integrations", tags=["integrations"])

class AIKeyCreate(BaseModel):
    provider: str = "gemini"
    api_key: str

def _require_role(user, roles=("admin", "manager")):
    """Require user to have one of the specified roles."""
    user_role = user.get("role") if isinstance(user, dict) else getattr(user, "role", None)
    if user_role not in roles:
        raise HTTPException(status_code=403, detail="forbidden")
    return True

@router.get("")
def get_integrations(user=Depends(get_current_user), org=Depends(get_current_user_org)):
    """Get integration status for YouTube and AI provider."""
    org_id = resolve_org_id(org.get('org_id'))
    
    youtube_connected = integration_service.check_youtube_connected(org_id)
    ai_status = integration_service.get_ai_key_status(org_id, "gemini")
    
    return {
        "youtube_connected": youtube_connected,
        "ai_key_configured": ai_status.get("configured", False),
        "provider": ai_status.get("provider", "gemini"),
        "key_hint": ai_status.get("hint")
    }

@router.post("/ai_key")
def save_ai_key(body: AIKeyCreate, user=Depends(get_current_user), org=Depends(get_current_user_org)):
    """Save AI provider API key (encrypted with AES-GCM)."""
    _require_role(user)
    
    # Optional input sanity check
    if len(body.api_key) < 10:
        raise HTTPException(status_code=422, detail="invalid_api_key")
    
    org_id = resolve_org_id(org.get('org_id'))
    
    try:
        result = integration_service.save_ai_key(org_id, body.provider, body.api_key)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/ai_key")
def delete_ai_key(provider: str = "gemini", user=Depends(get_current_user), org=Depends(get_current_user_org)):
    """Delete AI provider API key."""
    _require_role(user)
    
    org_id = resolve_org_id(org.get('org_id'))
    
    try:
        result = integration_service.delete_ai_key(org_id, provider)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
