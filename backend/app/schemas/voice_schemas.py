from pydantic import BaseModel
from typing import Optional

class VoiceGenerateRequest(BaseModel):
    task_id: Optional[str] = None
    channel_id: Optional[str] = None
    voice_id: Optional[str] = None
    text: str

class VoiceGenerateResponse(BaseModel):
    job_id: str
    status: str

class VoiceStatusResponse(BaseModel):
    job_id: str
    status: str
    output_url: Optional[str] = None

