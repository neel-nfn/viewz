import httpx
import os
import uuid
import time
import json
from typing import Tuple
from app.services import supabase_service

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

def build_prompt(topic: str, persona: str) -> str:
    return f"""Persona: {persona}
Task: Write SEO-optimized metadata for a YouTube video about: '{topic}'

Requirements:
- Title: Maximum 60 characters, engaging and keyword-rich
- Description: Maximum 150 characters, includes call-to-action
- Tags: 10 relevant tags separated by commas

Avoid clickbait or misleading claims. Focus on value and accuracy.

Output as JSON with this exact format:
{{"title": "...", "description": "...", "tags": ["tag1", "tag2", ...]}}
"""

async def call_gemini(prompt: str, temperature: float = 0.7) -> str:
    """Call Gemini API asynchronously."""
    if not GEMINI_API_KEY:
        # Mock response for local dev
        return json.dumps({
            "title": "Sample SEO Title",
            "description": "Sample description for the video topic.",
            "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
        })
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            res = await client.post(
                f"{GEMINI_URL}?key={GEMINI_API_KEY}",
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": temperature}
                },
            )
            data = res.json()
            text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            return text
    except Exception as e:
        # Fallback mock
        return json.dumps({
            "title": f"SEO Title for {prompt[:20]}...",
            "description": "AI-generated description.",
            "tags": ["seo", "youtube", "optimization"]
        })

async def generate_seo(
    org_id: str,
    task_id: str,
    topic: str,
    persona: str,
    temperature: float,
    user_id: str
) -> Tuple[str, float, float]:
    """Generate SEO metadata and log to ai_tasks table."""
    prompt = build_prompt(topic, persona)
    
    t0 = time.time()
    output = await call_gemini(prompt, temperature)
    dt = time.time() - t0
    
    # Calculate cost: approximate $0.0005 per 1K tokens (input + output)
    prompt_tokens = len(prompt) // 4  # Rough token estimate
    output_tokens = len(output) // 4
    total_tokens = prompt_tokens + output_tokens
    cost = round(total_tokens / 1000 * 0.0005, 4)
    
    # Insert into ai_tasks
    client = supabase_service._client()
    if client:
        try:
            import json as json_module
            task_data = {
                "id": str(uuid.uuid4()),
                "org_id": org_id,
                "task_id": task_id,
                "persona": persona,
                "mode": "seo",
                "prompt_text": prompt,
                "output_text": output,
                "model_used": "gemini-pro",
                "temperature": temperature,
                "cost": cost,
                "created_by": user_id
            }
            client.post("/ai_tasks", content=json_module.dumps(task_data))
        except Exception:
            pass  # Continue if logging fails
    
    return output, cost, dt

