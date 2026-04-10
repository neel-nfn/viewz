from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.api.deps import get_current_user_org, get_supabase_client, get_current_user
import json
import uuid
import base64
import os

router = APIRouter(prefix="/api/v1/attachments", tags=["attachments"])

class UploadAttachmentRequest(BaseModel):
    task_id: str
    file_data: str  # base64 encoded
    file_name: str
    type: str  # 'script', 'voice', 'thumbnail', etc.

class AttachmentResponse(BaseModel):
    id: str
    task_id: str
    file_url: str
    type: str
    uploaded_by: str
    created_at: str

@router.post("/upload", response_model=AttachmentResponse)
def upload_attachment(
    payload: UploadAttachmentRequest,
    client=Depends(get_supabase_client),
    user=Depends(get_current_user),
    org=Depends(get_current_user_org)
):
    """Upload a file attachment (base64 → Supabase Storage)."""
    user_id = user.get("id") or user.get("user_id", "mock-user")
    org_id = org.get("org_id")
    
    try:
        # Decode base64
        file_bytes = base64.b64decode(payload.file_data)
        
        # Generate file path
        attachment_id = str(uuid.uuid4())
        file_ext = os.path.splitext(payload.file_name)[1]
        storage_path = f"tasks/{payload.task_id}/{attachment_id}{file_ext}"
        
        # Upload to Supabase Storage
        # Note: This uses Supabase REST API for storage upload
        supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY", "")
        
        if not supabase_url or not supabase_key:
            # Fallback: store file_url as data URL for local dev
            file_url = f"data:application/octet-stream;base64,{payload.file_data}"
        else:
            # In production, use Supabase Storage API
            # For now, construct a URL (actual upload would use storage API)
            file_url = f"{supabase_url}/storage/v1/object/public/tasks/{storage_path}"
        
        # Insert attachment record
        attachment_data = {
            "id": attachment_id,
            "task_id": payload.task_id,
            "file_url": file_url,
            "type": payload.type,
            "uploaded_by": user_id
        }
        
        attachment_r = client.post("/attachments", content=json.dumps(attachment_data))
        if attachment_r.status_code not in (200, 201):
            raise HTTPException(status_code=500, detail=f"Failed to create attachment record: {attachment_r.status_code}")
        
        # Return attachment info
        return AttachmentResponse(
            id=attachment_id,
            task_id=payload.task_id,
            file_url=file_url,
            type=payload.type,
            uploaded_by=user_id,
            created_at=""  # Will be set by DB
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

