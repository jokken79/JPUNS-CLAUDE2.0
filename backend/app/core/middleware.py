"""Custom middlewares for logging, security and exception handling."""
from __future__ import annotations

import time
from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.exceptions import UNSException, http_exception_from_uns
from app.core.logging import app_logger, log_performance_metric, log_security_event


class LoggingMiddleware(BaseHTTPMiddleware):
    """Attach structured logging to each request."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.perf_counter()
        route = request.url.path
        method = request.method
        client = request.client.host if request.client else "unknown"

        app_logger.bind(route=route, method=method, client=client).info("request.started")

        response = await call_next(request)

        elapsed = time.perf_counter() - start
        response.headers["X-Process-Time"] = f"{elapsed:.4f}"

        log_performance_metric("request_duration", elapsed, route=route, status=response.status_code)
        app_logger.bind(route=route, method=method, status=response.status_code).info("request.finished")
        return response


class SecurityMiddleware(BaseHTTPMiddleware):
    """Add common security headers and detect suspicious behaviour."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("X-XSS-Protection", "1; mode=block")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")

        if request.headers.get("User-Agent") in {None, "", "curl", "python-requests/2.x"}:
            log_security_event(message="Suspicious user agent", user_agent=request.headers.get("User-Agent"))

        return response


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """Convert internal exceptions into JSON responses."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except UNSException as exc:
            app_logger.bind(route=request.url.path, type="uns").error(exc.message)
            raise http_exception_from_uns(exc)
        except HTTPException:
            raise
        except Exception as exc:  # pragma: no cover - defensive programming
            app_logger.bind(route=request.url.path, type="unhandled").exception("Unhandled exception")
            raise HTTPException(
                status_code=500,
                detail={"message": "Internal server error", "details": str(exc)}
            )


__all__ = ["LoggingMiddleware", "SecurityMiddleware", "ExceptionHandlerMiddleware"]
