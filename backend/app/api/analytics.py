from fastapi import APIRouter, Depends, Query
from app.schemas.analytics_schemas import IngestEvent, SummaryResponse, SummaryPoint, VideosResponse, VideoStat
from app.api.deps import get_current_user, get_current_user_org, get_current_channel
from app.utils.org import resolve_org_id
from app.db.pg import get_conn
from app.services.credentials import get_credentials_for_channel
from app.services.analytics_cache import get_cached, set_cached
from app.providers.youtube_client import get_channel_insights, get_channel_recommendations, get_keyword_analysis, get_channel_trends, get_top_videos
from app.exceptions.live import NoLiveCredentials, LiveProviderError
from app.utils.mock_data import get_mock_daily_summary, get_mock_top_videos
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict
import logging

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])
logger = logging.getLogger(__name__)

@router.post("/ingest")
def ingest(
    evt: IngestEvent,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org)
):
    """Ingest analytics event. Requires authentication and org context."""
    org_id = resolve_org_id(org.get('org_id'))
    # TODO: Store event in database with org_id
    logger.info(f"[INGEST] Event received for org {org_id}")
    return {"ok": True}

@router.get("/summary", response_model=SummaryResponse)
async def summary(
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
    current_channel=Depends(get_current_channel)
):
    """
    [LEGACY] Get daily summary. Uses real auth/org checks. Returns mock data if no YouTube connection.
    
    NOTE: This endpoint appears to be unused by the frontend. Consider removing in favor of
    /api/v1/analytics/channel_snapshot or /api/v1/analytics/trends.
    """
    org_id = resolve_org_id(org.get('org_id'))
    
    # Check if we have a connected channel
    if not current_channel or not current_channel.get("youtube_channel_id"):
        # Return mock data with flag
        data = get_mock_daily_summary()
        return {"points": [SummaryPoint(**d) for d in data], "mock": True, "source": "demo-fixture"}
    
    # Try to get real data, fallback to mock if unavailable
    try:
        creds = await get_credentials_for_channel(str(current_channel["id"]))
        if not creds.get("access_token"):
            raise NoLiveCredentials("No access token available")
        
        # TODO: Fetch real summary data from YouTube API
        # For now, return mock data
        data = get_mock_daily_summary()
        return {"points": [SummaryPoint(**d) for d in data], "mock": True, "source": "demo-fixture"}
    except Exception as e:
        logger.warning(f"[SUMMARY] Failed to fetch real data: {e}, returning mock")
        data = get_mock_daily_summary()
        return {"points": [SummaryPoint(**d) for d in data], "mock": True, "source": "demo-fixture"}

@router.get("/videos", response_model=VideosResponse)
async def videos(
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
    current_channel=Depends(get_current_channel)
):
    """
    [LEGACY] Get top videos. Uses real auth/org checks. Returns mock data if no YouTube connection.
    
    NOTE: This endpoint appears to be unused by the frontend. Use /api/v1/analytics/top_videos instead.
    """
    org_id = resolve_org_id(org.get('org_id'))
    
    # Check if we have a connected channel
    if not current_channel or not current_channel.get("youtube_channel_id"):
        # Return mock data with flag
        data = get_mock_top_videos()
        return {"items": [VideoStat(**d) for d in data], "mock": True, "source": "demo-fixture"}
    
    # Try to get real data, fallback to mock if unavailable
    try:
        creds = await get_credentials_for_channel(str(current_channel["id"]))
        if not creds.get("access_token"):
            raise NoLiveCredentials("No access token available")
        
        # TODO: Fetch real video data from YouTube API
        # For now, return mock data
        data = get_mock_top_videos()
        return {"items": [VideoStat(**d) for d in data], "mock": True, "source": "demo-fixture"}
    except Exception as e:
        logger.warning(f"[VIDEOS] Failed to fetch real data: {e}, returning mock")
        data = get_mock_top_videos()
        return {"items": [VideoStat(**d) for d in data], "mock": True, "source": "demo-fixture"}

