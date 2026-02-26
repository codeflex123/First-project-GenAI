from __future__ import annotations

from src.api import create_app
from fastapi.testclient import TestClient


def test_frontend_root_served():
    app = create_app()
    client = TestClient(app)

    resp = client.get("/")
    assert resp.status_code == 200
    text = resp.text

    assert "AI Restaurant Recommendation" in text
    assert "preferences-form" in text
    assert "/static/app.js" in text

