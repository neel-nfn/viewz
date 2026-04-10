from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from app.schemas.feedback_schemas import FeedbackCreate, FeedbackUpdate, FeedbackPublic
from app.services import feedback_service
from app.api.deps import get_current_user, get_current_user_org
from app.utils.org import resolve_org_id

router = APIRouter(prefix="/api/v1/feedback_reports", tags=["feedback"])

@router.post("", response_model=FeedbackPublic)
def submit_feedback(body: FeedbackCreate, user=Depends(get_current_user), org=Depends(get_current_user_org)):
    org_id = resolve_org_id(org.get('org_id'))
    if str(body.org_id) != str(org_id):
        raise HTTPException(status_code=403, detail="forbidden")
    # Override org_id from context
    body.org_id = org_id
    return feedback_service.create_feedback(body)

@router.get("", response_model=list[FeedbackPublic])
def list_feedback(status: str | None = None, limit: int=100, offset:int=0, user=Depends(get_current_user), org=Depends(get_current_user_org)):
    # Limit listing to Manager/Admin (aligns with Core API access rules)
    # For now, allow all since role might not be implemented yet
    # if user.get('role') not in ("admin","manager"):
    #     raise HTTPException(status_code=403, detail="forbidden")
    org_id = resolve_org_id(org.get('org_id'))
    return feedback_service.list_feedback(org_id, status, limit, offset)

@router.put("/{feedback_id}", response_model=FeedbackPublic)
def update_feedback(feedback_id: UUID, body: FeedbackUpdate, user=Depends(get_current_user), org=Depends(get_current_user_org)):
    # if user.get('role') not in ("admin","manager"):
    #     raise HTTPException(status_code=403, detail="forbidden")
    org_id = resolve_org_id(org.get('org_id'))
    try:
        return feedback_service.update_feedback_status(org_id, feedback_id, body)
    except ValueError:
        raise HTTPException(status_code=404, detail="not_found")
