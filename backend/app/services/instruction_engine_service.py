from __future__ import annotations

import json
import os
import re
import uuid
from typing import Any

import httpx
from psycopg.types.json import Jsonb

from app.db.pg import get_conn
from app.services.instruction_formatter_service import format_instruction_text
from app.services.instruction_versioning_service import (
    get_next_instruction_version,
    list_instruction_versions,
    save_instruction_version,
)
from app.services.state_machine_service import assert_transition
from app.services.workflow_event_service import log_event


def _headline(value: str, max_words: int = 8) -> str:
    words = [word for word in re.findall(r"\S+", (value or "").strip()) if word]
    if not words:
        return ""
    return " ".join(words[:max_words]).strip(' "\'')


def _slug_token(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", " ", (value or "").lower())
    tokens = [token for token in cleaned.split() if len(token) > 2]
    return " ".join(tokens)


def _deterministic_instruction(line: dict[str, Any], asset: dict[str, Any], link: dict[str, Any]) -> dict[str, Any]:
    raw_text = line.get("raw_text") or ""
    tokens = _slug_token(raw_text)
    has_emphasis = any(word in tokens for word in ("important", "key", "highlight", "focus", "reveal", "show"))
    has_energy = any(word in tokens for word in ("big", "win", "fast", "impact", "power", "strong", "scale"))

    start = float(link.get("selected_start") or asset.get("start_time") or 0)
    duration = float(link.get("duration") or max(0.1, float(asset.get("end_time") or 0) - float(asset.get("start_time") or 0)))
    overlay = _headline(raw_text)
    motion = "slow_zoom" if has_emphasis or has_energy else "none"
    transition = "cut" if duration <= 8 else "fade"
    sfx = "whoosh" if motion != "none" else "none"
    music = "build_up" if has_energy else "none"
    effects = "subtle punch-in" if has_emphasis else "none"
    visual_type = "highlight" if has_emphasis else "supporting"
    text_style = "bold_center" if overlay else "lower_third"

    return {
        "clip": {
            "start": round(start, 2),
            "duration": round(duration, 2),
        },
        "visual": {
            "type": visual_type,
            "motion": motion,
        },
        "text": {
            "overlay": overlay,
            "style": text_style,
        },
        "audio": {
            "sfx": sfx,
            "music": music,
        },
        "transition": transition,
        "effects": effects,
    }


def _build_prompt(line: dict[str, Any], asset: dict[str, Any], link: dict[str, Any]) -> str:
    return "\n".join(
        [
            "You are a video editor assistant.",
            "Return STRICT JSON only. No markdown, no commentary, no code fences.",
            "Output keys: clip, visual, text, audio, transition, effects.",
            "clip.start and clip.duration must be numbers.",
            "visual.type, visual.motion, text.overlay, text.style, audio.sfx, audio.music, transition, effects must be strings.",
            "",
            f"Script line: {line.get('raw_text') or ''}",
            f"Script title: {line.get('script_title') or ''}",
            f"Line number: {line.get('line_number') or ''}",
            f"Linked asset filename: {asset.get('filename') or ''}",
            f"Linked asset source: {asset.get('source_url') or ''}",
            f"Selected start: {link.get('selected_start') or asset.get('start_time') or 0}",
            f"Duration: {link.get('duration') or max(0.1, float(asset.get('end_time') or 0) - float(asset.get('start_time') or 0))}",
        ]
    )


def _extract_json_blob(value: str) -> dict[str, Any]:
    if not value:
        raise ValueError("Empty AI response")
    text = value.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            raise
        return json.loads(match.group(0))


def _call_gemini(prompt: str) -> dict[str, Any] | None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    model = os.getenv("GEMINI_MODEL", "gemini-pro")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    try:
        response = httpx.post(
            url,
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.2,
                    "topP": 0.9,
                    "topK": 40,
                },
            },
            timeout=60.0,
        )
        response.raise_for_status()
        data = response.json()
        text = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )
        if not text:
            return None
        return _extract_json_blob(text)
    except Exception:
        return None


