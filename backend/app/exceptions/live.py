"""
Live Data Provider Exceptions
"""


class NoLiveCredentials(Exception):
    """Raised when no credentials are available for live data."""
    pass


class LiveProviderError(Exception):
    """Raised when live provider (e.g., YouTube API) returns an error."""
    pass

