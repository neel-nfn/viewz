from pydantic import BaseModel
from typing import List, Optional, Dict

class AIGenerateRequest(BaseModel):
    channel_id: Optional[str] = None
    task_id: Optional[str] = None
    persona: str = "Max"
    mode: str = "script"
    prompt_text: str = ""

class AIGenerateResponse(BaseModel):
    job_id: str
    status: str
    output_url: Optional[str] = None
    model_used: Optional[str] = None

class AIHistoryResponse(BaseModel):
    items: List[Dict]

class SEOTaskRequest(BaseModel):
    org_id: str
    task_id: str
    mode: str = "seo"  # seo|script
    topic: str
    persona: str = "Max"
    temperature: float = 0.7

class SEOTaskResponse(BaseModel):
    title: str
    description: str
    tags: List[str]
    score: float
