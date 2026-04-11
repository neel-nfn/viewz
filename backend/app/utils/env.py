"""
Shared environment detection utilities.
Centralized logic for detecting local/dev vs production environments.
"""
import os


def is_local() -> bool:
    """
    Check if running in local/dev environment.
    
    Returns True if:
    - ENVIRONMENT is "local", "dev", or "development"
    - DEBUG is "1", "true", or "yes"
    - ENVIRONMENT is empty/missing (defaults to local-friendly)
    
    Returns False for production environments.
    """
    env = os.getenv("ENVIRONMENT", "").lower()
    debug = os.getenv("DEBUG", "").lower()
    # treat empty / missing as local-friendly
    return env in ("local", "dev", "development") or debug in ("1", "true", "yes")


def is_production() -> bool:
    """
    Check if running in production environment.
    
    Returns True if ENVIRONMENT is explicitly set to "production" or "prod".
    """
    env = os.getenv("ENVIRONMENT", "").lower()
    return env in ("production", "prod")


def require_local():
    """
    Raise HTTPException if not running in local/dev environment.
    Use this to protect debug/dev endpoints.
    """
    from fastapi import HTTPException
    if not is_local():
        raise HTTPException(status_code=404, detail="Not found")

