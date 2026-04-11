from fastapi import APIRouter, Response, HTTPException, Depends, Request as FastAPIRequest
from app.api.deps import get_current_user
from pydantic import BaseModel
from app.api.auth_login_fixed import build_auth_url

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

SESSION_COOKIE = "viewz_session"

FAKE_USER = {"id":"dev_user_1","name":"Viewz Developer","email":"dev@example.com","role":"admin"}

class LoginBody(BaseModel):
    provider: str
    state: str | None = None

@router.post("/login")
def start_login(body: LoginBody | None = None):
    state = (body.state or "").strip() if body else ""
    oauth_redirect_url = build_auth_url(state=state or "xyz")
    if not oauth_redirect_url:
        raise HTTPException(status_code=500, detail="OAuth not configured")
    return {"oauth_redirect_url": oauth_redirect_url}

# NOTE: Google OAuth callback is handled by app.api.auth_google.callback
# This stub callback is disabled to avoid route conflict
# If you need a dev callback, use a different path like /api/v1/auth/dev_callback
# @router.get("/callback")
# async def callback(code: str = "", state: str = "", response: Response = None, request: Request = None):
#     ... (stub implementation removed to allow real OAuth callback)

@router.get("/me")
async def read_me(request: FastAPIRequest, user = Depends(get_current_user)):
    return {"user": user}

@router.get("/debug-cookies")
async def debug_cookies(request: FastAPIRequest):
    """Debug endpoint to see what cookies the browser is sending"""
    from app.utils.auth_cookies import SESSION_COOKIE_NAME
    return {
        "cookies": request.cookies,
        "session_cookie": request.cookies.get(SESSION_COOKIE_NAME),
        "all_cookies": dict(request.cookies),
    }
