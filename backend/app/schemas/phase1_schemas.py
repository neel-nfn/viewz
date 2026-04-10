from pydantic import BaseModel, Field
from typing import Any, Optional, Literal


ScriptStatus = Literal["DRAFT", "ACTIVE", "ARCHIVED"]
LineStatus = Literal["NEEDS_RESEARCH", "RESEARCH_IN_PROGRESS", "READY_FOR_LINK", "LINKED"]
RequestStatus = Literal["PENDING", "IN_PROGRESS", "SUBMITTED", "APPROVED", "REJECTED"]
SubmissionStatus = Literal["PENDING_REVIEW", "APPROVED", "REJECTED"]
RelevanceType = Literal["DIRECT_MATCH", "RELATED_MATCH"]


class CreateScriptRequest(BaseModel):
    title: str
    source_text: str
    status: ScriptStatus = "DRAFT"


class CreateScriptResponse(BaseModel):
    script_id: str
    title: str
    status: str
    lines_created: int


class ScriptLineResponse(BaseModel):
    id: str
    script_id: str
    line_number: int
    raw_text: str
    status: str
    matched_asset_id: Optional[str] = None
    research_request_id: Optional[str] = None
    suggested_asset_id: Optional[str] = None
    suggested_match_confidence: Optional[float] = None
    suggestion_notes: Optional[str] = None
    created_at: str
    updated_at: str


class ScriptDetailResponse(BaseModel):
    script_id: str
    title: str
    source_text: str
    status: str
    lines: list[ScriptLineResponse] = Field(default_factory=list)


class GenerateResearchRequestsRequest(BaseModel):
    script_id: str
    assigned_to: Optional[str] = None


class GenerateResearchRequestsResponse(BaseModel):
    created: int
    skipped: int


class SubmitResearchRequest(BaseModel):
    research_request_id: str
    source_url: str
    start_time: float
    end_time: float
    relevance_type: RelevanceType
    notes: str = ""


class ResearchSubmissionResponse(BaseModel):
    submission_id: str
    research_request_id: str
    source_url: str
    start_time: float
    end_time: float
    relevance_type: str
    notes: str
    status: str


class ResearchRequestRecord(BaseModel):
    research_request_id: str
    script_line_id: str
    org_id: str
    keyword: str
    status: str
    assigned_to: Optional[str] = None
    script_title: str
    line_number: int
    raw_text: str
    latest_submission: Optional[ResearchSubmissionResponse] = None
    suggested_asset_id: Optional[str] = None
    suggested_match_confidence: Optional[float] = None
    suggestion_notes: Optional[str] = None


class CreateAssetFromSubmissionRequest(BaseModel):
    research_submission_id: str


class AssetResponse(BaseModel):
    asset_id: str
    org_id: str
    research_submission_id: Optional[str] = None
    source_url: str
    start_time: float
    end_time: float
    filename: str
    status: str


class AssetListItem(BaseModel):
    asset_id: str
    org_id: str
    research_submission_id: Optional[str] = None
    source_url: str
    start_time: float
    end_time: float
    filename: str
    status: str
    validation_count: int = 0
    last_validation_result: Optional[str] = None
    last_validation_notes: Optional[str] = None


class LinkAssetRequest(BaseModel):
    script_line_id: str
    research_submission_id: Optional[str] = None
    asset_id: Optional[str] = None
    selected_start: float
    duration: float


class LinkAssetResponse(BaseModel):
    link_id: str
    script_line_id: str
    asset_id: str
    selected_start: float
    duration: float


class AutoMatchRequest(BaseModel):
    script_line_id: str


class AutoMatchResponse(BaseModel):
    script_line_id: str
    matched: bool
    suggested_asset_id: Optional[str] = None
    suggested_match_confidence: Optional[float] = None
    suggestion_notes: Optional[str] = None


class ApprovalRequest(BaseModel):
    research_submission_id: str


class ApprovalResponse(BaseModel):
    research_submission_id: str
    asset_id: Optional[str] = None
    status: str


class AssetValidationRequest(BaseModel):
    asset_id: str
    validation_type: str = "manual"
    notes: str = ""


class AssetValidationResponse(BaseModel):
    asset_id: str
    result: str
    notes: str
    status: str


InstructionStatus = Literal["DRAFT", "GENERATED", "APPROVED", "OVERRIDDEN"]


class GenerateInstructionRequest(BaseModel):
    script_line_id: str


class InstructionVersionResponse(BaseModel):
    id: str
    instruction_id: str
    version: int
    instruction_json: dict[str, Any]
    created_at: str


class EditorInstructionResponse(BaseModel):
    instruction_id: str
    script_line_id: str
    asset_id: str
    script_title: str
    line_number: int
    raw_text: str
    asset_filename: str
    clip_start: float
    clip_duration: float
    transition: str
    motion: str
    text_overlay: str
    sound_design: str
    effects: str
    status: str
    instruction_json: dict[str, Any]
    instruction_text: str
    created_at: str
    updated_at: str
    versions: list[InstructionVersionResponse] = Field(default_factory=list)


class UpdateInstructionRequest(BaseModel):
    instruction_id: str
    instruction_json: dict[str, Any]
    instruction_text: Optional[str] = None
    status: InstructionStatus = "OVERRIDDEN"
