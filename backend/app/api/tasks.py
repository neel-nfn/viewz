from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_user, get_current_user_org, get_supabase_client
from app.utils.org import resolve_org_id
from typing import Optional

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])

@router.get("/today")
def tasks_today(user=Depends(get_current_user), org=Depends(get_current_user_org)):
    """Disabled until a real task model exists."""
    raise HTTPException(status_code=501, detail="Tasks endpoint disabled until real task tables are implemented.")

@router.get("/{task_id}")
def get_task(
    task_id: str,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
    client=Depends(get_supabase_client)
):
    """Get task details including guidebook data (stage_checklist, tool_links, asset_folder_url)."""
    org_id = resolve_org_id(org.get('org_id'))
    
    try:
        # Query task from Supabase using REST API
        task_r = client.get(f"/tasks?id=eq.{task_id}&org_id=eq.{org_id}")
        if task_r.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch task")
        
        tasks = task_r.json()
        if not tasks or len(tasks) == 0:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task = tasks[0]
        
        # Get related data (comments, attachments)
        comments_r = client.get(f"/task_comments?task_id=eq.{task_id}&is_deleted=eq.false&order=created_at.asc")
        attachments_r = client.get(f"/attachments?task_id=eq.{task_id}&order=created_at.desc")
        
        comments = comments_r.json() if comments_r.status_code == 200 else []
        attachments = attachments_r.json() if attachments_r.status_code == 200 else []
        
        # Format activity from comments
        activity = []
        for comment in comments:
            activity.append({
                "id": comment.get("id"),
                "action": "comment",
                "timestamp": comment.get("created_at"),
                "user_id": comment.get("user_id")
            })
        
        return {
            "task": task,
            "title": task.get("title"),
            "status": task.get("status"),
            "research_idea_id": task.get("research_idea_id"),
            "stage_checklist": task.get("stage_checklist") or [],
            "tool_links": task.get("tool_links") or [],
            "asset_folder_url": task.get("asset_folder_url"),
            "comments": comments,
            "attachments": attachments,
            "activity": activity
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch task: {str(e)}")
