TRANSITIONS = {
    "script_lines": {
        "NEEDS_RESEARCH": {"RESEARCH_IN_PROGRESS", "READY_FOR_LINK"},
        "RESEARCH_IN_PROGRESS": {"READY_FOR_LINK", "NEEDS_RESEARCH"},
        "READY_FOR_LINK": {"LINKED", "RESEARCH_IN_PROGRESS"},
        "LINKED": set(),
    },
    "research_requests": {
        "PENDING": {"IN_PROGRESS", "SUBMITTED", "REJECTED"},
        "IN_PROGRESS": {"SUBMITTED", "REJECTED"},
        "SUBMITTED": {"APPROVED", "REJECTED"},
        "APPROVED": set(),
        "REJECTED": {"PENDING", "IN_PROGRESS"},
    },
    "research_submissions": {
        "PENDING_REVIEW": {"APPROVED", "REJECTED"},
        "APPROVED": set(),
        "REJECTED": set(),
    },
    "assets": {
        "PENDING_VALIDATION": {"READY", "REJECTED"},
        "READY": set(),
        "REJECTED": set(),
    },
    "operator_jobs": {
        "QUEUED": {"IN_PROGRESS", "CANCELLED"},
        "IN_PROGRESS": {"PARTIAL_SUCCESS", "COMPLETED", "FAILED", "CANCELLED"},
        "PARTIAL_SUCCESS": {"COMPLETED", "FAILED", "CANCELLED", "QUEUED"},
        "COMPLETED": set(),
        "FAILED": {"QUEUED"},
        "CANCELLED": set(),
    },
    "operator_job_items": {
        "PENDING": {"PROCESSING", "FAILED", "SKIPPED"},
        "PROCESSING": {"STORED", "FAILED", "SKIPPED"},
        "STORED": set(),
        "FAILED": set(),
        "SKIPPED": set(),
    },
    "editor_instructions": {
        "DRAFT": {"GENERATED", "APPROVED", "OVERRIDDEN"},
        "GENERATED": {"DRAFT", "APPROVED", "OVERRIDDEN"},
        "APPROVED": {"GENERATED", "OVERRIDDEN"},
        "OVERRIDDEN": {"GENERATED", "APPROVED"},
    },
}


def assert_transition(entity: str, current_status: str | None, next_status: str) -> None:
    current = current_status or ""
    allowed = TRANSITIONS.get(entity, {}).get(current, None)
    if allowed is None:
        raise ValueError(f"Unknown entity/status transition: {entity}:{current}")
    if next_status not in allowed and current != next_status:
        raise ValueError(f"Invalid transition for {entity}: {current} -> {next_status}")
