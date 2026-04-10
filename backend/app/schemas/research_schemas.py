from pydantic import BaseModel, Field
from typing import Optional, Dict

class ScoreIdeaRequest(BaseModel):
    org_id: str
    channel_id: str
    title: str
    url: Optional[str] = None
    context: Optional[Dict] = None  # {keywords:[], competitors:[], recency_days:int}

class ScoreResponse(BaseModel):
    idea_id: str
    score: float = Field(..., ge=0, le=100)
    components: Dict[str, float]

