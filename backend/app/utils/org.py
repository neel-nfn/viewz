
import os
from uuid import UUID

def resolve_org_id(raw) -> UUID:
    try:
        return UUID(str(raw))
    except Exception:
        fallback = os.getenv("ORG_ID", "00000000-0000-0000-0000-000000000000")
        return UUID(fallback)
