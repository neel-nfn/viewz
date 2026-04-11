from fastapi import APIRouter, Depends, HTTPException
from app.schemas.workflow_schemas import (
    CreateWorkflowCardRequest,
    UpdateWorkflowCardRequest,
    UpdateWorkflowCardStageRequest,
    WorkflowCardResponse,
    WorkflowCardsListResponse
)
from app.api.deps import get_current_user, get_current_user_org
from app.db.pg import get_conn
from app.utils.org import resolve_org_id
import uuid
import logging

router = APIRouter(prefix="/api/v1/workflow", tags=["workflow"])
logger = logging.getLogger(__name__)

VALID_STAGES = ["ideas", "research", "script", "record", "edit", "thumbnail", "upload", "publish", "published"]


@router.get("/cards", response_model=WorkflowCardsListResponse)
async def list_workflow_cards(
    user=Depends(get_current_user),
    org=Depends(get_current_user_org)
):
    """List all workflow cards for the organization"""
    org_id = resolve_org_id(org.get('org_id'))
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Check if table exists
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'workflow_cards'
                    )
                """)
                table_exists = cur.fetchone().get("exists", False)
                
                if not table_exists:
                    logger.error("workflow_cards table does not exist. Please run migration 021_workflow_cards.sql")
                    raise HTTPException(
                        status_code=500, 
                        detail="Workflow cards table not found. Please ensure database migrations have been run."
                    )
                
                cur.execute("""
                    SELECT id, org_id, title, description, meta, stage, tags, 
                           topic_idea_id, position, created_by, created_at, updated_at
                    FROM workflow_cards
                    WHERE org_id = %s
                    ORDER BY stage, position, created_at DESC
                """, (org_id,))
                
                rows = cur.fetchall()
                cards = []
                for row in rows:
                    try:
                        cards.append(WorkflowCardResponse(
                            id=str(row["id"]),
                            org_id=str(row["org_id"]),
                            title=row["title"] or "",
                            description=row.get("description"),
                            meta=row.get("meta"),
                            stage=row["stage"],
                            tags=row["tags"] or [],
                            topic_idea_id=str(row["topic_idea_id"]) if row.get("topic_idea_id") else None,
                            position=row.get("position") or 0,
                            created_by=str(row["created_by"]),
                            created_at=row["created_at"],
                            updated_at=row["updated_at"]
                        ))
                    except Exception as card_error:
                        logger.error(f"Error creating WorkflowCardResponse from row: {card_error}, row: {row}")
                        raise
                
                return WorkflowCardsListResponse(cards=cards)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing workflow cards: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list workflow cards: {str(e)}")


@router.post("/cards", response_model=WorkflowCardResponse)
async def create_workflow_card(
    payload: CreateWorkflowCardRequest,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org)
):
    """Create a new workflow card"""
    org_id = resolve_org_id(org.get('org_id'))
    user_id = user.get("user_id") or user.get("sub") or "unknown"
    
    if payload.stage not in VALID_STAGES:
        raise HTTPException(status_code=400, detail=f"Invalid stage. Must be one of: {VALID_STAGES}")
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Get max position in the stage
                cur.execute("""
                    SELECT COALESCE(MAX(position), 0) as max_pos
                    FROM workflow_cards
                    WHERE org_id = %s AND stage = %s
                """, (org_id, payload.stage))
                max_pos_row = cur.fetchone()
                next_position = (max_pos_row.get("max_pos") or 0) + 1 if max_pos_row else 1
                
                card_id = uuid.uuid4()
                # Convert user_id to UUID if it's a string
                try:
                    created_by_uuid = uuid.UUID(str(user_id)) if user_id != "unknown" else uuid.uuid4()
                except (ValueError, TypeError):
                    created_by_uuid = uuid.uuid4()
                
                topic_idea_uuid = None
                if payload.topic_idea_id:
                    try:
                        topic_idea_uuid = uuid.UUID(payload.topic_idea_id)
                    except (ValueError, TypeError):
                        topic_idea_uuid = None
                
                cur.execute("""
                    INSERT INTO workflow_cards 
                    (id, org_id, title, description, meta, stage, tags, topic_idea_id, position, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, org_id, title, description, meta, stage, tags, topic_idea_id, position, created_by, created_at, updated_at
                """, (
                    card_id, org_id, payload.title, payload.description, payload.meta,
                    payload.stage, payload.tags or [], topic_idea_uuid, next_position, created_by_uuid
                ))
                
                row = cur.fetchone()
                conn.commit()
                
                if not row:
                    raise HTTPException(status_code=500, detail="Failed to create workflow card")
                
                return WorkflowCardResponse(
                    id=str(row["id"]),
                    org_id=str(row["org_id"]),
                    title=row["title"] or "",
                    description=row.get("description"),
                    meta=row.get("meta"),
                    stage=row["stage"],
                    tags=row.get("tags") or [],
                    topic_idea_id=str(row["topic_idea_id"]) if row.get("topic_idea_id") else None,
                    position=row.get("position") or 0,
                    created_by=str(row["created_by"]),
                    created_at=row["created_at"],
                    updated_at=row["updated_at"]
                )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating workflow card: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create workflow card: {str(e)}")


@router.put("/cards/{card_id}", response_model=WorkflowCardResponse)
async def update_workflow_card(
    card_id: str,
    payload: UpdateWorkflowCardRequest,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org)
):
    """Update a workflow card"""
    org_id = resolve_org_id(org.get('org_id'))
    
    if payload.stage and payload.stage not in VALID_STAGES:
        raise HTTPException(status_code=400, detail=f"Invalid stage. Must be one of: {VALID_STAGES}")
    
    try:
        with get_conn() as conn, conn.cursor() as cur:
            # Verify card belongs to org
            cur.execute("""
                SELECT id, org_id, stage FROM workflow_cards
                WHERE id = %s AND org_id = %s
            """, (card_id, org_id))
            existing = cur.fetchone()
            
            if not existing:
                raise HTTPException(status_code=404, detail="Workflow card not found")
            
            # Build update query dynamically
            updates = []
            values = []
            
            if payload.title is not None:
                updates.append("title = %s")
                values.append(payload.title)
            if payload.description is not None:
                updates.append("description = %s")
                values.append(payload.description)
            if payload.meta is not None:
                updates.append("meta = %s")
                values.append(payload.meta)
            if payload.stage is not None:
                updates.append("stage = %s")
                values.append(payload.stage)
            if payload.tags is not None:
                updates.append("tags = %s")
                values.append(payload.tags)
            if payload.topic_idea_id is not None:
                updates.append("topic_idea_id = %s")
                values.append(payload.topic_idea_id if payload.topic_idea_id else None)
            if payload.position is not None:
                updates.append("position = %s")
                values.append(payload.position)
            
            if not updates:
                # No changes, return existing card
                cur.execute("""
                    SELECT id, org_id, title, description, meta, stage, tags, 
                           topic_idea_id, position, created_by, created_at, updated_at
                    FROM workflow_cards
                    WHERE id = %s AND org_id = %s
                """, (card_id, org_id))
                row = cur.fetchone()
            else:
                values.extend([card_id, org_id])
                query = f"""
                    UPDATE workflow_cards
                    SET {', '.join(updates)}, updated_at = now()
                    WHERE id = %s AND org_id = %s
                    RETURNING id, org_id, title, description, meta, stage, tags, 
                              topic_idea_id, position, created_by, created_at, updated_at
                """
                cur.execute(query, values)
                row = cur.fetchone()
                conn.commit()
            
            return WorkflowCardResponse(
                id=str(row["id"]),
                org_id=str(row["org_id"]),
                title=row["title"],
                description=row["description"],
                meta=row["meta"],
                stage=row["stage"],
                tags=row["tags"] or [],
                topic_idea_id=str(row["topic_idea_id"]) if row["topic_idea_id"] else None,
                position=row["position"] or 0,
                created_by=str(row["created_by"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating workflow card: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/cards/{card_id}/stage", response_model=WorkflowCardResponse)
async def update_workflow_card_stage(
    card_id: str,
    payload: UpdateWorkflowCardStageRequest,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org)
):
    """Move a workflow card to a new stage"""
    org_id = resolve_org_id(org.get('org_id'))
    
    if payload.stage not in VALID_STAGES:
        raise HTTPException(status_code=400, detail=f"Invalid stage. Must be one of: {VALID_STAGES}")
    
    try:
        with get_conn() as conn, conn.cursor() as cur:
            # Verify card belongs to org
            cur.execute("""
                SELECT id, org_id, stage FROM workflow_cards
                WHERE id = %s AND org_id = %s
            """, (card_id, org_id))
            existing = cur.fetchone()
            
            if not existing:
                raise HTTPException(status_code=404, detail="Workflow card not found")
            
            # Get max position in the new stage
            cur.execute("""
                SELECT COALESCE(MAX(position), 0) as max_pos
                FROM workflow_cards
                WHERE org_id = %s AND stage = %s
            """, (org_id, payload.stage))
            max_pos_row = cur.fetchone()
            next_position = (max_pos_row["max_pos"] or 0) + 1
            
            # Update card stage and position
            cur.execute("""
                UPDATE workflow_cards
                SET stage = %s, position = %s, updated_at = now()
                WHERE id = %s AND org_id = %s
                RETURNING id, org_id, title, description, meta, stage, tags, 
                          topic_idea_id, position, created_by, created_at, updated_at
            """, (payload.stage, next_position, card_id, org_id))
            
            row = cur.fetchone()
            conn.commit()
            
            return WorkflowCardResponse(
                id=str(row["id"]),
                org_id=str(row["org_id"]),
                title=row["title"],
                description=row["description"],
                meta=row["meta"],
                stage=row["stage"],
                tags=row["tags"] or [],
                topic_idea_id=str(row["topic_idea_id"]) if row["topic_idea_id"] else None,
                position=row["position"] or 0,
                created_by=str(row["created_by"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating workflow card stage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cards/{card_id}")
async def delete_workflow_card(
    card_id: str,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org)
):
    """Delete a workflow card"""
    org_id = resolve_org_id(org.get('org_id'))
    
    try:
        with get_conn() as conn, conn.cursor() as cur:
            # Verify card belongs to org
            cur.execute("""
                SELECT id FROM workflow_cards
                WHERE id = %s AND org_id = %s
            """, (card_id, org_id))
            existing = cur.fetchone()
            
            if not existing:
                raise HTTPException(status_code=404, detail="Workflow card not found")
            
            cur.execute("""
                DELETE FROM workflow_cards
                WHERE id = %s AND org_id = %s
            """, (card_id, org_id))
            
            conn.commit()
            return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting workflow card: {e}")
        raise HTTPException(status_code=500, detail=str(e))

