from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Optional
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

def get_supabase_client():
    client = _client()
    if not client:
        raise HTTPException(status_code=503, detail="Supabase not configured")
    return client

