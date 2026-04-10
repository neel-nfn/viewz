from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
import os
try:
    from .api import pipeline as pipeline_api
except Exception:
    pipeline_api = None
try:
    from .api import attachments as attachments_api
except Exception:
    attachments_api = None

try:
    from .api import comments as comments_api
except Exception:
    comments_api = None

try:
    from .api import notifications as notifications_api
except Exception:
    notifications_api = None

try:
    from .api import support as support_api
except Exception:
    support_api = None


from app.api import auth_login_fixed

from .middleware import add_middleware, metrics_endpoint
from .services import scheduler

from .api import health
from .api import team
from .api import analytics as analytics_api
from .api import ai as ai_api
from .api import voice as voice_api
from .api import optimize, abtest, org, billing
from .api import auth_google
from .api import channels
from .api import stripe_webhook
from .api import research as research_api
from .api import scripts as scripts_api
from .api import instructions as instructions_api
from .api import operator as operator_api
from .api import worker as worker_api
from .api import storage as storage_api
from .api import filename as filename_api
from .api import assets as assets_api
from .api import links as links_api
from .api import lines as lines_api
from .api import feedback as feedback_api
from .api import integrations as integrations_api
from .api import competitors as competitors_api
from .api import workflow as workflow_api
from .api import env_echo

from .routes import auth

app = FastAPI(title="Viewz API", version="0.0.1")

@app.get("/")
async def root():
    """Root endpoint - API is available at /api/v1/..."""
    return {
        "name": "Viewz API",
        "version": "0.0.1",
        "docs": "/docs",
        "health": "/health",
        "api": "/api/v1"
    }

@app.get("/health")
async def health_check():
    return {"ok": True}

@app.get("/metrics")
def metrics():
    return metrics_endpoint()

add_middleware(app)

app.include_router(auth_login_fixed.router)

if health and hasattr(health, 'router'):
    app.include_router(health.router)

# Register auth_google BEFORE auth to ensure OAuth callback takes precedence
if auth_google and hasattr(auth_google, 'router'):
    app.include_router(auth_google.router)
if auth and hasattr(auth, 'router'):
    app.include_router(auth.router)
if team and hasattr(team, 'router'):
    app.include_router(team.router)
if analytics_api and hasattr(analytics_api, 'router'):
    app.include_router(analytics_api.router)
if ai_api and hasattr(ai_api, 'router'):
    app.include_router(ai_api.router)
if voice_api and hasattr(voice_api, 'router'):
    app.include_router(voice_api.router)
if optimize and hasattr(optimize, 'router'):
    app.include_router(optimize.router)
if abtest and hasattr(abtest, 'router'):
    app.include_router(abtest.router)
if org and hasattr(org, 'router'):
    app.include_router(org.router)
if billing and hasattr(billing, 'router'):
    app.include_router(billing.router)
if channels and hasattr(channels, 'router'):
    app.include_router(channels.router)
if stripe_webhook and hasattr(stripe_webhook, 'router'):
    app.include_router(stripe_webhook.router)
if research_api and hasattr(research_api, 'router'):
    app.include_router(research_api.router)
if scripts_api and hasattr(scripts_api, 'router'):
    app.include_router(scripts_api.router)
if instructions_api and hasattr(instructions_api, 'router'):
    app.include_router(instructions_api.router)
if operator_api and hasattr(operator_api, 'router'):
    app.include_router(operator_api.router)
if worker_api and hasattr(worker_api, 'router'):
    app.include_router(worker_api.router)
if storage_api and hasattr(storage_api, 'router'):
    app.include_router(storage_api.router)
if filename_api and hasattr(filename_api, 'router'):
    app.include_router(filename_api.router)
if assets_api and hasattr(assets_api, 'router'):
    app.include_router(assets_api.router)
if links_api and hasattr(links_api, 'router'):
    app.include_router(links_api.router)
if lines_api and hasattr(lines_api, 'router'):
    app.include_router(lines_api.router)
if pipeline_api and hasattr(pipeline_api, 'router'):
    app.include_router(pipeline_api.router)
