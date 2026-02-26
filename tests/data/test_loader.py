from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping

from src.data import loader
from src.data.models import Restaurant


class _FakeDataset:
    def __init__(self, rows: Iterable[Mapping[str, Any]]):
        self._rows = list(rows)

    def __iter__(self):
        return iter(self._rows)


def _fake_load_raw_restaurants() -> Iterable[Mapping[str, Any]]:
    # Minimal subset of realistic fields from the Zomato-style dataset.
    rows = [
        {
            "Restaurant ID": 1,
            "Restaurant Name": "Test Diner",
            "City": "Testville",
            "Address": "123 Test Street",
            "Locality": "Central",
            "Cuisines": "Italian, Pizza",
            "Price range": 2,
            "Average Cost for two": 800,
            "Aggregate rating": 4.3,
            "Rating text": "Very Good",
            "Votes": 150,
        },
        {
            "Restaurant ID": 2,
            "Restaurant Name": "Budget Bites",
            "City": "Cheap City",
            "Cuisines": "Fast Food",
            "Price range": 1,
            "Average Cost for two": 300,
            "Aggregate rating": 3.8,
            "Rating text": "Good",
            "Votes": 45,
        },
    ]
    return _FakeDataset(rows)


def test_load_restaurants_uses_mapping_and_respects_limit(monkeypatch):
    # Monkeypatch the hf_client to avoid any network calls during tests.
    monkeypatch.setattr(loader, "load_raw_restaurants", _fake_load_raw_restaurants)

    restaurants = loader.load_restaurants(limit=1)

    assert len(restaurants) == 1
    r = restaurants[0]
    assert isinstance(r, Restaurant)
    assert r.id == "1"
    assert r.name == "Test Diner"
    assert r.city == "Testville"
    assert "Italian" in r.cuisines
    assert r.price_range == 2
    assert r.aggregate_rating == 4.3


def test_load_restaurants_without_limit(monkeypatch):
    monkeypatch.setattr(loader, "load_raw_restaurants", _fake_load_raw_restaurants)

    restaurants = loader.load_restaurants()

    assert len(restaurants) == 2
    names = {r.name for r in restaurants}
    assert "Test Diner" in names
    assert "Budget Bites" in names

