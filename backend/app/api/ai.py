from fastapi import APIRouter, Depends, HTTPException
from app.schemas.ai_schemas import AIGenerateRequest, AIGenerateResponse, AIHistoryResponse, SEOTaskRequest, SEOTaskResponse
from app.services.ai_service import AIService
from app.services.seo_service import generate_seo
from app.api.deps import get_supabase_client, get_current_user, get_current_user_org
from app.dependencies import require_session
from app.utils.ratelimit import ai_under_limit_org
import json

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])

def get_current_org_id():
    return "org-demo"

def get_active_channel_id():
    return "chan-demo"

@router.post("/generate", response_model=AIGenerateResponse)
def ai_generate(body: AIGenerateRequest, org_id: str = Depends(get_current_org_id), user=Depends(require_session)):
    if not ai_under_limit_org(org_id, user.id, user.role):
        raise HTTPException(status_code=429, detail="AI generation limit exceeded for today")
    channel_id = body.channel_id or "chan-demo"
    svc = AIService()
    res = svc.generate(org_id, channel_id, user.id, body)
    return res

@router.get("/history/{task_id}", response_model=AIHistoryResponse)
def ai_history(task_id: str, org_id: str = Depends(get_current_org_id)):
    svc = AIService()
    items = svc.history(org_id, task_id)
    return {"items": items}

@router.post("/seo", response_model=SEOTaskResponse)
async def seo_generate(
    payload: SEOTaskRequest,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org)
):
    """Generate SEO metadata (title, description, tags) using Gemini API."""
    user_id = user.get("id") or user.get("user_id", "mock-user")
    org_id = org.get("org_id") or payload.org_id
    
    try:
        raw, cost, _ = await generate_seo(
            org_id=org_id,
            task_id=payload.task_id,
            topic=payload.topic,
            persona=payload.persona,
            temperature=payload.temperature,
            user_id=user_id
        )
        
        # Parse JSON response
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = {"title": "", "description": "", "tags": []}
        
        # Calculate score based on quality
        score = 80.0
        title = data.get("title", "")
        description = data.get("description", "")
        tags = data.get("tags", [])
        
        if len(title) > 0 and len(title) <= 60:
            score += 5
        if len(description) > 0 and len(description) <= 150:
            score += 5
        if len(tags) >= 5:
            score += min(10, len(tags) - 5)
        
        score = min(100, max(0, score))
        
        return SEOTaskResponse(
            title=title,
            description=description,
            tags=tags if isinstance(tags, list) else (tags.split(",") if isinstance(tags, str) else []),
            score=round(score, 2)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/usage")
def ai_usage(org=Depends(get_current_user_org)):
    """Get AI usage/cost for current month."""
    from datetime import datetime, timezone
    from app.services import supabase_service
    
    org_id = org.get("org_id")
    if not org_id:
        return {"month": datetime.now(timezone.utc).strftime("%Y-%m"), "total_cost": 0.0}
    
    client = supabase_service._client()
    if not client:
        return {"month": datetime.now(timezone.utc).strftime("%Y-%m"), "total_cost": 0.0}
    
    # Get current month's total cost
    try:
        current_month = datetime.now(timezone.utc).strftime("%Y-%m")
        r = client.get(f"/ai_tasks?org_id=eq.{org_id}&select=cost")
        if r.status_code == 200:
            tasks = r.json()
            total_cost = sum(float(t.get("cost", 0) or 0) for t in tasks)
            return {"month": current_month, "total_cost": round(total_cost, 4)}
    except Exception:
        pass
    
    return {"month": datetime.now(timezone.utc).strftime("%Y-%m"), "total_cost": 0.0}