if comments_api and hasattr(comments_api, 'router'):
    app.include_router(comments_api.router)
if attachments_api and hasattr(attachments_api, 'router'):
    app.include_router(attachments_api.router)
if notifications_api and hasattr(notifications_api, 'router'):
    app.include_router(notifications_api.router)
if support_api and hasattr(support_api, 'router'):
    app.include_router(support_api.router)
if feedback_api and hasattr(feedback_api, 'router'):
    app.include_router(feedback_api.router)
if integrations_api and hasattr(integrations_api, 'router'):
    app.include_router(integrations_api.router)
if competitors_api and hasattr(competitors_api, 'router'):
    app.include_router(competitors_api.router)
if workflow_api and hasattr(workflow_api, 'router'):
    app.include_router(workflow_api.router)
if env_echo and hasattr(env_echo, 'router'):
    app.include_router(env_echo.router)

@app.on_event("startup")
async def _start_scheduler():
    scheduler.start()

@app.on_event("shutdown")
async def _stop_scheduler():
    scheduler.stop()

# Debug endpoints - only available in local/dev environment
from fastapi import APIRouter, HTTPException
from app.utils.env import require_local

debug_router = APIRouter()

@debug_router.get("/api/v1/debug/jwt")
def debug_jwt(token: str = None):
    """Debug endpoint for JWT secret verification - LOCAL ONLY"""
    require_local()
    
    import os, base64, jwt
    
    raw = os.getenv("SUPABASE_JWT_SECRET", "")
    
    result = {
        "raw_len": len(raw),
        "used_decoded": False,
        "error": None,
        "algorithm": "HS256",
    }
    
    try:
        decoded = base64.b64decode(raw)
        if decoded:
            result["used_decoded"] = True
            secret = decoded
        else:
            secret = raw.encode()
    except Exception:
        secret = raw.encode()
    
    if token:
        for algo in ["HS256", "RS256"]:
            try:
                payload = jwt.decode(token, secret, algorithms=[algo])
                result["algorithm_tried"] = algo
                result["decoded_payload"] = payload
                break
            except Exception as e:
                result[f"error_{algo}"] = str(e)
    
    return result

@app.get("/api/v1/debug/env-check")
def env_check():
    """Debug endpoint for environment variable checking - LOCAL ONLY"""
    require_local()
    
    import os, base64
    info = {}
    
    # Collect .env-related data
    for k in ["SUPABASE_JWT_SECRET", "SUPABASE_URL", "SUPABASE_DB_URL", "DATABASE_URL"]:
        val = os.getenv(k)
        info[k] = {
            "exists": val is not None,
            "len": len(val) if val else 0,
            "start": val[:8] if val else None,
            "end": val[-8:] if val else None,
        }
    
    # Detect if multiple dotenv loads happened
    import inspect
    from dotenv import find_dotenv
    info["dotenv_loaded_from"] = find_dotenv()
    info["cwd"] = os.getcwd()
    try:
        info["env_files_in_dir"] = [f for f in os.listdir() if f.startswith(".env")]
    except Exception:
        info["env_files_in_dir"] = []
    
    # Try decoding base64
    raw = os.getenv("SUPABASE_JWT_SECRET", "")
    try:
        decoded = base64.b64decode(raw)
        info["decoded_secret"] = {
            "len": len(decoded),
            "is_valid_base64": True,
        }
    except Exception:
        info["decoded_secret"] = {"is_valid_base64": False}
    
    return info

@app.get("/api/v1/debug/token-claims")
def debug_token_claims(token: str):
    """
    Decode JWT token without verification (for debugging) - LOCAL ONLY.
    Returns header and payload as JSON.
    """
    require_local()
    
    import base64, json
    
    try:
        header_b64, payload_b64, _ = token.split(".")
        
        def b64url(x): 
            x += "=" * (-len(x) % 4)
            return base64.urlsafe_b64decode(x.encode()).decode()
        
        return {
            "header": json.loads(b64url(header_b64)),
            "payload": json.loads(b64url(payload_b64)),
        }
    except Exception as e:
        return {"error": str(e)}

app.include_router(debug_router)
