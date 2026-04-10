import os
from urllib.parse import quote
from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth-fixed"])

GOOGLE_AUTH = "https://accounts.google.com/o/oauth2/v2/auth"
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "")
SCOPES = os.getenv("GOOGLE_SCOPES", "https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/yt-analytics.readonly")

# Detect local dev mode
def is_local_dev():
    env = os.environ.get("ENVIRONMENT", "").lower()
    debug = os.environ.get("DEBUG", "").lower()
    return env == "local" or debug == "true"

# Check if Google OAuth credentials are configured
def has_google_creds():
    return bool(CLIENT_ID and REDIRECT_URI)

def build_auth_url(state="xyz"):
    if not CLIENT_ID or not REDIRECT_URI:
        return None
    q = (
        f"response_type=code"
        f"&client_id={quote(CLIENT_ID)}"
        f"&redirect_uri={quote(REDIRECT_URI, safe='')}"
        f"&scope={quote(SCOPES)}"
        f"&access_type=offline"
        f"&include_granted_scopes=true"
        f"&prompt=consent"
        f"&state={quote(state)}"
    )
    return f"{GOOGLE_AUTH}?{q}"

@router.get("/debug_auth_url")
def debug_auth_url():
    url = build_auth_url() or ""
    return {"client_id_set": bool(CLIENT_ID), "redirect_uri": REDIRECT_URI, "url": url}

@router.get("/login")
def login():
    # In local dev, if Google creds are missing, return stub response
    if is_local_dev() and not has_google_creds():
        return JSONResponse(
            status_code=200,
            content={
                "status": "oauth_skipped_in_local",
                "reason": "google creds not set",
                "message": "Google OAuth is not configured in local development. Using Supabase auth only."
            }
        )
    
    url = build_auth_url()
    if not url:
        # If not local dev, return error
        return Response(content="OAuth not configured (client_id / redirect_uri missing).", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": url})
