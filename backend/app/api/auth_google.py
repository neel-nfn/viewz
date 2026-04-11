import os
import urllib.parse
import httpx
import json
import logging
from pathlib import Path
from urllib.parse import parse_qs
from fastapi import APIRouter, Request, HTTPException
from app.utils.org import resolve_org_id
from fastapi.responses import RedirectResponse, JSONResponse
from datetime import datetime, timedelta
from app.services import supabase_service
from app.utils.tier_enforcement import can_add_channel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

GOOGLE_AUTH = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN = "https://oauth2.googleapis.com/token"

CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "")
SCOPE = os.environ.get("YOUTUBE_OAUTH_SCOPE", "https://www.googleapis.com/auth/youtube.readonly")

FRONTEND_OK = os.environ.get("FRONTEND_AUTH_SUCCESS_URL", "http://localhost:5173/app")
FRONTEND_FAIL = os.environ.get("FRONTEND_AUTH_FAIL_URL", "http://localhost:5173/auth/fail")
SESSION_COOKIE = "viewz_session"

# Detect local dev mode
def is_local_dev():
    env = os.environ.get("ENVIRONMENT", "").lower()
    debug = os.environ.get("DEBUG", "").lower()
    return env == "local" or debug == "true"

# Check if Google OAuth credentials are configured
def has_google_creds():
    return bool(CLIENT_ID and CLIENT_SECRET and REDIRECT_URI)

@router.get("/login")
def login(request: Request):
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
    
    # If not local dev and creds are missing, return error
    if not has_google_creds():
        raise HTTPException(
            status_code=500,
            detail="Google OAuth not configured (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, or GOOGLE_REDIRECT_URI missing)"
        )
    
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "access_type": "offline",
        "include_granted_scopes": "true",
        "prompt": "consent",
        "state": "xyz"
    }
    url = f"{GOOGLE_AUTH}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)

async def _exchange_code_for_tokens(code: str):
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(GOOGLE_TOKEN, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        if r.status_code != 200:
            raise HTTPException(status_code=400, detail=f"token_exchange_failed: {r.text}")
        return r.json()

async def _fetch_youtube_channel(access_token: str):
    url = "https://www.googleapis.com/youtube/v3/channels"
    params = {"part": "snippet", "mine": "true"}
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params, headers=headers)
        if r.status_code != 200:
            raise HTTPException(status_code=400, detail=f"youtube_fetch_failed: {r.text}")
        data = r.json()
        items = data.get("items", [])
        if not items:
            raise HTTPException(status_code=404, detail="no_channel_found_for_account")
        ch = items[0]
        return {
            "youtube_channel_id": ch["id"],
            "title": ch["snippet"]["title"],
            "logo_url": ch["snippet"]["thumbnails"]["default"]["url"] if ch["snippet"].get("thumbnails") else None
        }

try:
    from app.utils.encryption import encrypt as _enc
except Exception:
    def _enc(x: str) -> str:
        return x  # fallback no-op

