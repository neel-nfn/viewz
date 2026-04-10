"""AppSumo tier enforcement utilities."""
import os
from typing import Optional
from app.services import supabase_service

TIER_LIMITS = {
    "tier1": 1,
    "tier2": 5,
    "tier3": 20
}

def get_org_tier(org_id: str) -> str:
    """Get the tier for an org from billing_plans."""
    client = supabase_service._client()
    if not client:
        return "tier1"  # Default
    
    try:
        r = client.get(f"/billing_plans?org_id=eq.{org_id}&active=eq.true&select=tier&limit=1")
        if r.status_code == 200:
            data = r.json()
            if data and len(data) > 0:
                return data[0].get("tier", "tier1")
    except Exception:
        pass
    
    return "tier1"  # Default

def get_channel_limit(org_id: str) -> int:
    """Get the channel limit for an org based on tier."""
    tier = get_org_tier(org_id)
    return TIER_LIMITS.get(tier, 1)

def can_add_channel(org_id: str) -> tuple[bool, Optional[str]]:
    """Check if org can add another channel."""
    client = supabase_service._client()
    if not client:
        return True, None  # Allow in local dev
    
    try:
        limit = get_channel_limit(org_id)
        r = client.get(f"/channels?org_id=eq.{org_id}&status=eq.connected&select=id")
        if r.status_code == 200:
            count = len(r.json())
            if count >= limit:
                return False, f"Channel limit reached ({limit} channels for your tier)"
        return True, None
    except Exception:
        return True, None  # Allow on error

