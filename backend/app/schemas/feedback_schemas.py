from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict
from datetime import datetime
from uuid import UUID

Category = Literal["bug","idea","ui","performance","other"]
Severity = Literal["low","medium","high","critical"]
Status = Literal["open","triaged","resolved","rejected"]

class FeedbackCreate(BaseModel):
    org_id: UUID
    user_id: Optional[UUID] = None
    channel_id: Optional[UUID] = None
    url: Optional[str] = None
    category: Category = "other"
    severity: Severity = "low"
    title: str
    description: Optional[str] = None
    metadata: Optional[Dict] = None

class FeedbackUpdate(BaseModel):
    status: Status

class FeedbackPublic(BaseModel):
    id: UUID
    org_id: UUID
    user_id: Optional[UUID]
    channel_id: Optional[UUID]
    url: Optional[str]
    category: Category
    severity: Severity
    title: str
    description: Optional[str]
    metadata: Dict
    status: Status
    created_at: datetime
    updated_at: datetime
