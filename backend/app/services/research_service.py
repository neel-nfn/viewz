import math, uuid, json
from typing import Dict, Tuple
import httpx

def _safe_div(a: float, b: float) -> float:
    return a / b if b not in (0, None) else 0.0

def compute_outlier_components(snap: Dict) -> Dict[str, float]:
    views_vel = float(snap.get("views_velocity_7d", 0))
    ctr_delta = float(snap.get("ctr_delta_7d", 0))
    variance = float(snap.get("variance_7d", 0))
    ctr = float(snap.get("ctr", snap.get("ctr_7d", 0)))
    ctr_z = _safe_div(ctr_delta, math.sqrt(variance) if variance > 0 else 1.0)
    freshness = 1.0  # placeholder until recency is wired
    # Normalize to 0..1 bands
    views_vel_n = max(0.0, min(1.0, (views_vel + 1.0) / 2.0))
    ctr_z_n = max(0.0, min(1.0, (ctr_z + 3.0) / 6.0))
    freshness_n = max(0.0, min(1.0, freshness))
    return {
        "views_velocity": views_vel_n,
        "ctr_z": ctr_z_n,
        "freshness": freshness_n
    }

def score_from_components(components: Dict[str, float]) -> float:
    w = {"views_velocity": 0.5, "ctr_z": 0.35, "freshness": 0.15}
    s = sum(components[k] * w[k] for k in w)
    return round(s * 100.0, 2)

def score_idea(client: httpx.Client, org_id: str, channel_id: str, title: str, url: str | None, user_id: str) -> Tuple[str, float, Dict[str, float]]:
    # pick latest snapshot for the channel
    try:
        r = client.get(f"/analytics_snapshots?channel_id=eq.{channel_id}&order=date.desc&limit=1")
        if r.status_code == 200:
            snaps = r.json()
            snap = snaps[0] if snaps else {}
        else:
            snap = {}
    except Exception as e:
        snap = {}
    
    components = compute_outlier_components(snap)
    score = score_from_components(components)
    idea_id = str(uuid.uuid4())
    idea = {
        "id": idea_id,
        "org_id": org_id,
        "channel_id": channel_id,
        "source": "manual",
        "title": title,
        "url": url,
        "metadata": {},
        "created_by": user_id
    }
    
    # Insert idea
    r_idea = client.post("/research_ideas", content=json.dumps(idea))
    if r_idea.status_code not in (200, 201):
        raise RuntimeError(f"Failed to insert research_idea: {r_idea.status_code}")
    
    # Insert score
    r_score = client.post("/research_scores", content=json.dumps({
        "org_id": org_id,
        "channel_id": channel_id,
        "idea_id": idea_id,
        "score": score,
        "components": components,
        "created_by": user_id
    }))
    if r_score.status_code not in (200, 201):
        raise RuntimeError(f"Failed to insert research_score: {r_score.status_code}")
    
    return idea_id, score, components

