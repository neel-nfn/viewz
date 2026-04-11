from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Optional
from pathlib import Path
import json
import os
import base64
import jwt
from ..services.supabase_service import _client

auth_scheme = HTTPBearer(auto_error=False)

def _load_supabase_secret() -> Optional[bytes]:
    """Load SUPABASE_JWT_SECRET, return None if not set (ES256 doesn't need it)."""
    raw = os.getenv("SUPABASE_JWT_SECRET")
    if not raw:
        return None
    # many Supabase projects give a base64-looking secret (ends with '=')
    try:
        # try to base64-decode
        decoded = base64.b64decode(raw)
        # heuristic: if decoding gives something non-empty, use it
        if decoded:
            return decoded
    except Exception:
        # not base64, fall through
        pass
    # fallback: use raw string as bytes
    return raw.encode()

SUPABASE_JWT_SECRET = _load_supabase_secret()

async def get_current_user(creds: Optional[HTTPAuthorizationCredentials] = Depends(auth_scheme)) -> Dict:
    from app.utils.jwt_verifier import verify_supabase_jwt
    
    if not creds:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    token = creds.credentials
    supabase_url = os.getenv("SUPABASE_URL", "")
    
    print("🧠 [JWT DEBUG] Verifying via JWKS...")
    
    try:
        payload = verify_supabase_jwt(token, supabase_url=supabase_url, legacy_secret=SUPABASE_JWT_SECRET)
        print("✅ [JWT DEBUG] Token verified successfully!")
        return payload
    except Exception as e:
        error_msg = str(e)
        print("❌ [JWT DEBUG] Verify failed:", error_msg)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error_msg)

def get_current_user_org(user: Dict = Depends(get_current_user)) -> Dict:
    # Extract from JWT payload (Supabase token structure)
    user_id = user.get("sub") or user.get("user_id") or user.get("id") or "unknown"
    default_org_id = user.get("org_id") or os.getenv("ORG_ID", "00000000-0000-0000-0000-000000000000")
    return {"org_id": default_org_id, "user_id": user_id}

def get_current_channel(org: Dict = Depends(get_current_user_org)) -> Dict:
    """
    Resolve the active channel for the current org.

    Returns a dict with the fields used by analytics endpoints, or an empty
    dict when no connected channel is available.
    """
    client = _client()
    if client:
        try:
            response = client.get(
                f"/channels?org_id=eq.{org['org_id']}"
                "&status=eq.connected"
                "&select=id,title,youtube_channel_id,status,logo_url,brand_color,ai_credits_used,last_synced_at"
                "&order=last_synced_at.desc.nullslast"
                "&limit=1"
            )
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and data:
                    return data[0]
        except Exception:
            pass

    try:
        store_path = Path("local_dev_store/channels.json")
        if store_path.exists():
            raw = json.loads(store_path.read_text())
            if isinstance(raw, dict):
                return raw
            if isinstance(raw, list):
                for item in raw:
                    if isinstance(item, dict) and item.get("status", "connected") == "connected":
                        return item
    except Exception:
        pass

    return {}

def get_supabase_client():
    client = _client()
    if not client:
        raise HTTPException(status_code=503, detail="Supabase not configured")
    return client
