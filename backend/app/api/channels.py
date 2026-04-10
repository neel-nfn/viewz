import os
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.api.deps import get_current_user_org
from app.services import supabase_service

router = APIRouter(prefix="/api/v1/channels", tags=["channels"])

class ChannelPublic(BaseModel):
    id: Optional[str] = None
    title: str
    youtube_channel_id: str
    status: str = "connected"
    logo_url: Optional[str] = None
    brand_color: Optional[str] = None
    ai_credits_used: Optional[int] = 0
    last_synced_at: Optional[str] = None

class RevokeRequest(BaseModel):
    channel_id: str

@router.get("/list", response_model=List[ChannelPublic])
def list_channels(org=Depends(get_current_user_org)):
    # Try Supabase first if configured
    if supabase_service.SUPABASE_URL and supabase_service.SUPABASE_SERVICE_KEY:
        c = supabase_service._client()
        if c:
            try:
                r = c.get(f"/channels?org_id=eq.{org['org_id']}&select=id,title,youtube_channel_id,status,logo_url,brand_color,ai_credits_used,last_synced_at")
                if r.status_code == 200:
                    data = r.json()
                    # Ensure we return a list
                    if isinstance(data, list):
                        return data
                    return []
            except Exception:
                # Fall through to local dev store on any error
                pass
    
    # Fallback to local dev store
    try:
        store_path = "local_dev_store/channels.json"
        if os.path.exists(store_path):
            with open(store_path, "r") as f:
                data = json.loads(f.read())
                if isinstance(data, dict):
                    # Single channel format
                    return [ChannelPublic(
                        title=data.get("title", ""),
                        youtube_channel_id=data.get("youtube_channel_id", ""),
                        status=data.get("status", "connected"),
                        logo_url=data.get("logo_url"),
                        brand_color=data.get("brand_color"),
                        ai_credits_used=data.get("ai_credits_used", 0),
                        last_synced_at=data.get("last_synced_at")
                    ).dict()]
                elif isinstance(data, list):
                    # Already a list
                    return data
    except Exception:
        pass
    
    # Return empty list if all else fails
    return []

@router.post("/revoke")
def revoke(req: RevokeRequest, org=Depends(get_current_user_org)):
    if supabase_service.SUPABASE_URL and supabase_service.SUPABASE_SERVICE_KEY:
        c = supabase_service._client()
        if c:
            upd = c.patch(f"/channels?id=eq.{req.channel_id}&org_id=eq.{org['org_id']}", content='{"status":"revoked"}')
            if upd.status_code not in (200, 204):
                raise HTTPException(status_code=400, detail="revoke_failed")
            return {"ok": True}
    
    return {"ok": True}

class SyncNowRequest(BaseModel):
    channel_id: str

@router.post("/sync_now")
def sync_now(req: SyncNowRequest, org=Depends(get_current_user_org)):
    if supabase_service.SUPABASE_URL and supabase_service.SUPABASE_SERVICE_KEY:
        c = supabase_service._client()
        if c:
            from datetime import datetime, timezone
            ts = datetime.now(timezone.utc).isoformat()
            upd = c.patch(f"/channels?id=eq.{req.channel_id}&org_id=eq.{org['org_id']}", content=f'{{"last_synced_at":"{ts}"}}')
            if upd.status_code not in (200, 204):
                raise HTTPException(status_code=400, detail="sync_failed")
            return {"ok": True, "last_synced_at": ts}
    return {"ok": True}

