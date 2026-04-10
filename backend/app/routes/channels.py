from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/v1/channels", tags=["channels"])

class Channel(BaseModel):
    id: str
    title: Optional[str] = None
    handle: Optional[str] = None
    channel_id: Optional[str] = None

class ChannelsResponse(BaseModel):
    channels: List[Channel]

class RevokeRequest(BaseModel):
    channel_id: str

# In-memory demo store
CHANNELS_STORE = [
    Channel(id="UC_DEMO_1", title="Demo Channel A", handle="@demoA", channel_id="UC_DEMO_1"),
    Channel(id="UC_DEMO_2", title="Demo Channel B", handle="@demoB", channel_id="UC_DEMO_2"),
]

@router.get("/list", response_model=ChannelsResponse)
async def list_channels():
    return ChannelsResponse(channels=CHANNELS_STORE)

@router.post("/connect")
async def connect_channel():
    demo = Channel(id="UC_NEW_DEMO", title="New Demo Channel", handle="@demoNew", channel_id="UC_NEW_DEMO")
    exists = any(c.id == demo.id for c in CHANNELS_STORE)
    if not exists:
        CHANNELS_STORE.append(demo)
    return {"oauth_redirect_url": "https://accounts.google.com/o/oauth2/v2/auth"}

@router.post("/revoke")
async def revoke_channel(req: RevokeRequest):
    if not req.channel_id:
        raise HTTPException(status_code=400, detail="channel_id required")
    idx = next((i for i, c in enumerate(CHANNELS_STORE) if c.channel_id == req.channel_id or c.id == req.channel_id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="channel not found")
    CHANNELS_STORE.pop(idx)
    return {"ok": True}