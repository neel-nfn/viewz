from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.api.deps import get_current_user_org, get_supabase_client, get_current_user
import json
import uuid

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])

class CreateTaskFromIdeaRequest(BaseModel):
    research_idea_id: str
    channel_id: str
    title: Optional[str] = None
    stage: str = "research"  # Default to research stage

class TaskResponse(BaseModel):
    id: str
    title: str
    status: str
    research_idea_id: Optional[str] = None

@router.post("/from-idea", response_model=TaskResponse)
def create_task_from_idea(
    payload: CreateTaskFromIdeaRequest,
    client=Depends(get_supabase_client),
    user=Depends(get_current_user),
    org=Depends(get_current_user_org)
):
    """Create a task directly from a research idea."""
    user_id = user.get("id") or user.get("user_id", "mock-user")
    org_id = org.get("org_id")
    
    # Fetch the research idea to get title and validate org
    try:
        idea_r = client.get(f"/research_ideas?id=eq.{payload.research_idea_id}&select=id,title,org_id,channel_id")
        if idea_r.status_code != 200:
            raise HTTPException(status_code=404, detail="Research idea not found")
        
        ideas = idea_r.json()
        if not ideas:
            raise HTTPException(status_code=404, detail="Research idea not found")
        
        idea = ideas[0]
        
        # Verify org ownership
        if idea.get("org_id") != org_id:
            raise HTTPException(status_code=403, detail="Idea does not belong to your org")
        
        # Create task
        task_id = str(uuid.uuid4())
        task_title = payload.title or idea.get("title", "New Task")
        
        task_data = {
            "id": task_id,
            "org_id": org_id,
            "channel_id": payload.channel_id,
            "title": task_title,
            "status": payload.stage,
            "research_idea_id": payload.research_idea_id,
            "assigned_to": user_id,
            "created_by": user_id
        }
        
        # Insert task (assuming tasks table exists)
        task_r = client.post("/tasks", content=json.dumps(task_data))
        if task_r.status_code not in (200, 201):
            raise HTTPException(status_code=500, detail=f"Failed to create task: {task_r.status_code}")
        
        return TaskResponse(
            id=task_id,
            title=task_title,
            status=payload.stage,
            research_idea_id=payload.research_idea_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

