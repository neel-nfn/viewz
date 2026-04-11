from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.utils.env import require_local
import os

router = APIRouter(prefix="/api/v1", tags=["env"])

@router.get("/env")
async def env_echo(user=Depends(get_current_user)):
    """Echo environment info for UI debugging - LOCAL ONLY. Requires authentication."""
    require_local()
    return {
        "env": os.getenv("ENVIRONMENT", "local"),
        "service": "viewz-backend",
        "api_base": "/api/v1",
        "debug": os.getenv("DEBUG", "false").lower() == "true"
    }

