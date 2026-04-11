from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI
import os
import time

# Prometheus metrics
try:
    from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
    
    REQUESTS = Counter("http_requests_total", "Total HTTP requests", ["path", "method"])
    RESPONSES = Counter("http_responses_total", "Total HTTP responses", ["path", "method", "status"])
    REQUEST_LATENCY = Histogram("http_request_duration_seconds", "Request latency seconds", ["path", "method"])
    AUTH_FAILURES = Counter("auth_failures_total", "Auth failures (403/401)")
    ERROR_5XX = Counter("http_5xx_total", "Server errors")
    
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

def add_middleware(app: FastAPI):
    # Explicit origins for local development
    default_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    
    env_origins = os.getenv("ALLOWED_ORIGINS", "").strip()
    if env_origins:
        origins = [origin.strip() for origin in env_origins.split(",") if origin.strip()]
    else:
        origins = default_origins
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,  # Required for cookies
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add error logging middleware
    try:
        from app.middleware.error_logger import ErrorLoggerMiddleware
        app.add_middleware(ErrorLoggerMiddleware)
    except Exception as e:
        # If error logger fails to import, continue without it
        print(f"Warning: Error logger middleware not available: {e}")
    
    # Add Prometheus metrics middleware if available
    if PROMETHEUS_AVAILABLE and os.getenv("PROMETHEUS_ENABLED", "false").lower() == "true":
        app.add_middleware(MetricsMiddleware)

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if not PROMETHEUS_AVAILABLE:
            return await call_next(request)
        
        path = request.url.path
        method = request.method
        
        # Skip metrics endpoint itself
        if path == "/metrics":
            return await call_next(request)
        
        start = time.time()
        REQUESTS.labels(path=path, method=method).inc()
        
        try:
            response = await call_next(request)
        except Exception:
            ERROR_5XX.inc()
            raise
        finally:
            duration = time.time() - start
            REQUEST_LATENCY.labels(path=path, method=method).observe(duration)
        
        sc = getattr(response, "status_code", 500)
        RESPONSES.labels(path=path, method=method, status=str(sc)).inc()
        
        if sc in (401, 403):
            AUTH_FAILURES.inc()
        
        if 500 <= sc < 600:
            ERROR_5XX.inc()
        
        return response

def metrics_endpoint():
    from fastapi import Response
    if not PROMETHEUS_AVAILABLE:
        return Response("Prometheus client not installed", status_code=503)
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
