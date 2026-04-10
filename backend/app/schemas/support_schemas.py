from pydantic import BaseModel, EmailStr
from typing import Optional

class SupportTicketRequest(BaseModel):
    email: EmailStr
    subject: str
    body: str

class SupportTicketResponse(BaseModel):
    ticket_id: str
    status: str = "open"

