from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.api.deps import get_current_user_org, get_supabase_client, get_current_user
import json
import uuid
import re

router = APIRouter(prefix="/api/v1/comments", tags=["comments"])

class AddCommentRequest(BaseModel):
    task_id: str
    comment: str
    mentions: Optional[List[str]] = None

class CommentResponse(BaseModel):
    id: str
    task_id: str
    user_id: str
    comment: str
    mentions: List[str]
    created_at: str

class CommentListResponse(BaseModel):
    comments: List[CommentResponse]

def extract_mentions(text: str) -> List[str]:
    """Extract @username mentions from comment text."""
    matches = re.findall(r'@(\w+)', text)
    return list(set(matches))  # Unique mentions

@router.post("/add", response_model=CommentResponse)
def add_comment(
    payload: AddCommentRequest,
    client=Depends(get_supabase_client),
    user=Depends(get_current_user),
    org=Depends(get_current_user_org)
):
    """Add a comment with mentions. Creates notifications for mentioned users."""
    user_id = user.get("id") or user.get("user_id", "mock-user")
    org_id = org.get("org_id")
    
    # Extract mentions from comment text if not provided
    mentions = payload.mentions or extract_mentions(payload.comment)
    
    comment_id = str(uuid.uuid4())
    
    # Insert comment
    comment_data = {
        "id": comment_id,
        "task_id": payload.task_id,
        "user_id": user_id,
        "comment": payload.comment,
        "mentions": mentions,
        "is_deleted": False
    }
    
    try:
        comment_r = client.post("/task_comments", content=json.dumps(comment_data))
        if comment_r.status_code not in (200, 201):
            raise HTTPException(status_code=500, detail=f"Failed to create comment: {comment_r.status_code}")
        
        # Create notifications for mentioned users
        if mentions:
            from datetime import datetime, timezone
            for mention in mentions:
                # Find user by username/email (simplified - in prod, use user lookup)
                # For now, create notification with mention as identifier
                notification_data = {
                    "org_id": org_id,
                    "user_id": mention,  # In prod, resolve to actual user_id
                    "event": "mention",
                    "payload": {
                        "task_id": payload.task_id,
                        "comment_id": comment_id,
                        "mentioned_by": user_id,
                        "mention_text": mention
                    },
                    "is_read": False
                }
                try:
                    client.post("/notifications", content=json.dumps(notification_data))
                except:
                    pass  # Continue if notification fails
        
        # Fetch created comment to return
        fetch_r = client.get(f"/task_comments?id=eq.{comment_id}")
        if fetch_r.status_code == 200:
            comments = fetch_r.json()
            if comments:
                c = comments[0]
                return CommentResponse(
                    id=c["id"],
                    task_id=c["task_id"],
                    user_id=c["user_id"],
                    comment=c["comment"],
                    mentions=c.get("mentions", []),
                    created_at=c.get("created_at", "")
                )
        
        # Fallback
        return CommentResponse(
            id=comment_id,
            task_id=payload.task_id,
            user_id=user_id,
            comment=payload.comment,
            mentions=mentions,
            created_at=datetime.now(timezone.utc).isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=CommentListResponse)
def list_comments(
    task_id: str,
    client=Depends(get_supabase_client),
    org=Depends(get_current_user_org)
):
    """Fetch comment thread for a task."""
    try:
        comments_r = client.get(f"/task_comments?task_id=eq.{task_id}&is_deleted=eq.false&order=created_at.asc")
        if comments_r.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch comments")
        
        comments = comments_r.json()
        return CommentListResponse(
            comments=[
                CommentResponse(
                    id=c["id"],
                    task_id=c["task_id"],
                    user_id=c["user_id"],
                    comment=c["comment"],
                    mentions=c.get("mentions", []),
                    created_at=c.get("created_at", "")
                )
                for c in comments
            ]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