@router.get("/channel_snapshot")
async def channel_snapshot(
    days: int = Query(7, ge=7, le=90, description="Number of days (7, 30, or 90)"),
    force_refresh: bool = Query(False, description="Bypass cache and fetch fresh data"),
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
    current_channel=Depends(get_current_channel)
):
    """Get channel snapshot: views, watch_time, avg_ctr, subscribers for specified period."""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"[CHANNEL_SNAPSHOT] user={user}, org={org}, current_channel={current_channel}")
    
    org_id = resolve_org_id(org.get('org_id'))
    
    # Check connection status first
    if not current_channel or not current_channel.get("youtube_channel_id"):
        # Not connected - return demo with clear reason
        logger.warning(f"[CHANNEL_SNAPSHOT] No channel found - user has google_channel_id={user.get('google_channel_id')}")
        return {
            "views_7d": 0,
            "avg_ctr": 0.0,
            "channel_name": "No channel connected",
            "last_sync_at": None,
            "mock": True,
            "source": "demo-fixture",
            "fallback_reason": "YOUTUBE_NOT_CONNECTED"
        }
    
    # Check if we have a token
    has_token = False
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                select refresh_token
                from youtube_tokens
                where channel_id = %s
                limit 1
            """, (current_channel["id"],))
            row = cur.fetchone()
            has_token = bool(row and row.get("refresh_token"))
    except Exception:
        pass
    
    if not has_token:
        # Connected but no token - return demo with reason
        return {
            "views_7d": 0,
            "avg_ctr": 0.0,
            "channel_name": current_channel.get("title", "Channel connected"),
            "last_sync_at": None,
            "mock": True,
            "source": "demo-fixture",
            "fallback_reason": "YOUTUBE_TOKEN_MISSING"
        }
    
    # Try cache first (unless forcing refresh)
    channel_id_str = str(current_channel["id"])
    if not force_refresh:
        cached_data = get_cached(channel_id_str, "channel_snapshot", days=days)
        if cached_data:
            logger.info(f"[CHANNEL_SNAPSHOT] Cache hit for channel {channel_id_str}")
            return cached_data
    
    # Try live data
    try:
        creds = await get_credentials_for_channel(channel_id_str)
        live_data = await get_channel_insights(creds["access_token"], current_channel["youtube_channel_id"], days)
        
        # Get last_sync_at from database
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                select updated_at
                from youtube_channels
                where id = %s
            """, (current_channel["id"],))
            row = cur.fetchone()
            last_sync_at = row.get("updated_at") if row else None
        
        # Build response
        response_data = {
            **live_data,
            "last_sync_at": last_sync_at.isoformat() if last_sync_at else None,
            "mock": False,
            "source": "youtube"
        }
        
        # Cache the response (only if not mock)
        if not response_data.get("mock", False):
            set_cached(channel_id_str, "channel_snapshot", response_data, days=days)
        
        return response_data
    except (NoLiveCredentials, LiveProviderError) as e:
        # Credentials missing or provider error - return demo with reason
        logger.error(f"[CHANNEL_SNAPSHOT] Live data error: {type(e).__name__}: {str(e)}")
        return {
            "views_7d": 0,
            "avg_ctr": 0.0,
            "channel_name": current_channel.get("title", "Channel connected"),
            "last_sync_at": None,
            "mock": True,
            "source": "demo-fixture",
            "fallback_reason": "YOUTUBE_PROVIDER_ERROR"
        }
    except Exception as e:
        # Log error but fall through to demo
        import traceback
        logger.error(f"[CHANNEL_SNAPSHOT] Unexpected error fetching live channel snapshot: {type(e).__name__}: {str(e)}")
        logger.error(f"[CHANNEL_SNAPSHOT] Traceback: {traceback.format_exc()}")
    
    # Check if demo is allowed
    import json
    import os
    allow_demo = True
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config", "data-mode.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = json.load(f)
                allow_demo = config.get("allow_demo", True)
    except Exception:
        pass
    
    if not allow_demo:
        # Demo not allowed - return error instead
        from fastapi import HTTPException
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Live data unavailable",
                "fallback_reason": "YOUTUBE_PROVIDER_ERROR",
                "message": "Live data fetch failed and demo mode is disabled. Check your YouTube connection and token."
            }
        )
    
    # Demo fallback
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                select id, title, updated_at
                from youtube_channels
                where org_id = %s
                order by created_at desc
                limit 1
            """, (org_id,))
            channel = cur.fetchone()
            
            if channel:
                channel_name = channel.get("title", "Unknown Channel")
                last_sync_at = channel.get("updated_at")
                
                # Calculate demo values based on date range
                base_views = {7: 15200, 30: 65000, 90: 185000}
                base_watch_time = {7: 1824000, 30: 7800000, 90: 22200000}
                
                views_period = base_views.get(days, base_views[7])
                views_prev = int(views_period * 0.95)
                watch_time_period = base_watch_time.get(days, base_watch_time[7])
                watch_time_prev = int(watch_time_period * 0.95)
                
                return {
                    "views_7d": views_period,
                    "views_prev_7d": views_prev,
                    "views_change": views_period - views_prev,
                    "views_change_pct": round(((views_period - views_prev) / views_prev * 100) if views_prev > 0 else 0, 1),
                    "watch_time_7d": watch_time_period,
                    "watch_time_prev_7d": watch_time_prev,
                    "watch_time_change": watch_time_period - watch_time_prev,
                    "watch_time_change_pct": round(((watch_time_period - watch_time_prev) / watch_time_prev * 100) if watch_time_prev > 0 else 0, 1),
                    "avg_ctr": 4.8,
                    "avg_ctr_prev": 4.5,
                    "ctr_change": 0.3,
                    "subscribers_net": 45 if days == 7 else (180 if days == 30 else 540),
                    "subscribers_prev_net": 42 if days == 7 else (170 if days == 30 else 510),
                    "subscribers_change": 3 if days == 7 else (10 if days == 30 else 30),
                    "subscribers_change_pct": 7.1,
                    "channel_name": channel_name,
                    "total_subscribers": 1250,
                    "total_views": 456000,
                    "total_videos": 87,
                    "last_sync_at": last_sync_at.isoformat() if last_sync_at else None,
                    "mock": True,
                    "source": "demo-fixture",
                    "period_days": days
                }
    except Exception:
        pass
    
    # Final demo fallback
    base_views = {7: 15200, 30: 65000, 90: 185000}
    base_watch_time = {7: 1824000, 30: 7800000, 90: 22200000}
    
    views_period = base_views.get(days, base_views[7])
    views_prev = int(views_period * 0.95)
    watch_time_period = base_watch_time.get(days, base_watch_time[7])
    watch_time_prev = int(watch_time_period * 0.95)
    
    return {
        "views_7d": views_period,
        "views_prev_7d": views_prev,
        "views_change": views_period - views_prev,
        "views_change_pct": round(((views_period - views_prev) / views_prev * 100) if views_prev > 0 else 0, 1),
        "watch_time_7d": watch_time_period,
        "watch_time_prev_7d": watch_time_prev,
        "watch_time_change": watch_time_period - watch_time_prev,
        "watch_time_change_pct": round(((watch_time_period - watch_time_prev) / watch_time_prev * 100) if watch_time_prev > 0 else 0, 1),
        "avg_ctr": 4.8,
        "avg_ctr_prev": 4.5,
        "ctr_change": 0.3,
        "subscribers_net": 45 if days == 7 else (180 if days == 30 else 540),
        "subscribers_prev_net": 42 if days == 7 else (170 if days == 30 else 510),
        "subscribers_change": 3 if days == 7 else (10 if days == 30 else 30),
        "subscribers_change_pct": 7.1,
        "channel_name": "Demo Channel",
        "total_subscribers": 1250,
        "total_views": 456000,
        "total_videos": 87,
        "last_sync_at": datetime.now(timezone.utc).isoformat(),
        "mock": True,
        "source": "demo-fixture",
        "period_days": days
    }

@router.get("/keywords")
async def keywords(
    q: str = Query(..., description="Search term"), 
    force_refresh: bool = Query(False, description="Bypass cache and fetch fresh data"),
    user=Depends(get_current_user), 
    org=Depends(get_current_user_org), 
    current_channel=Depends(get_current_channel)
):
    """Get keyword analysis: reach_score, competition_level, suggested_length."""
    # Check connection status first
    if not current_channel or not current_channel.get("youtube_channel_id"):
        # Not connected - return demo with reason
        reach_score = min(100, max(20, len(q) * 8 + 30))
        competition_level = "medium" if reach_score < 70 else "high"
        return {
            "term": q,
            "reach_score": reach_score,
            "competition_level": competition_level,
            "suggested_length": max(60, min(100, 70 + len(q) * 2)),
            "mock": True,
            "source": "demo-fixture",
            "fallback_reason": "YOUTUBE_NOT_CONNECTED"
        }
    
    # Try cache first (unless forcing refresh)
    channel_id_str = str(current_channel["id"])
    if not force_refresh:
        cached_data = get_cached(channel_id_str, "keywords", q=q)
        if cached_data:
            logger.info(f"[KEYWORDS] Cache hit for channel {channel_id_str}, query: {q}")
            return cached_data
    
    # Try live data
    try:
        creds = await get_credentials_for_channel(channel_id_str)
        live_data = await get_keyword_analysis(creds["access_token"], q)
        
        response_data = {
            "term": live_data.get("term", q),
            "reach_score": live_data.get("reach_score", 50),
            "competition_level": live_data.get("competition_level", "medium"),
            "suggested_length": live_data.get("suggested_length", 70),
            "mock": False,
            "source": "youtube"
        }
        
        # Cache the response
        set_cached(channel_id_str, "keywords", response_data, q=q)
        
        return response_data
    except (NoLiveCredentials, LiveProviderError):
        # Fall through to demo with reason
        pass
    except Exception as e:
        logger.warning(f"[KEYWORDS] Error fetching live keyword analysis: {e}")
    
    # Demo fallback
    reach_score = min(100, max(20, len(q) * 8 + 30))
    competition_level = "medium" if reach_score < 70 else "high"
    
    fallback_data = {
        "term": q,
        "reach_score": reach_score,
        "competition_level": competition_level,
        "suggested_length": max(60, min(100, 70 + len(q) * 2)),
        "mock": True,
        "source": "demo-fixture",
        "fallback_reason": "YOUTUBE_PROVIDER_ERROR"
    }
    
    # Cache fallback data too (with shorter TTL)
    set_cached(channel_id_str, "keywords", fallback_data, q=q)
    
    return fallback_data

@router.get("/trends")
async def trends(
    days: int = Query(7, ge=7, le=90, description="Number of days (7, 30, or 90)"),
    force_refresh: bool = Query(False, description="Bypass cache and fetch fresh data"),
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
    current_channel=Depends(get_current_channel)
):
    """Get daily trend data for views and CTR over specified period."""
    logger = logging.getLogger(__name__)
    
    if not current_channel or not current_channel.get("youtube_channel_id"):
        # Return demo trends
        from datetime import datetime, timedelta
        demo_trends = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=days - i - 1)).strftime("%Y-%m-%d")
            demo_trends.append({
                "date": date,
                "views": 200 + (i % 3) * 50,
                "ctr": 4.0 + (i % 5) * 0.3,
            })
        return {
            "mock": True,
            "source": "demo-fixture",
            "fallback_reason": "YOUTUBE_NOT_CONNECTED",
            "data": demo_trends
        }
    
    # Try cache first (unless forcing refresh)
    channel_id_str = str(current_channel["id"])
    if not force_refresh:
        cached_data = get_cached(channel_id_str, "trends", days=days)
        if cached_data:
            logger.info(f"[TRENDS] Cache hit for channel {channel_id_str}")
            return cached_data
    
    try:
        creds = await get_credentials_for_channel(channel_id_str)
        trend_data = await get_channel_trends(creds["access_token"], current_channel["youtube_channel_id"], days)
        
        response_data = {
            "mock": False,
            "source": "youtube",
            "data": trend_data
        }
        
        # Cache the response
        set_cached(channel_id_str, "trends", response_data, days=days)
        
        return response_data
    except (NoLiveCredentials, LiveProviderError) as e:
        logger.error(f"[TRENDS] Error: {e}")
        # Return demo trends
        from datetime import datetime, timedelta
        demo_trends = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=days - i - 1)).strftime("%Y-%m-%d")
            demo_trends.append({
                "date": date,
                "views": 200 + (i % 3) * 50,
                "ctr": 4.0 + (i % 5) * 0.3,
            })
        return {
            "mock": True,
            "source": "demo-fixture",
            "fallback_reason": "YOUTUBE_PROVIDER_ERROR",
            "data": demo_trends
        }


@router.get("/top_videos")
async def top_videos(
    limit: int = Query(5, ge=1, le=10, description="Number of videos to return"),
    force_refresh: bool = Query(False, description="Bypass cache and fetch fresh data"),
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
    current_channel=Depends(get_current_channel)
):
    """Get top videos by performance."""
    logger = logging.getLogger(__name__)
    
    if not current_channel or not current_channel.get("youtube_channel_id"):
        # Return demo videos
        demo_videos = [
            {
                "video_id": "demo_video_1",
                "title": "Top Performing Video - F1 Race Highlights",
                "thumbnail_url": "https://via.placeholder.com/160x90?text=Video+1",
                "views": 125000,
                "ctr": 5.8,
                "likes": 7200,
                "comments": 450,
                "outlier_score": 87.5,
                "youtube_url": "https://www.youtube.com/watch?v=demo_video_1",
                "performance_indicator": "above_average"
            },
            {
                "video_id": "demo_video_2",
                "title": "Second Best - Qualifying Analysis",
                "thumbnail_url": "https://via.placeholder.com/160x90?text=Video+2",
                "views": 98000,
                "ctr": 4.9,
                "likes": 5800,
                "comments": 320,
                "outlier_score": 72.3,
                "youtube_url": "https://www.youtube.com/watch?v=demo_video_2",
                "performance_indicator": "above_average"
            },
            {
                "video_id": "demo_video_3",
                "title": "Third Place - Driver Interview",
                "thumbnail_url": "https://via.placeholder.com/160x90?text=Video+3",
                "views": 67000,
                "ctr": 4.2,
                "likes": 3500,
                "comments": 180,
                "outlier_score": 58.1,
                "youtube_url": "https://www.youtube.com/watch?v=demo_video_3",
                "performance_indicator": "needs_work"
            },
            {
                "video_id": "demo_video_4",
                "title": "Race Recap - Post-Race Discussion",
                "thumbnail_url": "https://via.placeholder.com/160x90?text=Video+4",
                "views": 45000,
                "ctr": 3.8,
                "likes": 2100,
                "comments": 95,
                "outlier_score": 45.2,
                "youtube_url": "https://www.youtube.com/watch?v=demo_video_4",
                "performance_indicator": "needs_work"
            },
            {
                "video_id": "demo_video_5",
                "title": "Behind the Scenes - Pit Lane Tour",
                "thumbnail_url": "https://via.placeholder.com/160x90?text=Video+5",
                "views": 32000,
                "ctr": 3.5,
                "likes": 1500,
                "comments": 67,
                "outlier_score": 38.7,
                "youtube_url": "https://www.youtube.com/watch?v=demo_video_5",
                "performance_indicator": "needs_work"
            }
        ]
        return {
            "mock": True,
            "source": "demo-fixture",
            "fallback_reason": "YOUTUBE_NOT_CONNECTED",
            "data": demo_videos
        }
    
    # Try cache first (unless forcing refresh)
    channel_id_str = str(current_channel["id"])
    if not force_refresh:
        cached_data = get_cached(channel_id_str, "top_videos", limit=limit)
        if cached_data:
            logger.info(f"[TOP_VIDEOS] Cache hit for channel {channel_id_str}")
            return cached_data
    
    try:
        creds = await get_credentials_for_channel(channel_id_str)
        videos = await get_top_videos(creds["access_token"], current_channel["youtube_channel_id"], limit)
        
        response_data = {
            "mock": False,
            "source": "youtube",
            "data": videos
        }
        
        # Cache the response
        set_cached(channel_id_str, "top_videos", response_data, limit=limit)
        
        return response_data
    except (NoLiveCredentials, LiveProviderError) as e:
        logger.error(f"[TOP_VIDEOS] Error: {e}")
        import traceback
        logger.error(f"[TOP_VIDEOS] Traceback: {traceback.format_exc()}")
        # Return demo videos with outlier scores
        demo_videos = [
            {
                "video_id": "demo_video_1",
                "title": "Top Performing Video - F1 Race Highlights",
                "thumbnail_url": "https://via.placeholder.com/160x90?text=Video+1",
                "views": 125000,
                "ctr": 5.8,
                "likes": 7200,
                "comments": 450,
                "outlier_score": 87.5,
                "youtube_url": "https://www.youtube.com/watch?v=demo_video_1",
                "performance_indicator": "above_average"
            },
            {
                "video_id": "demo_video_2",
                "title": "Second Best - Qualifying Analysis",
                "thumbnail_url": "https://via.placeholder.com/160x90?text=Video+2",
                "views": 98000,
                "ctr": 4.9,
                "likes": 5800,
                "comments": 320,
                "outlier_score": 72.3,
                "youtube_url": "https://www.youtube.com/watch?v=demo_video_2",
                "performance_indicator": "above_average"
            },
            {
                "video_id": "demo_video_3",
                "title": "Third Place - Driver Interview",
                "thumbnail_url": "https://via.placeholder.com/160x90?text=Video+3",
                "views": 67000,
                "ctr": 4.2,
                "likes": 3500,
                "comments": 180,
                "outlier_score": 58.1,
                "youtube_url": "https://www.youtube.com/watch?v=demo_video_3",
                "performance_indicator": "needs_work"
            },
            {
                "video_id": "demo_video_4",
                "title": "Race Recap - Post-Race Discussion",
                "thumbnail_url": "https://via.placeholder.com/160x90?text=Video+4",
                "views": 45000,
                "ctr": 3.8,
                "likes": 2100,
                "comments": 95,
                "outlier_score": 45.2,
                "youtube_url": "https://www.youtube.com/watch?v=demo_video_4",
                "performance_indicator": "needs_work"
            },
            {
                "video_id": "demo_video_5",
                "title": "Behind the Scenes - Pit Lane Tour",
                "thumbnail_url": "https://via.placeholder.com/160x90?text=Video+5",
                "views": 32000,
                "ctr": 3.5,
                "likes": 1500,
                "comments": 67,
                "outlier_score": 38.7,
                "youtube_url": "https://www.youtube.com/watch?v=demo_video_5",
                "performance_indicator": "needs_work"
            }
        ]
        return {
            "mock": True,
            "source": "demo-fixture",
            "fallback_reason": "YOUTUBE_PROVIDER_ERROR",
            "data": demo_videos
        }
    except Exception as e:
        logger.error(f"[TOP_VIDEOS] Unexpected error: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"[TOP_VIDEOS] Traceback: {traceback.format_exc()}")
        # Return demo videos as fallback
        demo_videos = [
            {
                "video_id": "demo_video_1",
                "title": "Top Performing Video - F1 Race Highlights",
                "thumbnail_url": "https://via.placeholder.com/160x90?text=Video+1",
                "views": 125000,
                "ctr": 5.8,
                "likes": 7200,
                "comments": 450,
                "outlier_score": 87.5,
                "youtube_url": "https://www.youtube.com/watch?v=demo_video_1",
                "performance_indicator": "above_average"
            },
            {
                "video_id": "demo_video_2",
                "title": "Second Best - Qualifying Analysis",
                "thumbnail_url": "https://via.placeholder.com/160x90?text=Video+2",
                "views": 98000,
                "ctr": 4.9,
                "likes": 5800,
                "comments": 320,
                "outlier_score": 72.3,
                "youtube_url": "https://www.youtube.com/watch?v=demo_video_2",
                "performance_indicator": "above_average"
            },
            {
                "video_id": "demo_video_3",
                "title": "Third Place - Driver Interview",
                "thumbnail_url": "https://via.placeholder.com/160x90?text=Video+3",
                "views": 67000,
                "ctr": 4.2,
                "likes": 3500,
                "comments": 180,
                "outlier_score": 58.1,
                "youtube_url": "https://www.youtube.com/watch?v=demo_video_3",
                "performance_indicator": "needs_work"
            },
            {
                "video_id": "demo_video_4",
                "title": "Race Recap - Post-Race Discussion",
                "thumbnail_url": "https://via.placeholder.com/160x90?text=Video+4",
                "views": 45000,
                "ctr": 3.8,
                "likes": 2100,
                "comments": 95,
                "outlier_score": 45.2,
                "youtube_url": "https://www.youtube.com/watch?v=demo_video_4",
                "performance_indicator": "needs_work"
            },
            {
                "video_id": "demo_video_5",
                "title": "Behind the Scenes - Pit Lane Tour",
                "thumbnail_url": "https://via.placeholder.com/160x90?text=Video+5",
                "views": 32000,
                "ctr": 3.5,
                "likes": 1500,
                "comments": 67,
                "outlier_score": 38.7,
                "youtube_url": "https://www.youtube.com/watch?v=demo_video_5",
                "performance_indicator": "needs_work"
            }
        ]
        return {
            "mock": True,
            "source": "demo-fixture",
            "fallback_reason": "YOUTUBE_PROVIDER_ERROR",
            "data": demo_videos
        }


@router.get("/ai_insights")
async def ai_insights(
    force_refresh: bool = Query(False, description="Bypass cache and fetch fresh data"),
    user=Depends(get_current_user),
    org=Depends(get_current_user_org),
    current_channel=Depends(get_current_channel)
):
    """Generate AI insights using Gemini based on channel analytics."""
    logger = logging.getLogger(__name__)
    
    if not current_channel or not current_channel.get("youtube_channel_id"):
        return {
            "mock": True,
            "source": "demo-fixture",
            "fallback_reason": "YOUTUBE_NOT_CONNECTED",
            "insights": [],
            "generated_at": None
        }
    
    # Try cache first (unless forcing refresh)
    channel_id_str = str(current_channel["id"])
    if not force_refresh:
        cached_data = get_cached(channel_id_str, "ai_insights")
        if cached_data:
            logger.info(f"[AI_INSIGHTS] Cache hit for channel {channel_id_str}")
            return cached_data
    
    try:
        # Get channel snapshot for context
        creds = await get_credentials_for_channel(channel_id_str)
        insights_data = await get_channel_insights(creds["access_token"], current_channel["youtube_channel_id"])
        
        # Generate insights using Gemini
        try:
            from app.services.seo_service import call_gemini
            from app.utils.org import resolve_org_id
            
            org_id = resolve_org_id(org.get('org_id'))
            
            prompt = f"""Analyze this YouTube channel analytics data and provide 2-3 concise insights in plain English (one per line with a dash).

