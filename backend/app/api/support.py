from fastapi import APIRouter, Depends, HTTPException
from app.schemas.support_schemas import SupportTicketRequest, SupportTicketResponse
from app.api.deps import get_supabase_client, get_current_user_org
import json
import uuid
from datetime import datetime, timezone

router = APIRouter(prefix="/api/v1/support", tags=["support"])

@router.post("/ticket", response_model=SupportTicketResponse)
def create_ticket(
    payload: SupportTicketRequest,
    client=Depends(get_supabase_client),
    org=Depends(get_current_user_org)
):
    """Create a support ticket."""
    org_id = org.get("org_id", "00000000-0000-0000-0000-000000000001")
    ticket_id = str(uuid.uuid4())
    
    ticket_data = {
        "id": ticket_id,
        "org_id": org_id,
        "email": payload.email,
        "subject": payload.subject,
        "body": payload.body,
        "status": "open"
    }
    
    try:
        r = client.post("/support_tickets", content=json.dumps(ticket_data))
        if r.status_code not in (200, 201):
            raise HTTPException(status_code=500, detail="Failed to create ticket")
        
        return SupportTicketResponse(ticket_id=ticket_id, status="open")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

