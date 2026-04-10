from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user, get_current_user_org, get_supabase_client
from app.db.pg import get_conn
from app.schemas.research_schemas import ScoreIdeaRequest, ScoreResponse
from app.schemas.phase1_schemas import (
    ApprovalRequest,
    ApprovalResponse,
    GenerateResearchRequestsRequest,
    GenerateResearchRequestsResponse,
    ResearchRequestRecord,
    ResearchSubmissionResponse,
    SubmitResearchRequest,
)
from app.services.approval_service import approve_submission, reject_submission
from app.services.asset_ingest_service import create_asset_from_submission
from app.services.research_request_service import generate_requests_for_script, list_research_requests
from app.services.research_submission_service import submit_research
from app.services.research_service import score_idea
from app.utils.org import resolve_org_id

router = APIRouter(prefix="/api/v1/research", tags=["research"])

@router.post("/score", response_model=ScoreResponse)
def post_score(payload: ScoreIdeaRequest, client=Depends(get_supabase_client), user=Depends(get_current_user)):
    try:
        idea_id, score, components = score_idea(
            client=client,
            org_id=payload.org_id,
            channel_id=payload.channel_id,
            title=payload.title,
            url=payload.url,
            user_id=user.get("id") or user.get("user_id", "mock-user")
        )
        return {"idea_id": idea_id, "score": score, "components": components}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/request/generate", response_model=GenerateResearchRequestsResponse)
def generate_research_requests(
    payload: GenerateResearchRequestsRequest,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    org_id = resolve_org_id(org.get("org_id"))
    user_id = user.get("id") or user.get("user_id") or user.get("sub") or "unknown"
    try:
        with get_conn() as conn:
            result = generate_requests_for_script(
                script_id=payload.script_id,
                org_id=org_id,
                assigned_to=payload.assigned_to or user_id,
                conn=conn,
            )
            conn.commit()
            return {
                "created": result["created_count"],
                "skipped": result["skipped_count"],
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/requests")
def get_research_requests(
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    org_id = resolve_org_id(org.get("org_id"))
    try:
        rows = list_research_requests(org_id)
        items = []
        for row in rows:
            latest_submission = None
            if row.get("submission_id"):
                latest_submission = {
                    "submission_id": str(row.get("submission_id")),
                    "research_request_id": str(row.get("research_request_id")),
                    "source_url": row.get("source_url"),
                    "start_time": row.get("start_time"),
                    "end_time": row.get("end_time"),
                    "relevance_type": row.get("relevance_type"),
                    "notes": row.get("notes") or "",
                    "status": row.get("submission_status"),
                }
            items.append(
                {
                    "research_request_id": str(row.get("research_request_id")),
                    "script_line_id": str(row.get("script_line_id")),
                    "org_id": str(row.get("org_id")),
                    "keyword": row.get("keyword"),
                    "status": row.get("status"),
                    "assigned_to": str(row.get("assigned_to")) if row.get("assigned_to") else None,
                    "script_title": row.get("script_title"),
                    "line_number": row.get("line_number"),
                    "raw_text": row.get("raw_text"),
                    "suggested_asset_id": str(row.get("suggested_asset_id")) if row.get("suggested_asset_id") else None,
                    "suggested_match_confidence": float(row.get("suggested_match_confidence")) if row.get("suggested_match_confidence") is not None else None,
                    "suggestion_notes": row.get("suggestion_notes"),
                    "latest_submission": latest_submission,
                }
            )
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit", response_model=ResearchSubmissionResponse)
def post_research_submission(
    payload: SubmitResearchRequest,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    _ = resolve_org_id(org.get("org_id"))
    try:
        with get_conn() as conn:
            submission = submit_research(
                research_request_id=payload.research_request_id,
                source_url=payload.source_url,
                start_time=payload.start_time,
                end_time=payload.end_time,
                relevance_type=payload.relevance_type,
                notes=payload.notes,
                conn=conn,
            )
            conn.commit()
            return {
                "submission_id": str(submission["id"]),
                "research_request_id": str(submission["research_request_id"]),
                "source_url": submission["source_url"],
                "start_time": submission["start_time"],
                "end_time": submission["end_time"],
                "relevance_type": submission["relevance_type"],
                "notes": submission["notes"],
                "status": submission["status"],
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approve", response_model=ApprovalResponse)
def approve_research(
    payload: ApprovalRequest,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    _ = resolve_org_id(org.get("org_id"))
    user_id = user.get("id") or user.get("user_id") or user.get("sub") or "unknown"
    try:
        with get_conn() as conn:
            result = approve_submission(payload.research_submission_id, actor_id=user_id, conn=conn)
            conn.commit()
            return {
                "research_submission_id": result["submission_id"],
                "asset_id": result["asset_id"],
                "status": result["status"],
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reject", response_model=ApprovalResponse)
def reject_research(
    payload: ApprovalRequest,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    _ = resolve_org_id(org.get("org_id"))
    user_id = user.get("id") or user.get("user_id") or user.get("sub") or "unknown"
    try:
        with get_conn() as conn:
            result = reject_submission(payload.research_submission_id, actor_id=user_id, conn=conn)
            conn.commit()
            return {
                "research_submission_id": result["submission_id"],
                "asset_id": None,
                "status": result["status"],
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