def _normalize_instruction_payload(payload: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any]:
    clip = payload.get("clip") or {}
    visual = payload.get("visual") or {}
    text = payload.get("text") or {}
    audio = payload.get("audio") or {}

    normalized = {
        "clip": {
            "start": float(clip.get("start", fallback["clip"]["start"])),
            "duration": float(clip.get("duration", fallback["clip"]["duration"])),
        },
        "visual": {
            "type": str(visual.get("type") or fallback["visual"]["type"]),
            "motion": str(visual.get("motion") or fallback["visual"]["motion"]),
        },
        "text": {
            "overlay": str(text.get("overlay") or fallback["text"]["overlay"]),
            "style": str(text.get("style") or fallback["text"]["style"]),
        },
        "audio": {
            "sfx": str(audio.get("sfx") or fallback["audio"]["sfx"]),
            "music": str(audio.get("music") or fallback["audio"]["music"]),
        },
        "transition": str(payload.get("transition") or fallback["transition"]),
        "effects": str(payload.get("effects") or fallback["effects"]),
    }
    return normalized


def get_instruction_for_line(script_line_id: str, org_id: str, conn=None):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                select
                    ei.id as instruction_id,
                    ei.script_line_id,
                    ei.asset_id,
                    ei.instruction_json,
                    ei.instruction_text,
                    ei.clip_start,
                    ei.clip_duration,
                    ei.transition,
                    ei.motion,
                    ei.text_overlay,
                    ei.sound_design,
                    ei.effects,
                    ei.status,
                    ei.created_at,
                    ei.updated_at,
                    sl.line_number,
                    sl.raw_text,
                    s.title as script_title,
                    a.filename as asset_filename
                from editor_instructions ei
                join script_lines sl on sl.id = ei.script_line_id
                join scripts s on s.id = sl.script_id
                join assets a on a.id = ei.asset_id
                where ei.script_line_id = %s and s.org_id = %s
                """,
                (script_line_id, org_id),
            )
            instruction = cur.fetchone()
            if not instruction:
                return None

            versions = list_instruction_versions(str(instruction["instruction_id"]), conn=db)
            return {
                "instruction": instruction,
                "versions": versions,
            }
    finally:
        if owns_conn:
            db.close()


def generate_instruction(script_line_id: str, org_id: str, actor_id: str | None = None, conn=None):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                select
                    sl.id as script_line_id,
                    sl.line_number,
                    sl.raw_text,
                    sl.status as line_status,
                    s.title as script_title,
                    s.org_id
                from script_lines sl
                join scripts s on s.id = sl.script_id
                where sl.id = %s and s.org_id = %s
                """,
                (script_line_id, org_id),
            )
            line = cur.fetchone()
            if not line:
                raise ValueError("Script line not found")
            if line.get("line_status") != "LINKED":
                raise ValueError("Script line must be LINKED before generating instructions")

            cur.execute(
                """
                select
                    al.id as link_id,
                    al.asset_id,
                    al.selected_start,
                    al.duration,
                    a.filename,
                    a.source_url,
                    a.start_time,
                    a.end_time,
                    a.status as asset_status
                from line_asset_links al
                join assets a on a.id = al.asset_id
                where al.script_line_id = %s
                limit 1
                """,
                (script_line_id,),
            )
            link = cur.fetchone()
            if not link:
                raise ValueError("Linked asset not found")
            if link.get("asset_status") != "READY":
                raise ValueError("Asset must be READY before generating instructions")

            fallback = _deterministic_instruction(line, link, link)
            prompt = _build_prompt(line, link, link)
            ai_payload = _call_gemini(prompt)
            payload = _normalize_instruction_payload(ai_payload or {}, fallback)
            instruction_text = format_instruction_text(payload)

            cur.execute(
                """
                select id, status
                from editor_instructions
                where script_line_id = %s
                """,
                (script_line_id,),
            )
            existing = cur.fetchone()
            if existing:
                assert_transition("editor_instructions", existing.get("status"), "GENERATED")
                instruction_id = str(existing["id"])
                cur.execute(
                    """
                    update editor_instructions
                    set asset_id = %s,
                        instruction_json = %s,
                        instruction_text = %s,
                        clip_start = %s,
                        clip_duration = %s,
                        transition = %s,
                        motion = %s,
                        text_overlay = %s,
                        sound_design = %s,
                        effects = %s,
                        status = %s,
                        updated_at = now()
                    where id = %s
                    returning id
                    """,
                    (
                        link["asset_id"],
                        Jsonb(payload),
                        instruction_text,
                        payload["clip"]["start"],
                        payload["clip"]["duration"],
                        payload["transition"],
                        payload["visual"]["motion"],
                        payload["text"]["overlay"],
                        payload["audio"]["sfx"],
                        payload["effects"],
                        "GENERATED",
                        instruction_id,
                    ),
                )
            else:
                instruction_id = str(uuid.uuid4())
                cur.execute(
                    """
                    insert into editor_instructions
                        (id, script_line_id, asset_id, instruction_json, instruction_text,
                         clip_start, clip_duration, transition, motion, text_overlay,
                         sound_design, effects, status)
                    values
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    returning id
                    """,
                    (
                        instruction_id,
                        script_line_id,
                        link["asset_id"],
                        Jsonb(payload),
                        instruction_text,
                        payload["clip"]["start"],
                        payload["clip"]["duration"],
                        payload["transition"],
                        payload["visual"]["motion"],
                        payload["text"]["overlay"],
                        payload["audio"]["sfx"],
                        payload["effects"],
                        "GENERATED",
                    ),
                )

            next_version = get_next_instruction_version(instruction_id, conn=db)
            save_instruction_version(instruction_id, next_version, payload, conn=db)
            log_event(
                entity_type="editor_instructions",
                entity_id=instruction_id,
                action="generate",
                from_status=existing.get("status") if existing else None,
                to_status="GENERATED",
                payload={"script_line_id": script_line_id, "version": next_version},
                actor_id=actor_id,
                conn=conn,
            )
            if owns_conn:
                db.commit()
            result = get_instruction_for_line(script_line_id, org_id, conn=db)
            if not result:
                raise ValueError("Instruction generation failed")
            return result
    except Exception:
        if owns_conn:
            db.rollback()
        raise
    finally:
        if owns_conn:
            db.close()