async def _save_channel_and_token(ch, refresh_token: str, org_id):
    # ch is expected like {"id": "<google_channel_id>", "title": "...", "scopes": [...]} 
    org_id = resolve_org_id(org_id)
    from app.db.pg import get_conn
    print('[DEBUG CH]', ch)

    # Failsafe: if org_id is the null UUID, attempt to map to a real org in dev/local
    if str(org_id) == "00000000-0000-0000-0000-000000000000":
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("select id from organizations limit 1;")
            row = cur.fetchone()
            if row and row.get("id"):
                org_id = row["id"]
            else:
                # Create a default Local Dev Org if none exists
                cur.execute("""
                    insert into organizations (id, name, created_at)
                    values ('00000000-0000-0000-0000-000000000000', 'Local Dev Org', now())
                    on conflict (id) do nothing;
                """)

    google_channel_id = ch.get("youtube_channel_id") or ch.get("id") or (ch.get("snippet", {}) or {}).get("channelId")
    title = ch.get("title") or (ch.get("snippet", {}) or {}).get("title")
    scopes = ch.get("scopes") or []

    if not google_channel_id:
        raise RuntimeError("google_channel_id_missing")

    import psycopg
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            insert into public.youtube_channels (org_id, google_channel_id, title)
            values (%(org_id)s, %(gcid)s, %(title)s)
            on conflict (google_channel_id)
            do update set
                title = excluded.title,
                updated_at = now()
            returning id
        """, {"org_id": org_id, "gcid": google_channel_id, "title": title})
        row = cur.fetchone()
        channel_id = row["id"] if row else None

        if not channel_id:
            raise RuntimeError("channel_id_missing_after_upsert")

        cur.execute("""
            insert into youtube_tokens (channel_id, refresh_token, scopes, updated_at)
            values (%(cid)s, %(rt)s, %(sc)s, now())
            on conflict (channel_id)
            do update set refresh_token = excluded.refresh_token,
                          scopes = excluded.scopes,
                          updated_at = now()
        """, {"cid": channel_id, "rt": refresh_token or "", "sc": scopes})

    print('[UPSERT OK]', {'org_id':str(org_id),'channel_id':str(channel_id),'gcid':google_channel_id,'title':title}); return channel_id

def _parse_oauth_state(raw_state: str) -> dict[str, str]:
    """
    Parse OAuth state passed from the frontend.

    Supports:
    - plain paths like "/settings/team-roles"
    - querystring payloads like "next=/settings/team-roles&org_id=..."
    - JSON payloads like '{"next": "/settings/team-roles", "org_id": "..."}'
    """
    parsed = {"next": "/app", "org_id": os.getenv("ORG_ID", "")}
    state = (raw_state or "").strip()
    if not state:
        return parsed

    if state.startswith("/"):
        parsed["next"] = state
        return parsed

    if state.startswith("{"):
        try:
            data = json.loads(state)
            if isinstance(data, dict):
                next_value = data.get("next") or data.get("state")
                if isinstance(next_value, str) and next_value.startswith("/"):
                    parsed["next"] = next_value
                org_value = data.get("org_id") or data.get("org")
                if org_value:
                    parsed["org_id"] = str(org_value)
                return parsed
        except Exception:
            pass

    try:
        query = parse_qs(state, keep_blank_values=True)
        if query:
            next_value = (query.get("next") or query.get("state") or [""])[0]
            if isinstance(next_value, str) and next_value.startswith("/"):
                parsed["next"] = next_value
            org_value = (query.get("org_id") or query.get("org") or [""])[0]
            if org_value:
                parsed["org_id"] = org_value
            return parsed
    except Exception:
        pass

    return parsed

@router.get("/callback")
async def callback(code: str = "", state: str = ""):
    state_ctx = _parse_oauth_state(state)
    org_id = resolve_org_id(state_ctx.get("org_id"))
    next_path = state_ctx.get("next") or "/app"
    # In local dev, if Google creds are missing, return stub response
    if is_local_dev() and not has_google_creds():
        logger.info("[OAUTH_CALLBACK] Local dev mode: OAuth skipped - Google creds not set")
        return JSONResponse(
            status_code=200,
            content={
                "status": "oauth_skipped_in_local",
                "reason": "google creds not set",
                "message": "Google OAuth is not configured in local development. Using Supabase auth only.",
                "stub_user": {"id": "dev_user", "org_id": str(org_id)}
            }
        )
    
    # SENTINEL WRITE - Forces file creation at callback entry
    import os, json, pathlib, time
    _store = os.environ.get("LOCAL_STORE_DIR") or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "local_dev_store")
    pathlib.Path(_store).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(_store, "channels.json"), "w") as _f:
        json.dump([{"id": "SENTINEL_" + str(int(time.time())), "title": "Callback Hit"}], _f)
    with open(os.path.join(_store, "oauth_token.json"), "w") as _f:
        json.dump({"ok": True, "t": "sentinel"}, _f)
    logger.info(f"[OAUTH_CALLBACK] SENTINEL WRITE COMPLETE - Store: {_store}")
    
    logger.info(f"[OAUTH_CALLBACK] Callback received: code={'present' if code else 'MISSING'}, org_id={org_id}, next={next_path}")
    
    if not code:
        logger.error("[OAUTH_CALLBACK] ❌ Missing code parameter")
        return RedirectResponse(f"{FRONTEND_FAIL}?error=missing_code")
    
    # If not local dev and creds are missing, return error
    if not has_google_creds():
        logger.error("[OAUTH_CALLBACK] ❌ Google OAuth not configured")
        return RedirectResponse(f"{FRONTEND_FAIL}?error=oauth_not_configured")
    
    try:
        logger.info("[OAUTH_CALLBACK] Exchanging code for tokens...")
        tok = await _exchange_code_for_tokens(code)
        access_token = tok.get("access_token")
        refresh_token = tok.get("refresh_token")
        
        logger.info(f"[OAUTH_CALLBACK] Token exchange: access_token={'present' if access_token else 'MISSING'}, refresh_token={'present' if refresh_token else 'MISSING'}")
        
        if not access_token:
            logger.error("[OAUTH_CALLBACK] ❌ No access_token received")
            return RedirectResponse(f"{FRONTEND_FAIL}?error=no_access_token")
        
        if not refresh_token:
            logger.warning("[OAUTH_CALLBACK] ⚠️  No refresh_token (Google may omit if previously consented)")
            # Google may omit refresh_token if user previously consented; consider prompt=consent & access_type=offline or token refresh path.
        
        logger.info("[OAUTH_CALLBACK] Fetching YouTube channel...")
        ch = await _fetch_youtube_channel(access_token)
        logger.info(f"[OAUTH_CALLBACK] Channel fetched: {ch.get('title', 'UNKNOWN')} (ID: {ch.get('youtube_channel_id', 'UNKNOWN')})")
        
        # Check tier limits before saving
        can_add, error_msg = can_add_channel(org_id=str(org_id))
        if not can_add:
            logger.warning(f"[OAUTH_CALLBACK] ⚠️  Channel limit reached: {error_msg}")
            return RedirectResponse(f"{FRONTEND_FAIL}?error={urllib.parse.quote(error_msg or 'channel_limit_reached')}")
        
        logger.info("[OAUTH_CALLBACK] Saving channel and token...")
        await _save_channel_and_token(ch, refresh_token or "", org_id=str(org_id))
        logger.info("[OAUTH_CALLBACK] ✅ Save completed successfully")
        
        # Set session cookie for local dev
        import secrets
        session_token = secrets.token_urlsafe(32)
        response = RedirectResponse(url=f"{FRONTEND_OK}?new=1&channel={urllib.parse.quote(ch['title'])}&id={ch['youtube_channel_id']}&next={urllib.parse.quote(next_path)}")
        
        # Cookie settings for local dev (SameSite=Lax, Secure=False, no Domain)
        cookie_domain = os.getenv("SESSION_COOKIE_DOMAIN", "").strip()
        cookie_samesite = os.getenv("SESSION_COOKIE_SAMESITE", "Lax").strip()
        cookie_secure = os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"
        
        response.set_cookie(
            key=SESSION_COOKIE,
            value=session_token,
            httponly=True,
            samesite=cookie_samesite.lower(),
            secure=cookie_secure,
            domain=cookie_domain if cookie_domain else None,
            max_age=86400 * 30  # 30 days
        )
        
        logger.info(f"[OAUTH_CALLBACK] Session cookie set, redirecting to: {FRONTEND_OK}?new=1")
        return response
    except HTTPException as e:
        logger.error(f"[OAUTH_CALLBACK] ❌ HTTPException: {e.detail}")
        return RedirectResponse(f"{FRONTEND_FAIL}?error={urllib.parse.quote(str(e.detail))}")
    except Exception as e:
        logger.error(f"[OAUTH_CALLBACK] ❌ Exception: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"[OAUTH_CALLBACK] Traceback:\n{traceback.format_exc()}")
        return RedirectResponse(f"{FRONTEND_FAIL}?error={urllib.parse.quote(str(e))}")
