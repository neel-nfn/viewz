import os
import asyncio
import contextlib
from typing import Set, Optional
from datetime import datetime, timezone
from app.services.usage_rollup import rollup_org
from app.services.analytics_rollup import rollup_all_channels
from app.services import supabase_service

INTERVAL_MIN = int(os.getenv("ROLLUP_INTERVAL_MIN", "15"))
ENABLED = os.getenv("ROLLUP_SCHED_ENABLED", "0") == "1"

_last_run_iso: Optional[str] = None

def _client():
    if not (supabase_service.SUPABASE_URL and supabase_service.SUPABASE_SERVICE_KEY):
        return None
    return supabase_service._client()

def _org_ids() -> Set[str]:
    c = _client()
    if not c:
        return set()
    r = c.get("/channels?select=org_id&distinct=org_id")
    if r.status_code != 200:
        return set()
    return {row["org_id"] for row in r.json() if row.get("org_id")}

async def _loop():
    global _last_run_iso
    try:
        while True:
            # Rollup AI usage per org
            for org_id in list(_org_ids()):
                with contextlib.suppress(Exception):
                    rollup_org(org_id)
            # Rollup analytics v2 fields for all channels
            with contextlib.suppress(Exception):
                rollup_all_channels()
            _last_run_iso = datetime.now(timezone.utc).isoformat()
            await asyncio.sleep(INTERVAL_MIN * 60)
    except asyncio.CancelledError:
        return

_task = None

def start():
    global _task
    if ENABLED and _task is None:
        _task = asyncio.create_task(_loop())

def stop():
    global _task
    if _task:
        _task.cancel()
        _task = None

def last_run_iso() -> Optional[str]:
    return _last_run_iso

