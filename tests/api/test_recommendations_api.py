from __future__ import annotations

from fastapi.testclient import TestClient

from src.api import create_app
from src.api.routes import recommendations as rec_mod
from src.data.indexes import RestaurantIndex
from src.data.models import Restaurant
from src.services.restaurant_query_service import UserPreferences


def _make_restaurant(
    id: str,
    name: str,
    city: str,
    cuisines: list[str],
    price_range: int,
    rating: float,
    votes: int,
) -> Restaurant:
    return Restaurant(
        id=id,
        name=name,
        city=city,
        address=None,
        locality=None,
        cuisines=cuisines,
        price_range=price_range,
        average_cost_for_two=None,
        aggregate_rating=rating,
        rating_text=None,
        votes=votes,
    )


def _fake_index() -> RestaurantIndex:
    restaurants = [
        _make_restaurant(
            "1",
            "Pasta Palace",
            "Testville",
            ["Italian", "Pasta"],
            price_range=3,
            rating=4.6,
            votes=200,
        ),
        _make_restaurant(
            "2",
            "Pizza Point",
            "Testville",
            ["Italian", "Pizza"],
            price_range=2,
            rating=4.2,
            votes=120,
        ),
    ]
    return RestaurantIndex(restaurants)


def _create_test_client() -> TestClient:
    app = create_app()
    # Override the RestaurantIndex dependency so tests do not hit Hugging Face.
    app.dependency_overrides[rec_mod._get_index] = _fake_index
    return TestClient(app)


def test_recommendations_endpoint_returns_results():
    client = _create_test_client()

    payload = {
        "city": "Testville",
        "cuisines": ["Italian"],
        "min_rating": 4.0,
        "price_range": 3,
        "max_results": 5,
    }

    response = client.post("/api/recommendations", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "recommendations" in data
    assert "explanation" in data
    assert len(data["recommendations"]) >= 1

    names = {r["name"] for r in data["recommendations"]}
    assert "Pasta Palace" in names or "Pizza Point" in names


def test_recommendations_endpoint_uses_gemini_when_configured(monkeypatch):
    client = _create_test_client()

    # Fake Gemini call so tests do not use the real API.
    def fake_call_gemini(prefs: UserPreferences, restaurants: list[Restaurant], model_name: str = "x") -> tuple[str, dict[str, str]]:  # type: ignore[override]
        explanation = "Gemini explanation"
        summaries = {r.id: f"Gemini summary for {r.name}" for r in restaurants}
        return explanation, summaries

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(rec_mod, "call_gemini_for_recommendations", fake_call_gemini)

    payload = {
        "city": "Testville",
        "cuisines": ["Italian"],
        "min_rating": 4.0,
        "price_range": 3,
        "max_results": 2,
    }

    response = client.post("/api/recommendations", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["explanation"] == "Gemini explanation"
    for rec in data["recommendations"]:
        assert rec["summary"].startswith("Gemini summary for ")

