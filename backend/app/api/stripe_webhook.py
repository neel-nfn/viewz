import os
import json
import stripe
from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional
from app.services import supabase_service

router = APIRouter(prefix="/api/v1/stripe/webhook", tags=["stripe"])

SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

def apply_plan_update(org_id: str, ai_credit_limit: int):
    """Update billing plan for an org."""
    c = supabase_service._client()
    if not c:
        return
    
    # Upsert billing plan
    payload = {
        "org_id": org_id,
        "tier": "paid",
        "ai_credit_limit": ai_credit_limit,
        "active": True
    }
    
    try:
        # Try to update existing active plan
        upd = c.patch(f"/billing_plans?org_id=eq.{org_id}&active=eq.true", content=json.dumps(payload))
        if upd.status_code not in (200, 204):
            # If no active plan, insert new one
            ins = c.post("/billing_plans", content=json.dumps(payload))
            if ins.status_code not in (200, 201):
                raise RuntimeError(f"plan_update_failed: {ins.status_code}")
    except Exception:
        pass

@router.post("")
async def webhook(req: Request):
    payload = await req.body()
    sig = req.headers.get('stripe-signature')
    
    if not SECRET:
        # Dev mode: parse without verification
        event = json.loads(payload.decode('utf-8'))
    else:
        try:
            event = stripe.Webhook.construct_event(payload=payload, sig_header=sig, secret=SECRET)
        except Exception as e:
            return {"received": False, "error": str(e)}
    
    t = event.get('type')
    obj = event.get('data', {}).get('object', {})
    
    if t == 'customer.subscription.updated':
        md = obj.get('metadata', {})
        org_id = md.get('org_id')
        limit = md.get('ai_credit_limit')
        if org_id and limit:
            apply_plan_update(org_id, int(limit))
    
    return {"received": True, "type": t}