Channel: {insights_data.get('channel_name', 'Unknown')}
Subscribers: {insights_data.get('total_subscribers', 0):,}
Total Videos: {insights_data.get('total_videos', 0)}
7-Day Views: {insights_data.get('views_7d', 0):,}
Views Change: {insights_data.get('views_change_pct', 0)}%
CTR: {insights_data.get('avg_ctr', 0)}%
CTR Change: {insights_data.get('ctr_change', 0)}%

Provide insights focusing on performance trends, opportunities, or actionable recommendations. Keep each insight under 100 characters."""

            insights_text = await call_gemini(prompt, temperature=0.7)
            
            # Parse insights into bullet points
            insights_list = [line.strip().replace("-", "").replace("•", "").strip() 
                           for line in insights_text.split("\n") 
                           if line.strip() and (line.strip().startswith("-") or line.strip().startswith("•") or len(line.strip()) > 10)]
            
            if not insights_list:
                # Fallback: generate simple insights from data
                insights_list = [
                    f"Your channel has {insights_data.get('total_subscribers', 0):,} subscribers and {insights_data.get('total_videos', 0)} videos.",
                    f"Views are {'up' if insights_data.get('views_change_pct', 0) > 0 else 'down'} {abs(insights_data.get('views_change_pct', 0))}% compared to last week.",
                    f"CTR is {insights_data.get('avg_ctr', 0)}% — {'above' if insights_data.get('avg_ctr', 0) >= 4.0 else 'below'} industry average."
                ]
        except Exception as gemini_error:
            logger.warning(f"[AI_INSIGHTS] Gemini error, using fallback: {gemini_error}")
            # Fallback insights
            insights_list = [
                f"Your channel has {insights_data.get('total_subscribers', 0):,} subscribers.",
                f"Views changed {insights_data.get('views_change_pct', 0)}% vs last week.",
                f"CTR is {insights_data.get('avg_ctr', 0)}%."
            ]
        
        response_data = {
            "mock": False,
            "source": "gemini",
            "insights": insights_list[:3],  # Max 3 insights
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Cache the response
        set_cached(channel_id_str, "ai_insights", response_data)
        
        return response_data
    except Exception as e:
        logger.error(f"[AI_INSIGHTS] Error: {e}")
        # Return demo insights
        fallback_data = {
            "mock": True,
            "source": "demo-fixture",
            "fallback_reason": "GEMINI_ERROR",
            "insights": [
                "Your CTR is performing well compared to industry averages.",
                "Consider experimenting with thumbnail styles to boost views.",
                "Subscriber growth is steady—maintain your upload schedule."
            ],
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Cache fallback data too
        set_cached(channel_id_str, "ai_insights", fallback_data)
        
        return fallback_data


@router.get("/recommendations")
async def recommendations(
    force_refresh: bool = Query(False, description="Bypass cache and fetch fresh data"),
    user=Depends(get_current_user), 
    org=Depends(get_current_user_org), 
    current_channel=Depends(get_current_channel)
):
    """Get AI recommendations: [{ id, type, text, action_uri }]."""
    # Check connection status first
    if not current_channel or not current_channel.get("youtube_channel_id"):
        # Not connected - return demo with reason
        demo_recs = [
            {
                "id": "r1",
                "type": "optimization",
                "text": "Your CTR is 15% below average. Consider A/B testing thumbnails.",
                "action_uri": "/app/optimization"
            },
            {
                "id": "r2",
                "type": "content",
                "text": "F1 qualifying topics are trending. Create a video this week.",
                "action_uri": "/app/research"
            }
        ]
        return {
            "mock": True,
            "source": "demo-fixture",
            "fallback_reason": "YOUTUBE_NOT_CONNECTED",
            "data": demo_recs
        }
    
    # Try cache first (unless forcing refresh)
    channel_id_str = str(current_channel["id"])
    if not force_refresh:
        cached_data = get_cached(channel_id_str, "recommendations")
        if cached_data:
            logger.info(f"[RECOMMENDATIONS] Cache hit for channel {channel_id_str}")
            return cached_data
    
    # Try live data
    try:
        creds = await get_credentials_for_channel(channel_id_str)
        live_recs = await get_channel_recommendations(creds["access_token"], current_channel["youtube_channel_id"])
        
        if live_recs:
            response_data = {
                "mock": False,
                "source": "youtube",
                "data": live_recs
            }
            
            # Cache the response
            set_cached(channel_id_str, "recommendations", response_data)
            
            return response_data
    except (NoLiveCredentials, LiveProviderError):
        # Fall through to demo with reason
        pass
    except Exception as e:
        logger.warning(f"[RECOMMENDATIONS] Error fetching live recommendations: {e}")
    
    # Demo fallback
    demo_recs = [
        {
            "id": "r1",
            "type": "optimization",
            "text": "Your CTR is 15% below average. Consider A/B testing thumbnails.",
            "action_uri": "/app/optimization"
        },
        {
            "id": "r2",
            "type": "content",
            "text": "F1 qualifying topics are trending. Create a video this week.",
            "action_uri": "/app/research"
        }
    ]
    
    fallback_data = {
        "mock": True,
        "source": "demo-fixture",
        "fallback_reason": "YOUTUBE_PROVIDER_ERROR",
        "data": demo_recs
    }
    
    # Cache fallback data too
    set_cached(channel_id_str, "recommendations", fallback_data)
    
    return fallback_data

