from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any, Optional, Literal


OperatorJobStatus = Literal["QUEUED", "IN_PROGRESS", "PARTIAL_SUCCESS", "COMPLETED", "FAILED", "CANCELLED"]
OperatorJobItemStatus = Literal["PENDING", "PROCESSING", "STORED", "FAILED", "SKIPPED"]
StorageProviderName = Literal["local_stub", "supabase"]


class CreateOperatorJobRequest(BaseModel):
    job_type: str = "INGEST"
    storage_provider: StorageProviderName = "local_stub"
    assigned_to: Optional[str] = None
    submission_ids: list[str] = Field(default_factory=list)


class CreateOperatorJobResponse(BaseModel):
    job_id: str
    status: str
    total_items: int
    processed_items: int
    failed_items: int


class OperatorJobListItem(BaseModel):
    job_id: str
    org_id: str
    job_type: str
    status: str
    requested_by: Optional[str] = None
    assigned_to: Optional[str] = None
    total_items: int
    processed_items: int
    failed_items: int
    storage_provider: str
    locked_by: Optional[str] = None
    locked_at: Optional[str] = None
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None


class OperatorJobItemRecord(BaseModel):
    id: str
    operator_job_id: str
    research_submission_id: Optional[str] = None
    asset_id: Optional[str] = None
    script_line_id: Optional[str] = None
    status: str
    source_url: str
    requested_start_time: Optional[float] = None
    requested_end_time: Optional[float] = None
    normalized_filename: str
    storage_provider: str
    storage_path: str
    checksum: Optional[str] = None
    error_message: str
    retry_count: int = 0
    max_retries: int = 3
    last_retry_at: Optional[str] = None
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None


class OperatorJobDetailResponse(BaseModel):
    job_id: str
    org_id: str
    job_type: str
    status: str
    requested_by: Optional[str] = None
    assigned_to: Optional[str] = None
    total_items: int
    processed_items: int
    failed_items: int
    storage_provider: str
    input_payload_json: dict[str, Any]
    result_payload_json: dict[str, Any]
    error_message: str
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None
    items: list[OperatorJobItemRecord] = Field(default_factory=list)


class StartOperatorJobResponse(BaseModel):
    job_id: str
    status: str


class ProcessOperatorJobItemRequest(BaseModel):
    operator_job_item_id: str
    storage_provider: Optional[StorageProviderName] = None


class ProcessOperatorJobItemResponse(BaseModel):
    job_item: OperatorJobItemRecord
    job: OperatorJobListItem
    dedupe: dict[str, Any] = Field(default_factory=dict)


class CompleteOperatorJobResponse(BaseModel):
    job_id: str
    status: str
    total_items: int
    processed_items: int
    failed_items: int


class RetryFailedItemsResponse(BaseModel):
    job_id: str
    status: str
    retried_items: int
    skipped_items: int


class StorageProviderTestRequest(BaseModel):
    provider: StorageProviderName = "local_stub"
    object_name: str = "probe.mp4"


class StorageProviderTestResponse(BaseModel):
    provider: str
    healthy: bool
    preview_key: str
    preview_url: str
    message: str


class StorageObjectRecord(BaseModel):
    storage_object_id: str
    org_id: str
    asset_id: Optional[str] = None
    provider: str
    bucket_or_drive_id: Optional[str] = None
    object_key: str
    public_url: Optional[str] = None
    mime_type: Optional[str] = None
    byte_size: Optional[int] = None
    checksum: Optional[str] = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)
    created_at: str
    updated_at: str


class StorageObjectListResponse(BaseModel):
    items: list[StorageObjectRecord] = Field(default_factory=list)


class FilenamePreviewRequest(BaseModel):
    script_title: str
    line_number: int
    keyword: str
    asset_id: str
    source_url: Optional[str] = None
    extension: str = "mp4"


class FilenamePreviewResponse(BaseModel):
    rule_id: Optional[str] = None
    rule_name: str
    pattern_template: str
    normalized_filename: str
    is_valid: bool
    reasons: list[str] = Field(default_factory=list)


class FilenameValidateRequest(FilenamePreviewRequest):
    candidate_filename: str


class FilenameValidateResponse(BaseModel):
    rule_id: Optional[str] = None
    rule_name: str
    pattern_template: str
    candidate_filename: str
    is_valid: bool
    reasons: list[str] = Field(default_factory=list)


class ActiveFilenameRuleResponse(BaseModel):
    rule_id: Optional[str] = None
    rule_name: str
    pattern_template: str
    is_active: bool = True


class AssetFingerprintRequest(BaseModel):
    fingerprint_type: Literal["sha256", "filename", "source_url"] = "sha256"
    fingerprint_value: Optional[str] = None


class AssetFingerprintResponse(BaseModel):
    asset_id: str
    fingerprint_type: str
    fingerprint_value: str
    duplicate: bool
    duplicate_asset_id: Optional[str] = None


class AssetIntegrityResponse(BaseModel):
    asset_id: str
    checksum: Optional[str] = None
    duplicates: list[dict[str, Any]] = Field(default_factory=list)
    fingerprints: list[dict[str, Any]] = Field(default_factory=list)
    storage_objects: list[dict[str, Any]] = Field(default_factory=list)


class WorkerStatusResponse(BaseModel):
    worker_id: Optional[str] = None
    running: bool = False
    current_job_id: Optional[str] = None
    current_item_id: Optional[str] = None
    last_poll_at: Optional[str] = None
    poll_interval_seconds: float = 2.0
    queue_size: int = 0
    active_job_count: int = 0
    failed_item_count: int = 0
    message: str = ""
    active_jobs: list[OperatorJobListItem] = Field(default_factory=list)
