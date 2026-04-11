"""
Auth cookie utilities for setting and managing session cookies
"""
from fastapi import Response
from app.utils.env import is_local

SESSION_COOKIE_NAME = "viewz_session"

def set_session_cookie(
    response: Response,
    token: str,
    max_age: int = 60 * 60 * 24 * 7,  # 7 days
    localhost: bool = None,
):
    """
    Set a session cookie on the response.
    
    For localhost: secure=False, samesite="lax", no domain
    For prod: secure=True, samesite="none", domain set
    """
    # Determine if we're in local/dev (use provided localhost or detect)
    is_local_env = localhost if localhost is not None else is_local()
    
    if is_local_env:
        # Local development settings
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=token,
            max_age=max_age,
            httponly=True,
            secure=False,  # localhost doesn't need HTTPS
            samesite="lax",  # works with localhost
            path="/",
            # No domain - let browser set it for localhost
        )
    else:
        # Production settings
        import os
        domain = os.getenv("COOKIE_DOMAIN", ".getarainc.com")
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=token,
            max_age=max_age,
            httponly=True,
            secure=True,  # HTTPS required
            samesite="none",  # cross-site cookies
            path="/",
            domain=domain,
        )


def clear_session_cookie(response: Response):
    """
    Clear the session cookie by deleting it.
    Must match the same path/domain settings used when setting the cookie.
    """
    # Delete by setting expired cookie with same name/path
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/",
    )

