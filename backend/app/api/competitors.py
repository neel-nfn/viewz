from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas.competitor_schemas import (
    AddCompetitorRequest, CompetitorResponse, CompetitorsListResponse,
    TopVideosResponse, TopVideoResponse,
    SaveTopicIdeaRequest, TopicIdeaResponse, TopicIdeasListResponse,
    UpdateTopicIdeaStatusRequest,
    SaveTopicIdeaFromExtensionRequest, SaveTopicIdeaFromExtensionResponse
)
from app.api.deps import get_current_user, get_current_user_org
from app.db.pg import get_conn
from app.utils.org import resolve_org_id
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
import re
import logging

router = APIRouter(prefix="/api/v1/competitors", tags=["competitors"])
logger = logging.getLogger(__name__)


def extract_channel_id(url_or_id: str) -> str:
    """Extract YouTube channel ID from URL or return ID if already in correct format"""
    # If it's already a channel ID (starts with UC and is 24 chars)
    if url_or_id.startswith("UC") and len(url_or_id) == 24:
        return url_or_id
    
    # Try to extract from various YouTube URL formats
    patterns = [
        r"youtube\.com/channel/(UC[\w-]{22})",
        r"youtube\.com/c/([\w-]+)",
        r"youtube\.com/@([\w-]+)",
        r"youtube\.com/user/([\w-]+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            # For channel/ URLs, return the ID directly
            if "channel/" in pattern:
                return match.group(1)
            # For other formats, we'd need to use YouTube API to resolve
            # For now, return the handle/username
            return match.group(1)
    
    # If nothing matches, return as-is and let YouTube API handle it
    return url_or_id


@router.post("/add", response_model=CompetitorResponse)
async def add_competitor(
    payload: AddCompetitorRequest,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org)
):
    """Add a competitor channel"""
    org_id = resolve_org_id(org.get('org_id'))
    user_id = user.get("user_id") or user.get("sub") or "unknown"
    
    # Extract channel ID from URL
    youtube_channel_id = extract_channel_id(payload.youtube_channel_url_or_id)
    
    # TODO: Fetch channel details from YouTube API
    # For now, use mock data
    channel_name = f"Channel {youtube_channel_id[:8]}"
    channel_avatar_url = None
    subscriber_count = 0
    video_count = 0
    
    try:
        with get_conn() as conn, conn.cursor() as cur:
            # Check if competitor already exists
            cur.execute("""
                SELECT id, channel_name, channel_avatar_url, subscriber_count, video_count, 
                       last_refreshed_at, created_at
                FROM competitors
                WHERE org_id = %s AND youtube_channel_id = %s
            """, (org_id, youtube_channel_id))
            
            existing = cur.fetchone()
            if existing:
                return CompetitorResponse(
                    id=str(existing["id"]),
                    org_id=org_id,
                    youtube_channel_id=youtube_channel_id,
                    channel_name=existing["channel_name"],
                    channel_avatar_url=existing["channel_avatar_url"],
                    subscriber_count=existing["subscriber_count"],
                    video_count=existing["video_count"],
                    last_refreshed_at=existing["last_refreshed_at"],
                    created_at=existing["created_at"]
                )
            
            # Insert new competitor
            cur.execute("""
                INSERT INTO competitors 
                (org_id, youtube_channel_id, channel_name, channel_avatar_url, 
                 subscriber_count, video_count, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, created_at
            """, (org_id, youtube_channel_id, channel_name, channel_avatar_url,
                  subscriber_count, video_count, user_id))
            
            result = cur.fetchone()
            conn.commit()
            
            return CompetitorResponse(
                id=str(result["id"]),
                org_id=org_id,
                youtube_channel_id=youtube_channel_id,
                channel_name=channel_name,
                channel_avatar_url=channel_avatar_url,
                subscriber_count=subscriber_count,
                video_count=video_count,
                last_refreshed_at=None,
                created_at=result["created_at"]
            )
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error adding competitor: {error_msg}")
        
        # Check if it's a table doesn't exist error
        if "does not exist" in error_msg.lower() or "relation" in error_msg.lower():
            raise HTTPException(
                status_code=500,
                detail="Database migration required. Please run the migration: backend/migrations/020_competitors.sql"
            )
        
        raise HTTPException(status_code=500, detail=f"Database error: {error_msg}")


