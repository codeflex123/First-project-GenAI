from __future__ import annotations

from src.data.indexes import RestaurantIndex
from src.data.models import Restaurant
from src.services.restaurant_query_service import UserPreferences, query_restaurants


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


def _sample_index() -> RestaurantIndex:
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
        _make_restaurant(
            "3",
            "Sushi Central",
            "Fishcity",
            ["Japanese", "Sushi"],
            price_range=4,
            rating=4.8,
            votes=80,
        ),
        _make_restaurant(
            "4",
            "Budget Bites",
            "Testville",
            ["Fast Food"],
            price_range=1,
            rating=3.5,
            votes=40,
        ),
    ]
    return RestaurantIndex(restaurants)


def test_query_by_city_and_cuisine():
    index = _sample_index()

    prefs = UserPreferences(city="Testville", cuisines=["Italian"], max_results=10)
    results = query_restaurants(index, prefs)

    names = [r.name for r in results]
    assert "Pasta Palace" in names
    assert "Pizza Point" in names
    # Filtered out restaurants from other cities.
    assert "Sushi Central" not in names


def test_query_by_rating_and_price():
    index = _sample_index()

    prefs = UserPreferences(
        city="Testville",
        min_rating=4.0,
        max_price_range=2,
        max_results=10,
    )
    results = query_restaurants(index, prefs)

    # Only "Pizza Point" satisfies rating >= 4.0 and price_range <= 2 in Testville.
    assert len(results) == 1
    assert results[0].name == "Pizza Point"


def test_query_limits_results():
    index = _sample_index()

    prefs = UserPreferences(city=None, max_results=2)
    results = query_restaurants(index, prefs)

    assert len(results) == 2

