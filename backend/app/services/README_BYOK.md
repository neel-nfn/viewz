# BYOK (Bring Your Own Key) Usage

This service supports storing and retrieving encrypted Gemini API keys per organization.

## Runtime Usage Example

Update your Gemini API call sites to use BYOK keys:

```python
from app.services.integration_service import load_ai_key_for_org
from app.utils.org import resolve_org_id
import os

# In your service function (e.g., seo_service.py, ai_service.py):
async def call_gemini(prompt: str, org_id: UUID, temperature: float = 0.7) -> str:
    # Try to load org-specific BYOK first
    key = load_ai_key_for_org(org_id, "gemini")
    
    # Fallback to system key if BYOK not configured
    if not key:
        key = os.getenv("GEMINI_API_KEY")
    
    if not key:
        raise RuntimeError("No Gemini API key configured for org or system")
    
    # Use the key to make API call
    async with httpx.AsyncClient(timeout=60.0) as client:
        res = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={key}",
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": temperature}
            },
        )
        # ... handle response
```

## Metrics (Optional)

Add Prometheus counters in your AI call sites:

```python
from prometheus_client import Counter

BYOK_REQUESTS = Counter("ai_byok_requests_total", "Total BYOK requests")
BYOK_MISSING = Counter("ai_byok_missing_total", "BYOK missing, using fallback")
BYOK_FAILURES = Counter("ai_byok_failures_total", "BYOK decryption failures")

# In your call function:
if key:
    BYOK_REQUESTS.inc()
else:
    BYOK_MISSING.inc()
```

