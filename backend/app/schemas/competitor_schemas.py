from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AddCompetitorRequest(BaseModel):
    youtube_channel_url_or_id: str  # Can be full URL or channel ID


class CompetitorResponse(BaseModel):
    id: str
    org_id: str
    youtube_channel_id: str
    channel_name: Optional[str] = None
    channel_avatar_url: Optional[str] = None
    subscriber_count: Optional[int] = None
    video_count: Optional[int] = None
    last_refreshed_at: Optional[datetime] = None
    created_at: datetime


class CompetitorsListResponse(BaseModel):
    competitors: List[CompetitorResponse]


class TopVideoResponse(BaseModel):
    video_id: str
    video_title: str
    video_url: str
    thumbnail_url: Optional[str] = None
    views: int
    likes: Optional[int] = None
    comments: Optional[int] = None
    published_at: Optional[datetime] = None
    outlier_score: Optional[float] = None
    performance_indicator: str  # 'outlier', 'above_average', 'normal'


class TopVideosResponse(BaseModel):
    competitor_id: str
    channel_name: str
    videos: List[TopVideoResponse]
    mock: bool = False
    source: str = "youtube"


class SaveTopicIdeaRequest(BaseModel):
    competitor_id: str
    video_id: str
    video_title: str
    video_url: str
    thumbnail_url: Optional[str] = None
    views: int
    likes: Optional[int] = None
    comments: Optional[int] = None
    published_at: Optional[datetime] = None
    outlier_score: Optional[float] = None
    performance_indicator: str
    notes: Optional[str] = None


class TopicIdeaResponse(BaseModel):
    id: str
    competitor_id: str
    competitor_name: Optional[str] = None
    video_id: str
    video_title: str
    video_url: str
    thumbnail_url: Optional[str] = None
    views: int
    outlier_score: Optional[float] = None
    performance_indicator: str
    notes: Optional[str] = None
    status: str
    created_at: datetime


class TopicIdeasListResponse(BaseModel):
    ideas: List[TopicIdeaResponse]


class UpdateTopicIdeaStatusRequest(BaseModel):
    status: str  # 'saved', 'to_script', 'in_progress', 'ignore'


class SaveTopicIdeaFromExtensionRequest(BaseModel):
    video_id: str
    video_title: str
    video_url: str
    channel_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    views: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    source: str = "extension"


class SaveTopicIdeaFromExtensionResponse(BaseModel):
    id: str
    video_id: str
    video_title: str
    video_url: str
    outlier_score: Optional[float] = None
    competitor_id: Optional[str] = None
    competitor_name: Optional[str] = None
    saved: bool

