import os
from typing import Optional
from app.services import supabase_service

def _client():
    if not (supabase_service.SUPABASE_URL and supabase_service.SUPABASE_SERVICE_KEY):
        return None
    return supabase_service._client()

def rollup_org(org_id: str) -> Optional[bool]:
    """Roll up AI usage per channel for an org."""
    c = _client()
    if not c:
        return None
    
    # Get all channels for this org
    r = c.get(f"/channels?org_id=eq.{org_id}&select=id")
    if r.status_code != 200:
        return None
    
    channel_ids = [ch["id"] for ch in r.json() if ch.get("id")]
    
    # For each channel, count AI jobs from last 30 days
    from datetime import datetime, timedelta, timezone
    since = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    
    for channel_id in channel_ids:
        # Count AI jobs for this channel
        jobs_r = c.get(f"/ai_jobs?channel_id=eq.{channel_id}&created_at=gte.{since}&select=id")
        if jobs_r.status_code == 200:
            count = len(jobs_r.json())
            # Update channel's ai_credits_used
            upd = c.patch(f"/channels?id=eq.{channel_id}", content=f'{{"ai_credits_used": {count}}}')
            if upd.status_code not in (200, 204):
                continue
    
    return True

