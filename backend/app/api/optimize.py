from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.api.deps import get_current_user_org

router = APIRouter(prefix="/api/v1/optimize", tags=["optimize"])

class Recommendation(BaseModel):
    id: str
    type: str
    priority: str
    message: str
    task_id: Optional[str] = None
    channel_id: Optional[str] = None

@router.get("/recommendations", response_model=List[Recommendation])
def get_recommendations(org=Depends(get_current_user_org)):
    return [
        Recommendation(
            id="rec-1",
            type="thumbnail",
            priority="high",
            message="CTR down 18% last 7d. Try Template B.",
            channel_id=None,
            task_id=None,
        )
    ]

