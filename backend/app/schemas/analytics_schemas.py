from pydantic import BaseModel
from typing import Any, List, Optional

class IngestEvent(BaseModel):
    event_type: str
    metadata: Optional[dict] = {}

class SummaryPoint(BaseModel):
    date: str
    views: int
    watch_time: int

class SummaryResponse(BaseModel):
    points: List[SummaryPoint]

class VideoStat(BaseModel):
    title: str
    ctr: float

class VideosResponse(BaseModel):
    items: List[VideoStat]

