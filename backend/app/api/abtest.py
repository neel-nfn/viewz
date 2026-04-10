from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.api.deps import get_current_user_org

router = APIRouter(prefix="/api/v1/abtest", tags=["abtest"])

class ABStartRequest(BaseModel):
    channel_id: str
    video_id: str
    variant_a: dict
    variant_b: dict

class ABStartResponse(BaseModel):
    id: str
    status: str

class ABResultResponse(BaseModel):
    id: str
    winner: Optional[str]
    status: str

@router.post("/start", response_model=ABStartResponse)
def start(req: ABStartRequest, org=Depends(get_current_user_org)):
    return ABStartResponse(id="abt-1", status="running")

@router.get("/result/{ab_id}", response_model=ABResultResponse)
def result(ab_id: str, org=Depends(get_current_user_org)):
    return ABResultResponse(id=ab_id, winner=None, status="running")

