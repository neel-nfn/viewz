from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.api.deps import get_current_user_org
from app.services import supabase_service

router = APIRouter(prefix="/api/v1/billing", tags=["billing"])

class UsageResponse(BaseModel):
    credits_total: int
    credits_used: int
    credits_remaining: int

class PlanLimitResponse(BaseModel):
    ai_credit_limit: int

@router.get("/usage", response_model=UsageResponse)
def usage(org=Depends(get_current_user_org)):
    return UsageResponse(credits_total=10000, credits_used=1234, credits_remaining=8766)

@router.get("/plan_limit", response_model=PlanLimitResponse)
def get_plan_limit(org=Depends(get_current_user_org)):
    if supabase_service.SUPABASE_URL and supabase_service.SUPABASE_SERVICE_KEY:
        c = supabase_service._client()
        if c:
            try:
                r = c.get(f"/billing_plans?org_id=eq.{org['org_id']}&active=eq.true&select=ai_credit_limit&limit=1")
                if r.status_code == 200:
                    data = r.json()
                    if data and len(data) > 0:
                        limit = data[0].get("ai_credit_limit", 100)
                        return PlanLimitResponse(ai_credit_limit=int(limit))
            except Exception:
                # Fall back to default if query fails (billing disabled / local dev)
                pass
    # Default: return free tier limit
    return PlanLimitResponse(ai_credit_limit=100)

@router.post("/rollup_ai_usage")
def rollup_ai_usage(org=Depends(get_current_user_org)):
    """Manual trigger for AI usage rollup."""
    from app.services.usage_rollup import rollup_org
    rollup_org(org['org_id'])
    return {"ok": True}

