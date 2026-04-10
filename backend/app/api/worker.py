from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user, get_current_user_org
from app.schemas.phase4_schemas import WorkerStatusResponse
from app.services.job_worker_service import get_worker_status, start_worker, stop_worker
from app.utils.org import resolve_org_id

router = APIRouter(prefix="/api/v1/worker", tags=["worker"])


@router.post("/start", response_model=WorkerStatusResponse)
def post_worker_start(
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    _ = user
    org_id = resolve_org_id(org.get("org_id"))
    try:
        start_worker()
        return get_worker_status(org_id=org_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop", response_model=WorkerStatusResponse)
def post_worker_stop(
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    _ = user
    org_id = resolve_org_id(org.get("org_id"))
    try:
        stop_worker()
        return get_worker_status(org_id=org_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=WorkerStatusResponse)
def get_worker_status_endpoint(
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
):
    _ = user
    org_id = resolve_org_id(org.get("org_id"))
    try:
        return get_worker_status(org_id=org_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
