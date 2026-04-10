from fastapi import APIRouter, Depends, HTTPException
from app.schemas.voice_schemas import VoiceGenerateRequest, VoiceGenerateResponse, VoiceStatusResponse
from app.services.voice_service import VoiceService
from app.dependencies import require_session
from app.utils.ratelimit import voice_under_limit_org

router = APIRouter(tags=["voice"])

def get_current_org_id():
    return "org-demo"

def get_active_channel_id():
    return "chan-demo"

@router.post("/api/v1/voice/generate", response_model=VoiceGenerateResponse)
def voice_generate(body: VoiceGenerateRequest, org_id: str = Depends(get_current_org_id), user=Depends(require_session)):
    if not voice_under_limit_org(org_id, user.id, user.role):
        raise HTTPException(status_code=429, detail="Voice generation limit exceeded for today")
    channel_id = body.channel_id or "chan-demo"
    svc = VoiceService()
    res = svc.generate(org_id, channel_id, user.id, body.text, body.voice_id or "default")
    return res

@router.get("/api/v1/voice/status/{job_id}", response_model=VoiceStatusResponse)
def voice_status(job_id: str):
    svc = VoiceService()
    res = svc.status(job_id)
    return res

