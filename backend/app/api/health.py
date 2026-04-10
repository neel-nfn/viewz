import os
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.scheduler import ENABLED as SCHED_ENABLED
from app.services.scheduler import last_run_iso as SCHED_LAST
from app.services import supabase_service

router = APIRouter(prefix="/api/v1", tags=["health"])

class Health(BaseModel):
    ok: bool
    oauth_client: bool
    sched_enabled: bool
    sched_last_run: str | None
    stripe_webhook_secret: bool
    supabase_configured: bool

@router.get("/health", response_model=Health)
def health():
    return Health(
        ok=True,
        oauth_client=bool(os.getenv("GOOGLE_CLIENT_ID") and os.getenv("GOOGLE_CLIENT_SECRET")),
        sched_enabled=bool(SCHED_ENABLED),
        sched_last_run=SCHED_LAST(),
        stripe_webhook_secret=bool(os.getenv("STRIPE_WEBHOOK_SECRET")),
        supabase_configured=bool(supabase_service.SUPABASE_URL and supabase_service.SUPABASE_SERVICE_KEY),
    )