def update_instruction(
    instruction_id: str,
    org_id: str,
    instruction_json: dict[str, Any],
    instruction_text: str | None = None,
    status: str = "OVERRIDDEN",
    actor_id: str | None = None,
    conn=None,
):
    owns_conn = conn is None
    db = conn or get_conn()
    try:
        with db.cursor() as cur:
            cur.execute(
                """
                select
                    ei.id,
                    ei.script_line_id,
                    ei.asset_id,
                    ei.status,
                    s.org_id
                from editor_instructions ei
                join script_lines sl on sl.id = ei.script_line_id
                join scripts s on s.id = sl.script_id
                where ei.id = %s and s.org_id = %s
                """,
                (instruction_id, org_id),
            )
            instruction = cur.fetchone()
            if not instruction:
                raise ValueError("Instruction not found")

            assert_transition("editor_instructions", instruction.get("status"), status)
            fallback = _deterministic_instruction({"raw_text": ""}, {"start_time": 0, "end_time": 0}, {"selected_start": 0, "duration": 0})
            payload = _normalize_instruction_payload(instruction_json, fallback)
            text = instruction_text or format_instruction_text(payload)

            cur.execute(
                """
                update editor_instructions
                set instruction_json = %s,
                    instruction_text = %s,
                    clip_start = %s,
                    clip_duration = %s,
                    transition = %s,
                    motion = %s,
                    text_overlay = %s,
                    sound_design = %s,
                    effects = %s,
                    status = %s,
                    updated_at = now()
                where id = %s
                """,
                (
                    Jsonb(payload),
                    text,
                    payload["clip"]["start"],
                    payload["clip"]["duration"],
                    payload["transition"],
                    payload["visual"]["motion"],
                    payload["text"]["overlay"],
                    payload["audio"]["sfx"],
                    payload["effects"],
                    status,
                    instruction_id,
                ),
            )

            next_version = get_next_instruction_version(instruction_id, conn=db)
            save_instruction_version(instruction_id, next_version, payload, conn=db)
            log_event(
                entity_type="editor_instructions",
                entity_id=instruction_id,
                action="update",
                from_status=instruction.get("status"),
                to_status=status,
                payload={"version": next_version},
                actor_id=actor_id,
                conn=conn,
            )
            if owns_conn:
                db.commit()

            result = get_instruction_for_line(str(instruction["script_line_id"]), str(instruction["org_id"]), conn=db)
            if not result:
                raise ValueError("Instruction update failed")
            return result
    except Exception:
        if owns_conn:
            db.rollback()
        raise
    finally:
        if owns_conn:
            db.close()
