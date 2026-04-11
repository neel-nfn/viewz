"""
Analytics Cache Service
In-memory cache for analytics data to reduce YouTube API calls.
Can be easily swapped to DB-based caching later.
"""

import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# In-memory cache storage
_cache: Dict[str, Dict[str, Any]] = {}

# Default TTL: 30 minutes (in seconds)
DEFAULT_TTL = 30 * 60

# Cache TTLs by endpoint type
CACHE_TTL = {
    "channel_snapshot": 30 * 60,  # 30 minutes
    "trends": 30 * 60,  # 30 minutes
    "top_videos": 60 * 60,  # 1 hour (changes less frequently)
    "keywords": 90 * 60,  # 1.5 hours (keyword analysis is relatively stable)
    "ai_insights": 120 * 60,  # 2 hours (AI insights change slowly)
    "recommendations": 90 * 60,  # 1.5 hours (recommendations update periodically)
    "youtube_health": 5 * 60,  # 5 minutes (health checks should be relatively fresh)
}


def _make_cache_key(channel_id: str, endpoint: str, **kwargs) -> str:
    """Generate a cache key from channel_id, endpoint, and parameters."""
    key_parts = [endpoint, channel_id]
    # Sort kwargs for consistent keys
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}:{v}")
    return "|".join(key_parts)


def get_cached(channel_id: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
    """
    Get cached analytics data.
    
    Args:
        channel_id: Channel ID
        endpoint: Endpoint name (e.g., "channel_snapshot", "trends")
        **kwargs: Additional parameters (e.g., days=7, limit=5)
    
    Returns:
        Cached data dict or None if not found/expired
    """
    cache_key = _make_cache_key(channel_id, endpoint, **kwargs)
    
    if cache_key not in _cache:
        return None
    
    cached_item = _cache[cache_key]
    ttl = CACHE_TTL.get(endpoint, DEFAULT_TTL)
    
    # Check if expired
    if time.time() - cached_item["timestamp"] > ttl:
        # Remove expired entry
        del _cache[cache_key]
        return None
    
    logger.debug(f"Cache hit for {cache_key}")
    return cached_item["data"]


def set_cached(channel_id: str, endpoint: str, data: Dict[str, Any], **kwargs) -> None:
    """
    Cache analytics data.
    
    Args:
        channel_id: Channel ID
        endpoint: Endpoint name
        data: Data to cache
        **kwargs: Additional parameters
    """
    cache_key = _make_cache_key(channel_id, endpoint, **kwargs)
    
    _cache[cache_key] = {
        "data": data,
        "timestamp": time.time(),
    }
    
    logger.debug(f"Cached data for {cache_key}")


def clear_cache(channel_id: Optional[str] = None, endpoint: Optional[str] = None) -> int:
    """
    Clear cache entries.
    
    Args:
        channel_id: If provided, only clear entries for this channel
        endpoint: If provided, only clear entries for this endpoint
    
    Returns:
        Number of entries cleared
    """
    if channel_id is None and endpoint is None:
        # Clear all
        count = len(_cache)
        _cache.clear()
        return count
    
    # Clear matching entries
    keys_to_delete = []
    for key in _cache.keys():
        key_parts = key.split("|")
        if endpoint and key_parts[0] != endpoint:
            continue
        if channel_id and channel_id not in key:
            continue
        keys_to_delete.append(key)
    
    for key in keys_to_delete:
        del _cache[key]
    
    return len(keys_to_delete)


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    return {
        "total_entries": len(_cache),
        "endpoints": list(set(key.split("|")[0] for key in _cache.keys())),
    }
