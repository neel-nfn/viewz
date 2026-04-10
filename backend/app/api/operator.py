from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user, get_current_user_org
from app.db.pg import get_conn
from app.schemas.phase4_schemas import (
    CompleteOperatorJobResponse,
    CreateOperatorJobRequest,
    CreateOperatorJobResponse,
    OperatorJobDetailResponse,
    OperatorJobListItem,
    ProcessOperatorJobItemRequest,
    ProcessOperatorJobItemResponse,
    RetryFailedItemsResponse,
    StartOperatorJobResponse,
)
from app.services.operator_ingest_service import create_operator_job_from_approved_submissions, process_operator_job_item
from app.services.operator_queue_service import complete_job, create_job, get_job, list_jobs, retry_failed_items, start_job
from app.utils.org import resolve_org_id

router = APIRouter(prefix="/api/v1/operator", tags=["operator"])


@router.post("/jobs", response_model=CreateOperatorJobResponse)
def post_operator_job(
    payload: CreateOperatorJobRequest,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    org_id = resolve_org_id(org.get("org_id"))
    user_id = user.get("id") or user.get("user_id") or user.get("sub") or "unknown"
    try:
        with get_conn() as conn:
            job = create_job(
                org_id=org_id,
                job_type=payload.job_type,
                requested_by=user_id,
                assigned_to=payload.assigned_to,
                storage_provider=payload.storage_provider,
                input_payload_json={"submission_ids": payload.submission_ids or []},
                conn=conn,
            )
            conn.commit()
            return {
                "job_id": job["job_id"],
                "status": job["status"],
                "total_items": job["total_items"],
                "processed_items": job["processed_items"],
                "failed_items": job["failed_items"],
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jobs/from-approved-submissions", response_model=CreateOperatorJobResponse)
def post_operator_job_from_submissions(
    payload: CreateOperatorJobRequest,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    org_id = resolve_org_id(org.get("org_id"))
    user_id = user.get("id") or user.get("user_id") or user.get("sub") or "unknown"
    try:
        with get_conn() as conn:
            result = create_operator_job_from_approved_submissions(
                org_id=org_id,
                requested_by=user_id,
                assigned_to=payload.assigned_to,
                storage_provider=payload.storage_provider,
                submission_ids=payload.submission_ids or None,
                conn=conn,
            )
            conn.commit()
            job = result["job"]
            return {
                "job_id": job["job_id"],
                "status": job["status"],
                "total_items": job["total_items"],
                "processed_items": job["processed_items"],
                "failed_items": job["failed_items"],
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs")
def get_operator_jobs(
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    org_id = resolve_org_id(org.get("org_id"))
    try:
        with get_conn() as conn:
            jobs = list_jobs(org_id, conn=conn)
            return {
                "items": [
                    {
                        "job_id": job["job_id"],
                        "org_id": job["org_id"],
                        "job_type": job["job_type"],
                        "status": job["status"],
                        "requested_by": job["requested_by"],
                        "assigned_to": job["assigned_to"],
                        "total_items": job["total_items"],
                        "processed_items": job["processed_items"],
                        "failed_items": job["failed_items"],
                        "storage_provider": job["storage_provider"],
                        "created_at": job["created_at"],
                        "updated_at": job["updated_at"],
                        "completed_at": job["completed_at"],
                    }
                    for job in jobs
                ]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}", response_model=OperatorJobDetailResponse)
def get_operator_job_detail(
    job_id: str,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    org_id = resolve_org_id(org.get("org_id"))
    try:
        with get_conn() as conn:
            job = get_job(job_id, org_id, conn=conn)
            if not job:
                raise HTTPException(status_code=404, detail="Operator job not found")
            return job
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jobs/{job_id}/start", response_model=StartOperatorJobResponse)
def post_operator_job_start(
    job_id: str,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    _ = resolve_org_id(org.get("org_id"))
    user_id = user.get("id") or user.get("user_id") or user.get("sub") or "unknown"
    try:
        with get_conn() as conn:
            job = start_job(job_id, actor_id=user_id, conn=conn)
            conn.commit()
            return {"job_id": job["job_id"], "status": job["status"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jobs/{job_id}/process-item", response_model=ProcessOperatorJobItemResponse)
def post_operator_job_process_item(
    job_id: str,
    payload: ProcessOperatorJobItemRequest,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    org_id = resolve_org_id(org.get("org_id"))
    user_id = user.get("id") or user.get("user_id") or user.get("sub") or "unknown"
    try:
        with get_conn() as conn:
            item_bundle = process_operator_job_item(
                operator_job_id=job_id,
                operator_job_item_id=payload.operator_job_item_id,
                org_id=org_id,
                actor_id=user_id,
                storage_provider=payload.storage_provider,
                conn=conn,
            )
            conn.commit()
            return item_bundle
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jobs/{job_id}/complete", response_model=CompleteOperatorJobResponse)
def post_operator_job_complete(
    job_id: str,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    _ = resolve_org_id(org.get("org_id"))
    user_id = user.get("id") or user.get("user_id") or user.get("sub") or "unknown"
    try:
        with get_conn() as conn:
            job = complete_job(job_id, actor_id=user_id, conn=conn)
            conn.commit()
            return {
                "job_id": job["job_id"],
                "status": job["status"],
                "total_items": job["total_items"],
                "processed_items": job["processed_items"],
                "failed_items": job["failed_items"],
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/jobs/{job_id}/retry-failed", response_model=RetryFailedItemsResponse)
def post_operator_job_retry_failed(
    job_id: str,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    org_id = resolve_org_id(org.get("org_id"))
    user_id = user.get("id") or user.get("user_id") or user.get("sub") or "unknown"
    try:
        with get_conn() as conn:
            job = get_job(job_id, org_id, conn=conn)
            if not job:
                raise HTTPException(status_code=404, detail="Operator job not found")
            result = retry_failed_items(job_id, actor_id=user_id, conn=conn)
            conn.commit()
            return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
