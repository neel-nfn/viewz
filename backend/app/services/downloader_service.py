from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any


DOWNLOADER_MODE = os.getenv("VIEWZ_DOWNLOADER_MODE", "real").strip().lower()


def _validate_range(start_time: float, end_time: float) -> float:
    start = float(start_time)
    end = float(end_time)
    duration = end - start
    if start < 0:
        raise ValueError("start_time must be >= 0")
    if end <= start:
        raise ValueError("end_time must be greater than start_time")
    if duration <= 0:
        raise ValueError("Clip duration must be positive")
    if duration > 60 * 60:
        raise ValueError("Clip duration is too long")
    return duration


def _ensure_tool(name: str) -> str:
    resolved = shutil.which(name)
    if not resolved:
        raise RuntimeError(f"Required tool not found: {name}")
    return resolved


def _stub_download(source_url: str, start_time: float, end_time: float) -> str:
    temp_dir = Path(tempfile.mkdtemp(prefix="viewz-downloader-stub-"))
    output_path = temp_dir / f"clip-{uuid.uuid4().hex}.mp4"
    payload = {
        "mode": "stub",
        "source_url": source_url,
        "start_time": start_time,
        "end_time": end_time,
        "duration": end_time - start_time,
    }
    output_path.write_bytes(json.dumps(payload, sort_keys=True).encode("utf-8"))
    return str(output_path)


def _download_with_yt_dlp(source_url: str, working_dir: Path) -> Path:
    yt_dlp = _ensure_tool("yt-dlp")
    download_template = str(working_dir / "source.%(ext)s")
    cmd = [
        yt_dlp,
        "--no-playlist",
        "--format",
        "bv*+ba/b",
        "--merge-output-format",
        "mp4",
        "-o",
        download_template,
        source_url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp failed: {result.stderr.strip() or result.stdout.strip()}")

    matches = sorted(working_dir.glob("source.*"))
    if not matches:
        raise RuntimeError("yt-dlp did not produce a source file")
    return matches[0]


def _extract_with_ffmpeg(source_path: Path, output_path: Path, start_time: float, duration: float) -> None:
    ffmpeg = _ensure_tool("ffmpeg")
    cmd = [
        ffmpeg,
        "-y",
        "-ss",
        str(start_time),
        "-i",
        str(source_path),
        "-t",
        str(duration),
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr.strip() or result.stdout.strip()}")
    if not output_path.exists() or output_path.stat().st_size <= 0:
        raise RuntimeError("ffmpeg did not produce an output file")


def download_and_extract(source_url: str, start_time: float, end_time: float) -> str:
    _validate_range(start_time, end_time)
    if not source_url:
        raise ValueError("source_url is required")

    if DOWNLOADER_MODE == "stub":
        return _stub_download(source_url, start_time, end_time)

    working_dir = Path(tempfile.mkdtemp(prefix="viewz-downloader-"))
    output_path = working_dir / f"clip-{uuid.uuid4().hex}.mp4"

    if source_url.startswith("file://"):
        source_path = Path(source_url.removeprefix("file://"))
        if not source_path.exists():
            raise RuntimeError(f"Local source path does not exist: {source_path}")
    else:
        candidate_path = Path(source_url)
        if candidate_path.exists():
            source_path = candidate_path
        else:
            source_path = _download_with_yt_dlp(source_url, working_dir)

    _extract_with_ffmpeg(source_path, output_path, float(start_time), float(end_time) - float(start_time))
    return str(output_path)
