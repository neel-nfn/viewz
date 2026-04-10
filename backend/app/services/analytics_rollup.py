import statistics
from datetime import date, timedelta
from typing import Optional, Dict, Any, List
from app.services import supabase_service

def _client():
    if not (supabase_service.SUPABASE_URL and supabase_service.SUPABASE_SERVICE_KEY):
        return None
    return supabase_service._client()

def compute_rollups(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute v2 fields (views_7d, ctr_7d, velocity, variance) from snapshot rows."""
    if not rows:
        return {
            "views_7d": 0,
            "views_28d": 0,
            "ctr_7d": 0.0,
            "ctr_28d": 0.0,
            "views_velocity_7d": 0.0,
            "views_velocity_28d": 0.0,
            "ctr_delta_7d": 0.0,
            "ctr_delta_28d": 0.0,
            "variance_7d": 0.0
        }
    
    s7 = rows[:7]
    s28 = rows[:28] if len(rows) >= 28 else rows
    
    def sumv(xs): 
        return sum(x or 0 for x in xs)
    
    views_7d = sumv([r.get("views", 0) or 0 for r in s7])
    views_28d = sumv([r.get("views", 0) or 0 for r in s28])
    
    ctrs_7d = [float(r.get("ctr", 0) or 0) for r in s7 if r.get("ctr") is not None]
    ctrs_28d = [float(r.get("ctr", 0) or 0) for r in s28 if r.get("ctr") is not None]
    
    ctr_7d = sum(ctrs_7d) / max(1, len(ctrs_7d)) if ctrs_7d else 0.0
    ctr_28d = sum(ctrs_28d) / max(1, len(ctrs_28d)) if ctrs_28d else 0.0
    
    variance_7d = statistics.pvariance(ctrs_7d) if len(ctrs_7d) > 1 else 0.0
    
    latest = rows[0]
    latest_views = latest.get("views", 0) or 0
    latest_ctr = float(latest.get("ctr", 0) or 0)
    
    vv7 = 0.0
    if views_7d > 0:
        vv7 = (latest_views - views_7d) / views_7d
    
    vv28 = 0.0
    if views_28d > 0:
        vv28 = (latest_views - views_28d) / views_28d
    
    return {
        "views_7d": views_7d,
        "views_28d": views_28d,
        "ctr_7d": round(ctr_7d, 3),
        "ctr_28d": round(ctr_28d, 3),
        "views_velocity_7d": round(vv7, 4),
        "views_velocity_28d": round(vv28, 4),
        "ctr_delta_7d": round(latest_ctr - ctr_7d, 4),
        "ctr_delta_28d": round(latest_ctr - ctr_28d, 4),
        "variance_7d": round(variance_7d, 6)
    }

def rollup_channel_analytics(channel_id: str) -> Optional[bool]:
    """Update analytics_snapshots v2 fields for a channel."""
    c = _client()
    if not c:
        return None
    
    # Fetch all snapshots for this channel, ordered by date desc
    r = c.get(f"/analytics_snapshots?channel_id=eq.{channel_id}&order=date.desc&limit=30")
    if r.status_code != 200:
        return None
    
    rows = r.json()
    if not rows:
        return True  # No data to rollup
    
    # Group by date and compute rollups for latest snapshot
    rollups = compute_rollups(rows)
    
    # Update the latest snapshot with v2 fields
    latest_id = rows[0].get("id")
    if not latest_id:
        return True
    
    import json
    upd = c.patch(
        f"/analytics_snapshots?id=eq.{latest_id}",
        content=json.dumps(rollups)
    )
    
    return upd.status_code in (200, 204)

def rollup_all_channels() -> int:
    """Rollup analytics v2 fields for all channels."""
    c = _client()
    if not c:
        return 0
    
    # Get all channel IDs
    r = c.get("/channels?select=id")
    if r.status_code != 200:
        return 0
    
    channels = r.json()
    count = 0
    for ch in channels:
        channel_id = ch.get("id")
        if channel_id and rollup_channel_analytics(channel_id):
            count += 1
    
    return count

