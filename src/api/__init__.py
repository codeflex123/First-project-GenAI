from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path

from src.api.routes.recommendations import router as recommendations_router
from src.api.middleware.request_metrics import RequestMetricsMiddleware
from src.observability.metrics import get_metrics_snapshot


def create_app() -> FastAPI:
    """
    Phase 3 FastAPI application factory.

    - Registers health check.
    - Mounts the recommendations router under /api.
    - Serves a simple Phase 5 frontend from /.
    """

    app = FastAPI(title="AI Restaurant Recommendation Service", version="0.1.0")

    # Middleware
    app.add_middleware(RequestMetricsMiddleware)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/metrics")
    async def metrics() -> dict:
        """Basic JSON metrics snapshot (Phase 6)."""
        return get_metrics_snapshot()

    app.include_router(recommendations_router, prefix="/api")

    # Static frontend (Phase 5)
    frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
    if frontend_dir.exists():
        app.mount(
            "/static",
            StaticFiles(directory=frontend_dir, html=False),
            name="static",
        )

        @app.get("/", include_in_schema=False)
        async def index():
            # Rely on StaticFiles for assets; serve index.html manually.
            index_path = frontend_dir / "index.html"
            try:
                return HTMLResponse(index_path.read_text(encoding="utf-8"))
            except FileNotFoundError:
                return JSONResponse({"detail": "Frontend not found"}, status_code=404)

    return app


app = create_app()


__all__ = ["create_app", "app"]

