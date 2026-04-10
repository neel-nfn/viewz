import os
import httpx
import json
from typing import Optional, Dict, Any

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

def _client():
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        return None
    return httpx.Client(
        base_url=f"{SUPABASE_URL}/rest/v1",
        headers={
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        },
        timeout=30.0
    )

def upsert_channel(org_id: str, youtube_channel_id: str, title: str, logo_url: Optional[str]) -> Optional[Dict[str, Any]]:
    c = _client()
    if not c:
        return None
    
    payload = {
        "org_id": org_id,
        "youtube_channel_id": youtube_channel_id,
        "title": title,
        "logo_url": logo_url,
        "status": "connected"
    }
    
    r = c.post("/channels?on_conflict=youtube_channel_id,org_id", content=json.dumps(payload))
    if r.status_code not in (200, 201):
        raise RuntimeError(f"upsert_channel_failed {r.status_code}: {r.text}")
    
    data = r.json()
    return data[0] if isinstance(data, list) and data else data

def insert_or_update_token(channel_id: str, refresh_token_encrypted: str) -> None:
    c = _client()
    if not c:
        return
    
    # try update first
    upd = c.patch(f"/oauth_tokens?channel_id=eq.{channel_id}", content=json.dumps({"refresh_token": refresh_token_encrypted}))
    if upd.status_code not in (200, 204):
        raise RuntimeError(f"update_token_failed {upd.status_code}: {upd.text}")
    
    # if no row updated, insert
    if upd.headers.get("content-range", "0-0/0").endswith("/0"):
        ins = c.post("/oauth_tokens", content=json.dumps({"channel_id": channel_id, "refresh_token": refresh_token_encrypted}))
        if ins.status_code not in (200, 201):
            raise RuntimeError(f"insert_token_failed {ins.status_code}: {ins.text}")

