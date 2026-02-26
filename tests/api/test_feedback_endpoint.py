from __future__ import annotations

from fastapi.testclient import TestClient

from src.api import create_app


def test_feedback_endpoint_records_and_returns_snapshot():
    app = create_app()
    client = TestClient(app)

    payload = {
        "restaurant_id": "1",
        "liked": True,
        "variant": "gemini",
        "reason": "Delicious and accurate recommendation",
    }

    resp = client.post("/api/feedback", json=payload)
    assert resp.status_code == 200

    data = resp.json()
    assert data["success"] is True
    assert "snapshot" in data
    snap = data["snapshot"]

    assert "restaurants" in snap
    assert "1" in snap["restaurants"]
    assert snap["restaurants"]["1"]["likes"] >= 1

