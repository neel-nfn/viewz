from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api.deps import get_current_user_org

router = APIRouter(prefix="/api/v1/org", tags=["org"])

class SwitchRequest(BaseModel):
    org_id: str

class SwitchResponse(BaseModel):
    active_org_id: str

@router.post("/switch", response_model=SwitchResponse)
def switch(req: SwitchRequest, org=Depends(get_current_user_org)):
    return SwitchResponse(active_org_id=req.org_id)

