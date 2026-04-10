
from fastapi import APIRouter
from uuid import UUID, uuid4
from typing import Dict
from app.api.auth_google import _save_channel_and_token

router = APIRouter(prefix="/api/v1/dev", tags=["dev"])

@router.post("/upsert_dummy")
async def upsert_dummy() -> Dict:
    ch = {"id":"UC_DEV_LOCAL_001","title":"Dev Local Channel","scopes":["youtube.readonly","yt-analytics.readonly"]}
    org_id = UUID("00000000-0000-0000-0000-000000000000")
    cid = await _save_channel_and_token(ch, "dev_refresh_token_local", org_id=org_id)
    return {"ok": True, "channel_id": str(cid)}
