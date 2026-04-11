from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CreateWorkflowCardRequest(BaseModel):
    title: str
    description: Optional[str] = None
    meta: Optional[str] = None
    stage: str = "ideas"
    tags: List[str] = []
    topic_idea_id: Optional[str] = None


class UpdateWorkflowCardRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    meta: Optional[str] = None
    stage: Optional[str] = None
    tags: Optional[List[str]] = None
    topic_idea_id: Optional[str] = None
    position: Optional[int] = None


class UpdateWorkflowCardStageRequest(BaseModel):
    stage: str


class WorkflowCardResponse(BaseModel):
    id: str
    org_id: str
    title: str
    description: Optional[str] = None
    meta: Optional[str] = None
    stage: str
    tags: List[str] = []
    topic_idea_id: Optional[str] = None
    position: int
    created_by: str
    created_at: datetime
    updated_at: datetime


class WorkflowCardsListResponse(BaseModel):
    cards: List[WorkflowCardResponse]

