from fastapi import APIRouter
from typing import List, Dict

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])

@router.get("/list")
def list_notifications(unread_only: bool = True) -> List[Dict]:
    return []
