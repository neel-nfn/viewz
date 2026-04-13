from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Optional
from pathlib import Path
import json
import os
import base64
from ..services.supabase_service import _client

auth_scheme = HTTPBearer(auto_error=False)


def _build_local_cookie_user(request: Request) -> Dict:
    """Build a lightweight local user payload from session cookies."""
    org_id = os.getenv("ORG_ID", "00000000-0000-0000-0000-000000000000")
    email = request.cookies.get("user_email", "local@viewz.dev")
    role = request.cookies.get("user_role", "admin")
    user_id = request.cookies.get("user_id", "local_session_user")
    return {
        "sub": user_id,
        "id": user_id,
        "email": email,
        "role": role,
        "org_id": org_id,
        "auth_mode": "cookie_local",
    }


def _load_supabase_secret() -> Optional[bytes]:
    """Load SUPABASE_JWT_SECRET, return None if not set (ES256 doesn't need it)."""
    raw = os.getenv("SUPABASE_JWT_SECRET")
    if not raw:
        return None
    try:
        decoded = base64.b64decode(raw)
        if decoded:
            return decoded
    except Exception:
        pass
    return raw.encode()


SUPABASE_JWT_SECRET = _load_supabase_secret()


async def get_current_user(
    request: Request,
    creds: Optional[HTTPAuthorizationCredentials] = Depends(auth_scheme),
) -> Dict:
    from app.utils.env import is_local
    from app.utils.jwt_verifier import verify_supabase_jwt

    if not creds:
        if is_local() and request.cookies.get("viewz_session"):
            return _build_local_cookie_user(request)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = creds.credentials
    supabase_url = os.getenv("SUPABASE_URL", "")

    print("[JWT DEBUG] Verifying via JWKS...")

    try:
        payload = verify_supabase_jwt(token, supabase_url=supabase_url, legacy_secret=SUPABASE_JWT_SECRET)
        print("[JWT DEBUG] Token verified successfully!")
        return payload
    except Exception as e:
        if is_local() and request.cookies.get("viewz_session"):
            return _build_local_cookie_user(request)
        error_msg = str(e)
        print("[JWT DEBUG] Verify failed:", error_msg)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error_msg)


def get_current_user_org(user: Dict = Depends(get_current_user)) -> Dict:
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
