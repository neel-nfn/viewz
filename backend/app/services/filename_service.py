from __future__ import annotations

import re
import uuid
from typing import Any

from app.db.pg import get_conn


DEFAULT_PATTERN = "{script_slug}-line-{line_number:03d}-{keyword_slug}-{asset_id8}.{extension}"
DEFAULT_RULE_NAME = "default"
ALLOWED_FILENAME_RE = re.compile(r"^[a-z0-9._-]+$")


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")
    return cleaned or "asset"


def _normalize_extension(extension: str) -> str:
    ext = (extension or "mp4").strip().lower().lstrip(".")
    return ext or "mp4"


def _metadata_context(metadata: dict[str, Any]) -> dict[str, Any]:
    asset_id = str(metadata.get("asset_id") or uuid.uuid4())
    script_title = metadata.get("script_title") or metadata.get("title") or "script"
    keyword = metadata.get("keyword") or metadata.get("line_text") or "clip"
    line_number = int(metadata.get("line_number") or 0)
    extension = _normalize_extension(metadata.get("extension") or "mp4")

    return {
        "script_slug": _slugify(script_title),
        "keyword_slug": _slugify(keyword),
        "source_slug": _slugify(metadata.get("source_url") or "source"),
        "asset_id8": asset_id[:8],
        "asset_id": asset_id,
        "line_number": line_number,
        "extension": extension,
    }


def _safe_format(template: str, context: dict[str, Any]) -> str:
    try:
        return template.format(**context)
    except Exception:
        return DEFAULT_PATTERN.format(**context)


def ensure_active_filename_rule(org_id: str, conn=None):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                select id, org_id, rule_name, pattern_template, is_active, created_at, updated_at
                from filename_rules
                where org_id = %s and is_active = true
                order by created_at desc
                limit 1
                """,
                (org_id,),
            )
            rule = cur.fetchone()
            if rule:
                return rule

            rule_id = str(uuid.uuid4())
            cur.execute(
                """
                insert into filename_rules (id, org_id, rule_name, pattern_template, is_active)
                values (%s, %s, %s, %s, true)
                returning id, org_id, rule_name, pattern_template, is_active, created_at, updated_at
                """,
                (rule_id, org_id, DEFAULT_RULE_NAME, DEFAULT_PATTERN),
            )
            return cur.fetchone()
    finally:
        if owns_conn:
            db.close()


def list_filename_rules(org_id: str, conn=None):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                select id, org_id, rule_name, pattern_template, is_active, created_at, updated_at
                from filename_rules
                where org_id = %s
                order by is_active desc, created_at desc
                """,
                (org_id,),
            )
            rows = cur.fetchall()
            if rows:
                return rows
            return [ensure_active_filename_rule(org_id, conn=db)]
    finally:
        if owns_conn:
            db.close()


def build_normalized_filename(metadata: dict[str, Any], rule: dict[str, Any] | None = None, org_id: str | None = None, conn=None):
    rule_row = rule or (ensure_active_filename_rule(org_id, conn=conn) if org_id else None)
    if not rule_row:
        rule_row = {
            "id": None,
            "rule_name": DEFAULT_RULE_NAME,
            "pattern_template": DEFAULT_PATTERN,
            "is_active": True,
        }
    context = _metadata_context(metadata)
    normalized = _safe_format(rule_row["pattern_template"], context).strip().lower()
    normalized = re.sub(r"[^a-z0-9._/-]+", "-", normalized)
    normalized = normalized.replace("//", "/")
    normalized = normalized.replace(" ", "-")
    if "/" in normalized:
        normalized = normalized.split("/")[-1]
    if not normalized.endswith(f".{context['extension']}"):
        normalized = f"{normalized}.{context['extension']}"
    if not ALLOWED_FILENAME_RE.match(normalized):
        normalized = re.sub(r"[^a-z0-9._-]+", "-", normalized)
    return {
        "rule": rule_row,
        "normalized_filename": normalized,
        "context": context,
    }


def validate_filename(candidate_filename: str, metadata: dict[str, Any], rule: dict[str, Any] | None = None, org_id: str | None = None, conn=None):
    built = build_normalized_filename(metadata, rule=rule, org_id=org_id, conn=conn)
    normalized_candidate = (candidate_filename or "").strip().lower()
    reasons: list[str] = []

    if not normalized_candidate:
        reasons.append("Filename is required")
    if normalized_candidate != built["normalized_filename"]:
        reasons.append("Filename does not match normalized pattern")
    if not ALLOWED_FILENAME_RE.match(normalized_candidate or ""):
        reasons.append("Filename contains invalid characters")
    if ".." in normalized_candidate or normalized_candidate.startswith("."):
        reasons.append("Filename path is not allowed")

    return {
        "rule": built["rule"],
        "normalized_filename": built["normalized_filename"],
        "candidate_filename": normalized_candidate,
        "is_valid": len(reasons) == 0,
        "reasons": reasons,
    }


def preview_filename(metadata: dict[str, Any], org_id: str, conn=None):
    built = build_normalized_filename(metadata, org_id=org_id, conn=conn)
    return {
        "rule": built["rule"],
        "normalized_filename": built["normalized_filename"],
        "is_valid": True,
        "reasons": [],
    }
