"""
Credentials Service
Loads and refreshes YouTube OAuth tokens for live data access
"""

import os
from typing import Optional, Dict
from app.db.pg import get_conn
from app.exceptions.live import NoLiveCredentials, LiveProviderError
import logging

logger = logging.getLogger(__name__)


async def get_credentials_for_channel(channel_id: str) -> Dict[str, str]:
    """
    Get OAuth credentials (access_token, refresh_token) for a channel.
    
    Raises NoLiveCredentials if no token exists or refresh fails.
    """
    try:
        with get_conn() as conn, conn.cursor() as cur:
            # Get refresh token from database
            cur.execute("""
                select refresh_token, scopes
                from youtube_tokens
                where channel_id = %s
                limit 1
            """, (channel_id,))
            
            row = cur.fetchone()
            if not row or not row.get("refresh_token"):
                raise NoLiveCredentials(f"No refresh token found for channel {channel_id}")
            
            refresh_token = row.get("refresh_token")
            scopes = row.get("scopes", "")
            
            # Refresh access token using Google OAuth
            access_token = await _refresh_access_token(refresh_token)
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "scopes": scopes,
            }
    except NoLiveCredentials:
        raise
    except Exception as e:
        logger.error(f"Error getting credentials for channel {channel_id}: {e}")
        raise NoLiveCredentials(f"Failed to load credentials: {e}")


async def _refresh_access_token(refresh_token: str) -> str:
    """
    Refresh Google OAuth access token using refresh token.
    
    Returns new access_token.
    Raises LiveProviderError if refresh fails.
    """
    import httpx
    
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        raise NoLiveCredentials("Google OAuth credentials not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
                timeout=10.0,
            )
            
            if response.status_code != 200:
                error_data = response.text
                logger.error(f"Token refresh failed: {response.status_code} - {error_data}")
                raise LiveProviderError(f"Token refresh failed: {error_data}")
            
            data = response.json()
            access_token = data.get("access_token")
            
            if not access_token:
                raise LiveProviderError("No access_token in refresh response")
            
            return access_token
    except httpx.HTTPError as e:
        logger.error(f"HTTP error refreshing token: {e}")
        raise LiveProviderError(f"Network error: {e}")
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise LiveProviderError(f"Token refresh failed: {e}")

