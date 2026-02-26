from __future__ import annotations

import time
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send

from src.observability.metrics import get_metrics_store


class RequestMetricsMiddleware(BaseHTTPMiddleware):
    """
    Phase 6 middleware to track basic request metrics:
    - Total requests
    - Errors
    - Average latency
    - Per-path counts
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self._store = get_metrics_store()

    async def dispatch(self, request: Request, call_next: Callable):
        path = request.url.path
        # Use the metrics store context manager for consistency.
        with self._store.track_request(path):
            response = await call_next(request)
        return response


__all__ = ["RequestMetricsMiddleware"]

