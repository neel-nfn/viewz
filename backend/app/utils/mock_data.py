"""
Centralized mock/demo data for development and fallback scenarios.
Use this instead of scattered mock data throughout the codebase.
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone


def get_mock_daily_summary() -> List[Dict[str, Any]]:
    """Mock daily summary data for analytics summary endpoint."""
    base_date = datetime.now(timezone.utc) - timedelta(days=7)
    return [
        {"date": (base_date + timedelta(days=i)).strftime("%Y-%m-%d"), "views": 1200 + i * 100, "watch_time": 800 + i * 50}
        for i in range(7)
    ]


def get_mock_top_videos() -> List[Dict[str, Any]]:
    """Mock top videos data for analytics videos endpoint."""
    return [
        {"title": "Race Recap", "ctr": 6.1},
        {"title": "Pit Stop Secrets", "ctr": 5.4},
        {"title": "Setup Myths", "ctr": 4.9},
        {"title": "Quali Drama", "ctr": 4.7},
        {"title": "Undercut 101", "ctr": 4.6}
    ]


def get_mock_tasks() -> List[Dict[str, Any]]:
    """Mock tasks for tasks/today endpoint."""
    return [
        {"id": "t1", "title": "Review script for F1 Recap", "status": "pending"},
        {"id": "t2", "title": "Upload thumbnail variations", "status": "in_progress"},
        {"id": "t3", "title": "Schedule next video", "status": "completed"}
    ]


def get_mock_channel_snapshot() -> Dict[str, Any]:
    """Mock channel snapshot data."""
    return {
        "views_7d": 0,
        "avg_ctr": 0.0,
        "channel_name": "No channel connected",
        "last_sync_at": None,
        "mock": True,
        "source": "demo-fixture",
        "fallback_reason": "YOUTUBE_NOT_CONNECTED"
    }

