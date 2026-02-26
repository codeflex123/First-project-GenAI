from __future__ import annotations

from src.data.models import Restaurant
from src.llm.parser import parse_gemini_response
from src.llm.prompts import build_recommendation_prompt
from src.services.restaurant_query_service import UserPreferences


def _sample_restaurants() -> list[Restaurant]:
    return [
        Restaurant(
            id="1",
            name="Pasta Palace",
            city="Testville",
            address=None,
            locality=None,
            cuisines=["Italian", "Pasta"],
            price_range=3,
            average_cost_for_two=None,
            aggregate_rating=4.6,
            rating_text=None,
            votes=200,
        ),
        Restaurant(
            id="2",
            name="Pizza Point",
            city="Testville",
            address=None,
            locality=None,
            cuisines=["Italian", "Pizza"],
            price_range=2,
            average_cost_for_two=None,
            aggregate_rating=4.2,
            rating_text=None,
            votes=120,
        ),
    ]


def test_build_recommendation_prompt_includes_core_info():
    prefs = UserPreferences(
        city="Testville",
        cuisines=["Italian"],
        min_rating=4.0,
        max_price_range=3,
        max_results=5,
    )
    restaurants = _sample_restaurants()

    prompt = build_recommendation_prompt(prefs, restaurants)

    assert "Pasta Palace" in prompt
    assert "Pizza Point" in prompt
    assert "Testville" in prompt
    assert "Maximum results: 5" in prompt
    # Ensure we instruct model to output JSON.
    assert '"explanation": string' in prompt


def test_parse_gemini_response_happy_path():
    restaurants = _sample_restaurants()
    raw = """
    {
      "explanation": "Top Italian places in Testville.",
      "restaurants": [
        {"id": "1", "name": "Pasta Palace", "summary": "Cozy pasta-focused restaurant."},
        {"id": "2", "name": "Pizza Point", "summary": "Casual pizza joint."}
      ]
    }
    """
    explanation, summaries = parse_gemini_response(raw, restaurants)

    assert "Top Italian places" in explanation
    assert summaries["1"] == "Cozy pasta-focused restaurant."
    assert summaries["2"] == "Casual pizza joint."


def test_parse_gemini_response_handles_invalid_json():
    restaurants = _sample_restaurants()
    raw = "this is not json"

    explanation, summaries = parse_gemini_response(raw, restaurants)

    assert "unavailable" in explanation.lower()
    assert summaries == {}

