from __future__ import annotations

from fastapi.testclient import TestClient

from src.api import create_app


def test_metrics_endpoint_counts_requests():
    app = create_app()
    client = TestClient(app)

    # Trigger a couple of requests.
    client.get("/health")
    client.get("/health")

    resp = client.get("/metrics")
    assert resp.status_code == 200

    data = resp.json()
    assert "requests" in data
    assert "llm" in data

    assert data["requests"]["total"] >= 2
    assert data["requests"]["per_path"]["/health"] >= 2

