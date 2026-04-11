"""
Error logging middleware for FastAPI
Logs 500 errors and unhandled exceptions to logs/app.log
"""
import logging
import os
from pathlib import Path
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import traceback

# Setup logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logger = logging.getLogger("app.errors")
logger.setLevel(logging.ERROR)

# File handler for errors
file_handler = logging.FileHandler(log_dir / "app.log")
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Also log to console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class ErrorLoggerMiddleware(BaseHTTPMiddleware):
    """Middleware to log 500 errors and exceptions"""
    
    async def dispatch(self, request: Request, call_next):
        resp = None
        try:
            resp = await call_next(request)
        except Exception as e:
            # Log full traceback
            error_trace = traceback.format_exc()
            logger.error(
                "Unhandled error on %s %s\n%s",
                request.method,
                request.url.path,
                error_trace
            )
            raise
        
        # Log 500 status codes
        if resp.status_code >= 500:
            logger.error(
                "500 error on %s %s - Status: %d",
                request.method,
                request.url.path,
                resp.status_code
            )
        
        return resp