@router.get("/list", response_model=CompetitorsListResponse)
async def list_competitors(
    user=Depends(get_current_user),
    org=Depends(get_current_user_org)
):
    """List all competitors for the org"""
    org_id = resolve_org_id(org.get('org_id'))
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                # Check if table exists (try both lowercase and check for any case variations)
                try:
                    cur.execute("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND LOWER(table_name) = 'competitors'
                    """)
                    table_result = cur.fetchone()
                    table_exists = table_result is not None
                    
                    if not table_exists:
                        # Also check for competitor_topic_ideas to see if migration partially ran
                        cur.execute("""
                            SELECT table_name 
                            FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND LOWER(table_name) IN ('competitors', 'competitor_topic_ideas')
                        """)
                        existing_tables = [row[0] for row in cur.fetchall()]
                        logger.error(f"competitors table does not exist. Found tables: {existing_tables}")
                        raise HTTPException(
                            status_code=500,
                            detail=f"Competitors table not found. Found: {existing_tables}. Please run migration 020_competitors.sql"
                        )
                except HTTPException:
                    raise
                except Exception as check_error:
                    logger.error(f"Error checking table existence: {check_error}", exc_info=True)
                    # Continue with query - if table doesn't exist, the query will fail with a clearer error
                
                cur.execute("""
                    SELECT id, org_id, youtube_channel_id, channel_name, channel_avatar_url,
                           subscriber_count, video_count, last_refreshed_at, created_at
                    FROM competitors
                    WHERE org_id = %s
                    ORDER BY created_at DESC
                """, (org_id,))
                
                rows = cur.fetchall()
                competitors = []
                for row in rows:
                    try:
                        competitors.append(CompetitorResponse(
                            id=str(row["id"]),
                            org_id=str(row["org_id"]),
                            youtube_channel_id=row["youtube_channel_id"],
                            channel_name=row.get("channel_name"),
                            channel_avatar_url=row.get("channel_avatar_url"),
                            subscriber_count=row.get("subscriber_count") or 0,
                            video_count=row.get("video_count") or 0,
                            last_refreshed_at=row.get("last_refreshed_at"),
                            created_at=row["created_at"]
                        ))
                    except Exception as card_error:
                        logger.error(f"Error creating CompetitorResponse from row: {card_error}, row: {row}")
                        raise
                
                return CompetitorsListResponse(competitors=competitors)
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error listing competitors: {error_msg}", exc_info=True)
        
        # Check if it's a table doesn't exist error
        if "does not exist" in error_msg.lower() or "relation" in error_msg.lower():
            raise HTTPException(
                status_code=500,
                detail="Database migration required. Please run the migration: backend/migrations/020_competitors.sql"
            )
        
        raise HTTPException(status_code=500, detail=f"Failed to list competitors: {error_msg}")


@router.delete("/{competitor_id}")
async def delete_competitor(
    competitor_id: str,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org)
):
    """Delete a competitor"""
    org_id = resolve_org_id(org.get('org_id'))
    
    try:
        with get_conn() as conn, conn.cursor() as cur:
            # Verify ownership and delete
            cur.execute("""
                DELETE FROM competitors
                WHERE id = %s AND org_id = %s
                RETURNING id
            """, (competitor_id, org_id))
            
            result = cur.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Competitor not found")
            
            conn.commit()
            return {"ok": True, "id": competitor_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting competitor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{competitor_id}/videos", response_model=TopVideosResponse)
async def get_competitor_videos(
    competitor_id: str,
    days: int = Query(30, ge=7, le=90, description="Time range in days"),
    user=Depends(get_current_user),
    org=Depends(get_current_user_org)
):
    """Get top-performing videos for a competitor"""
    org_id = resolve_org_id(org.get('org_id'))
    
    try:
        with get_conn() as conn, conn.cursor() as cur:
            # Get competitor details
            cur.execute("""
                SELECT youtube_channel_id, channel_name
                FROM competitors
                WHERE id = %s AND org_id = %s
            """, (competitor_id, org_id))
            
            competitor = cur.fetchone()
            if not competitor:
                raise HTTPException(status_code=404, detail="Competitor not found")
            
            competitor_channel_id = competitor["youtube_channel_id"]
            
            # Try to get OAuth token from any connected channel in the org
            # This allows us to fetch public competitor data using YouTube API
            access_token = None
            try:
                from app.services.credentials import get_credentials_for_channel
                # Get any channel from this org that has OAuth credentials
                cur.execute("""
                    SELECT c.id, c.youtube_channel_id
                    FROM youtube_channels c
                    JOIN youtube_tokens t ON t.channel_id = c.id
                    WHERE c.org_id = %s AND t.refresh_token IS NOT NULL
                    LIMIT 1
                """, (org_id,))
                
                org_channel = cur.fetchone()
                if org_channel:
                    creds = await get_credentials_for_channel(str(org_channel["id"]))
                    access_token = creds.get("access_token")
            except Exception as e:
                logger.warning(f"Could not get OAuth token for competitor videos: {e}")
                access_token = None
            
            # Fetch real videos from YouTube API if we have a token
            if access_token:
                try:
                    from app.providers.youtube_client import get_competitor_videos as fetch_competitor_videos
                    from app.exceptions.live import LiveProviderError
                    
                    youtube_videos = await fetch_competitor_videos(
                        access_token=access_token,
                        competitor_channel_id=competitor_channel_id,
                        days=days
                    )
                    
                    # Map YouTube API response to TopVideoResponse format
                    videos = []
                    for vid in youtube_videos:
                        videos.append(TopVideoResponse(
                            video_id=vid["video_id"],
                            video_title=vid["video_title"],
                            video_url=vid["video_url"],
                            thumbnail_url=vid.get("thumbnail_url"),
                            views=vid["views"],
                            likes=vid.get("likes"),
                            comments=vid.get("comments"),
                            published_at=vid.get("published_at"),
                            outlier_score=vid.get("outlier_score"),
                            performance_indicator=vid.get("performance_indicator", "normal")
                        ))
                    
                    return TopVideosResponse(
                        competitor_id=competitor_id,
                        channel_name=competitor["channel_name"] or "Unknown Channel",
                        videos=videos,
                        mock=False,
                        source="youtube"
                    )
                except LiveProviderError as e:
                    logger.warning(f"YouTube API error fetching competitor videos: {e}")
                    # Fall through to mock data
                except Exception as e:
                    logger.error(f"Error fetching competitor videos from YouTube: {e}")
                    # Fall through to mock data
            
            # Fallback to mock data if YouTube API fails or no token available
            from datetime import datetime, timedelta
            
            mock_videos = []
            for i in range(10):
                days_ago = i * 3
                mock_videos.append(TopVideoResponse(
                    video_id=f"demo_vid_{competitor_id[:8]}_{i}",
                    video_title=f"Top Video #{i+1} - {competitor['channel_name']}",
                    video_url=f"https://www.youtube.com/watch?v=demo_vid_{i}",
                    thumbnail_url=f"https://via.placeholder.com/320x180?text=Video+{i+1}",
                    views=100000 - (i * 5000),
                    likes=5000 - (i * 200),
                    comments=300 - (i * 15),
                    published_at=datetime.now(timezone.utc) - timedelta(days=days_ago),
                    outlier_score=90.0 - (i * 8),
                    performance_indicator="outlier" if i < 2 else ("above_average" if i < 5 else "normal")
                ))
            
            return TopVideosResponse(
                competitor_id=competitor_id,
                channel_name=competitor["channel_name"] or "Unknown Channel",
                videos=mock_videos,
                mock=True,
                source="demo-fixture"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching competitor videos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/topic-ideas/save", response_model=TopicIdeaResponse)
async def save_topic_idea(
    payload: SaveTopicIdeaRequest,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org)
):
    """Save a competitor video as a topic idea"""
    org_id = resolve_org_id(org.get('org_id'))
    user_id = user.get("user_id") or user.get("sub") or "unknown"
    
    try:
        with get_conn() as conn, conn.cursor() as cur:
            # Verify competitor exists and belongs to org
            cur.execute("""
                SELECT channel_name FROM competitors
                WHERE id = %s AND org_id = %s
            """, (payload.competitor_id, org_id))
            
            competitor = cur.fetchone()
            if not competitor:
                raise HTTPException(status_code=404, detail="Competitor not found")
            
            # Check if already saved
            cur.execute("""
                SELECT id FROM competitor_topic_ideas
                WHERE org_id = %s AND competitor_id = %s AND video_id = %s
            """, (org_id, payload.competitor_id, payload.video_id))
            
            existing = cur.fetchone()
            if existing:
                raise HTTPException(status_code=400, detail="Topic idea already saved")
            
            # Insert topic idea
            cur.execute("""
                INSERT INTO competitor_topic_ideas
                (org_id, competitor_id, video_id, video_title, video_url, thumbnail_url,
                 views, likes, comments, published_at, outlier_score, performance_indicator,
                 notes, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, status, created_at
            """, (org_id, payload.competitor_id, payload.video_id, payload.video_title,
                  payload.video_url, payload.thumbnail_url, payload.views, payload.likes,
                  payload.comments, payload.published_at, payload.outlier_score,
                  payload.performance_indicator, payload.notes, user_id))
            
            result = cur.fetchone()
            conn.commit()
            
            return TopicIdeaResponse(
                id=str(result["id"]),
                competitor_id=payload.competitor_id,
                competitor_name=competitor["channel_name"],
                video_id=payload.video_id,
                video_title=payload.video_title,
                video_url=payload.video_url,
                thumbnail_url=payload.thumbnail_url,
                views=payload.views,
                outlier_score=payload.outlier_score,
                performance_indicator=payload.performance_indicator,
                notes=payload.notes,
                status=result["status"],
                created_at=result["created_at"]
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving topic idea: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/topic-ideas/list", response_model=TopicIdeasListResponse)
async def list_topic_ideas(
    status: Optional[str] = Query(None, description="Filter by status"),
    user=Depends(get_current_user),
    org=Depends(get_current_user_org)
):
    """List all saved topic ideas"""
    org_id = resolve_org_id(org.get('org_id'))
    
    try:
        with get_conn() as conn, conn.cursor() as cur:
            if status:
                cur.execute("""
                    SELECT cti.id, cti.competitor_id, c.channel_name as competitor_name,
                           cti.video_id, cti.video_title, cti.video_url, cti.thumbnail_url,
                           cti.views, cti.outlier_score, cti.performance_indicator,
                           cti.notes, cti.status, cti.created_at
                    FROM competitor_topic_ideas cti
                    LEFT JOIN competitors c ON cti.competitor_id = c.id
                    WHERE cti.org_id = %s AND cti.status = %s
                    ORDER BY cti.created_at DESC
                """, (org_id, status))
            else:
                cur.execute("""
                    SELECT cti.id, cti.competitor_id, c.channel_name as competitor_name,
                           cti.video_id, cti.video_title, cti.video_url, cti.thumbnail_url,
                           cti.views, cti.outlier_score, cti.performance_indicator,
                           cti.notes, cti.status, cti.created_at
                    FROM competitor_topic_ideas cti
                    LEFT JOIN competitors c ON cti.competitor_id = c.id
                    WHERE cti.org_id = %s
                    ORDER BY cti.created_at DESC
                """, (org_id,))
            
            rows = cur.fetchall()
            ideas = [
                TopicIdeaResponse(
                    id=str(row["id"]),
                    competitor_id=str(row["competitor_id"]),
                    competitor_name=row["competitor_name"],
                    video_id=row["video_id"],
                    video_title=row["video_title"],
                    video_url=row["video_url"],
                    thumbnail_url=row["thumbnail_url"],
                    views=row["views"],
                    outlier_score=float(row["outlier_score"]) if row["outlier_score"] else None,
                    performance_indicator=row["performance_indicator"],
                    notes=row["notes"],
                    status=row["status"],
                    created_at=row["created_at"]
                )
                for row in rows
            ]
            
            return TopicIdeasListResponse(ideas=ideas)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error listing topic ideas: {error_msg}")
        
        # Check if it's a table doesn't exist error
        if "does not exist" in error_msg.lower() or "relation" in error_msg.lower():
            # Return empty list instead of error for better UX
            return TopicIdeasListResponse(ideas=[])
        
        raise HTTPException(status_code=500, detail=f"Database error: {error_msg}")


@router.patch("/topic-ideas/{idea_id}/status")
async def update_topic_idea_status(
    idea_id: str,
    payload: UpdateTopicIdeaStatusRequest,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org)
):
    """Update the status of a topic idea"""
    org_id = resolve_org_id(org.get('org_id'))
    
    valid_statuses = ['saved', 'to_script', 'in_progress', 'ignore']
    if payload.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                UPDATE competitor_topic_ideas
                SET status = %s, updated_at = now()
                WHERE id = %s AND org_id = %s
                RETURNING id
            """, (payload.status, idea_id, org_id))
            
            result = cur.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Topic idea not found")
            
            conn.commit()
            return {"ok": True, "id": idea_id, "status": payload.status}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating topic idea status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/topic-ideas/{idea_id}")
async def delete_topic_idea(
    idea_id: str,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org)
):
    """Delete a topic idea"""
    org_id = resolve_org_id(org.get('org_id'))
    
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                DELETE FROM competitor_topic_ideas
                WHERE id = %s AND org_id = %s
                RETURNING id
            """, (idea_id, org_id))
            
            result = cur.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Topic idea not found")
            
            conn.commit()
            return {"ok": True, "id": idea_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting topic idea: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def calculate_simple_outlier_score(views: int, likes: Optional[int], comments: Optional[int]) -> Tuple[Optional[float], str]:
    """
    Calculate a simple outlier score for a video based on engagement metrics.
    Returns (score, performance_indicator) or (None, "normal") if insufficient data.
    """
    if not views or views == 0:
        return None, "normal"
    
    likes_ratio = (likes / views * 100) if likes and likes > 0 else 0
    comments_ratio = (comments / views * 100) if comments and comments > 0 else 0
    
    # Simple scoring based on engagement rates
    # High engagement: likes > 5%, comments > 0.5%
    # Medium engagement: likes > 2%, comments > 0.2%
    engagement_score = 0.0
    
    if likes_ratio > 5.0:
        engagement_score += 0.4
    elif likes_ratio > 2.0:
        engagement_score += 0.2
    
    if comments_ratio > 0.5:
        engagement_score += 0.3
    elif comments_ratio > 0.2:
        engagement_score += 0.15
    
    # Views normalization (assuming 1M+ views is high)
    views_normalized = min(1.0, views / 1_000_000) if views > 0 else 0
    views_score = views_normalized * 0.3
    
    total_score = round((engagement_score + views_score) * 100, 1)
    
    # Performance indicator
    if total_score >= 70:
        perf_indicator = "outlier"
    elif total_score >= 50:
        perf_indicator = "above_average"
    else:
        perf_indicator = "normal"
    
    return total_score, perf_indicator


@router.post("/topic-ideas/save-from-extension", response_model=SaveTopicIdeaFromExtensionResponse)
async def save_topic_idea_from_extension(
    payload: SaveTopicIdeaFromExtensionRequest,
    user=Depends(get_current_user),
    org=Depends(get_current_user_org)
):
    """
    Save a video from extension as a topic idea.
    If channel is tracked (competitor or own channel), calculate outlier score.
    If channel is not tracked, save without score but optionally create competitor.
    """
    org_id = resolve_org_id(org.get('org_id'))
    user_id = user.get("user_id") or user.get("sub") or "unknown"
    
    try:
        with get_conn() as conn, conn.cursor() as cur:
            competitor_id = None
            competitor_name = None
            outlier_score = None
            performance_indicator = "normal"
            
            # Extract channel ID from channel_url if provided
            channel_id = None
            if payload.channel_url:
                channel_id = extract_channel_id(payload.channel_url)
            
            # Check if this channel is tracked as a competitor
            if channel_id:
                cur.execute("""
                    SELECT id, channel_name FROM competitors
                    WHERE org_id = %s AND youtube_channel_id = %s
                """, (org_id, channel_id))
                
                competitor = cur.fetchone()
                if competitor:
                    competitor_id = str(competitor["id"])
                    competitor_name = competitor["channel_name"]
                    
                    # Calculate outlier score if we have video metrics
                    if payload.views is not None:
                        score, perf_ind = calculate_simple_outlier_score(
                            payload.views or 0,
                            payload.likes,
                            payload.comments
                        )
                        if score is not None:
                            outlier_score = score
                            performance_indicator = perf_ind
            
            # If channel not tracked as competitor, check if it's our own channel
            if not competitor_id and channel_id:
                cur.execute("""
                    SELECT id FROM youtube_channels
                    WHERE org_id = %s AND (
                        youtube_channel_id = %s OR google_channel_id = %s
                    )
                    LIMIT 1
                """, (org_id, channel_id, channel_id))
                
                own_channel = cur.fetchone()
                if own_channel and payload.views is not None:
                    # Calculate score for own channel too
                    score, perf_ind = calculate_simple_outlier_score(
                        payload.views or 0,
                        payload.likes,
                        payload.comments
                    )
                    if score is not None:
                        outlier_score = score
                        performance_indicator = perf_ind
            
            # If competitor exists, check for duplicate
            if competitor_id:
                cur.execute("""
                    SELECT id FROM competitor_topic_ideas
                    WHERE org_id = %s AND competitor_id = %s AND video_id = %s
                """, (org_id, competitor_id, payload.video_id))
                
                existing = cur.fetchone()
                if existing:
                    # Return existing idea
                    return SaveTopicIdeaFromExtensionResponse(
                        id=str(existing["id"]),
                        video_id=payload.video_id,
                        video_title=payload.video_title,
                        video_url=payload.video_url,
                        outlier_score=outlier_score,
                        competitor_id=competitor_id,
                        competitor_name=competitor_name,
                        saved=True
                    )
            
            # Insert topic idea
            # If competitor_id is None, we'll need to make competitor_id nullable or create a default competitor
            # For now, let's create a competitor entry if channel_id exists but not tracked
            if not competitor_id and channel_id:
                # Create a competitor entry for this channel
                channel_name = f"Channel {channel_id[:8]}"
                cur.execute("""
                    INSERT INTO competitors 
                    (org_id, youtube_channel_id, channel_name, created_by)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (org_id, youtube_channel_id) DO NOTHING
                    RETURNING id, channel_name
                """, (org_id, channel_id, channel_name, user_id))
                
                result = cur.fetchone()
                if result:
                    competitor_id = str(result["id"])
                    competitor_name = result["channel_name"]
                else:
                    # Competitor already exists, fetch it
                    cur.execute("""
                        SELECT id, channel_name FROM competitors
                        WHERE org_id = %s AND youtube_channel_id = %s
                    """, (org_id, channel_id))
                    comp = cur.fetchone()
                    if comp:
                        competitor_id = str(comp["id"])
                        competitor_name = comp["channel_name"]
            
            # If still no competitor_id, we can't save (competitor_id is required in schema)
            # For extension saves, we'll create a placeholder competitor or allow NULL
            # Check if competitor_id column allows NULL
            if not competitor_id:
                # Create a generic "Untracked" competitor for extension saves
                cur.execute("""
                    SELECT id FROM competitors
                    WHERE org_id = %s AND youtube_channel_id = 'UNTRACKED'
                    LIMIT 1
                """, (org_id,))
                
                untracked = cur.fetchone()
                if not untracked:
                    cur.execute("""
                        INSERT INTO competitors 
                        (org_id, youtube_channel_id, channel_name, created_by)
                        VALUES (%s, 'UNTRACKED', 'Untracked Channels', %s)
                        RETURNING id
                    """, (org_id, user_id))
                    untracked = cur.fetchone()
                
                if untracked:
                    competitor_id = str(untracked["id"])
                    competitor_name = "Untracked Channels"
            
            # Now insert the topic idea
            cur.execute("""
                INSERT INTO competitor_topic_ideas
                (org_id, competitor_id, video_id, video_title, video_url, thumbnail_url,
                 views, likes, comments, outlier_score, performance_indicator,
                 notes, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (org_id, competitor_id, payload.video_id, payload.video_title,
                  payload.video_url, payload.thumbnail_url, payload.views, payload.likes,
                  payload.comments, outlier_score, performance_indicator,
                  f"Saved from extension ({payload.source})", user_id))
            
            result = cur.fetchone()
            conn.commit()
            
            return SaveTopicIdeaFromExtensionResponse(
                id=str(result["id"]),
                video_id=payload.video_id,
                video_title=payload.video_title,
                video_url=payload.video_url,
                outlier_score=outlier_score,
                competitor_id=competitor_id,
                competitor_name=competitor_name,
                saved=True
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving topic idea from extension: {e}")
        raise HTTPException(status_code=500, detail=str(e))

