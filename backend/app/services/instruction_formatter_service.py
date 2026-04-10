from __future__ import annotations

from typing import Any


def format_instruction_text(instruction_json: dict[str, Any]) -> str:
    clip = instruction_json.get("clip") or {}
    visual = instruction_json.get("visual") or {}
    text = instruction_json.get("text") or {}
    audio = instruction_json.get("audio") or {}
    transition = instruction_json.get("transition") or "cut"
    effects = instruction_json.get("effects") or ""

    start = clip.get("start")
    duration = clip.get("duration")
    overlay = text.get("overlay") or ""
    motion = visual.get("motion") or "none"
    sfx = audio.get("sfx") or "none"
    music = audio.get("music") or "none"

    lines = []
    if start is not None and duration is not None:
        lines.append(f"Use clip from {start:.2f}s for {duration:.2f}s.")
    if motion and motion != "none":
        lines.append(f"Apply {motion}.")
    if overlay:
        lines.append(f'Add text overlay: "{overlay}".')
    if sfx and sfx != "none":
        lines.append(f"Use SFX: {sfx}.")
    if music and music != "none":
        lines.append(f"Music cue: {music}.")
    if transition:
        lines.append(f"Transition: {transition}.")
    if effects:
        lines.append(f"Effects: {effects}.")

    return " ".join(lines) if lines else "No instructions generated."
