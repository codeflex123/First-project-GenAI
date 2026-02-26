from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from src.data.indexes import RestaurantIndex
from src.data.models import Restaurant


@dataclass
class UserPreferences:
    city: Optional[str] = None
    cuisines: Optional[List[str]] = None
    min_rating: Optional[float] = None
    max_price_range: Optional[int] = None
    max_results: int = 10


def _normalize_city(city: Optional[str]) -> Optional[str]:
    return city.strip().lower() if city else None


def _normalize_cuisines(cuisines: Optional[List[str]]) -> List[str]:
    if not cuisines:
        return []
    return [c.strip().lower() for c in cuisines if c.strip()]


def _matches_city(r: Restaurant, city_key: str) -> bool:
    """
    Match a city filter against multiple location fields.

    Many rows in the HF dataset have city information embedded in the
    address/locality rather than a dedicated city column, so we check:
    - city
    - locality
    - address
    """

    city_key = city_key.lower()
    for value in (r.city, r.locality, r.address):
        if value and city_key in value.lower():
            return True
    return False


def _score_restaurant(r: Restaurant) -> float:
    """
    Compute a simple score for ranking:
    - Primary: aggregate rating (default 0)
    - Secondary: number of votes (scaled)
    """

    rating = r.aggregate_rating or 0.0
    votes = r.votes or 0
    # Small weight for votes so they help break ties.
    return rating + min(votes, 1000) / 1000.0


def query_restaurants(index: RestaurantIndex, prefs: UserPreferences) -> List[Restaurant]:
    """
    Phase 2 core API:
    - Filter restaurants based on user preferences (city, cuisine, rating, price).
    - Rank by a simple heuristic (rating + votes).
    - Return at most `max_results` restaurants.
    """

    city_key = _normalize_city(prefs.city)
    cuisine_keys = _normalize_cuisines(prefs.cuisines)

    # 1. Start with city subset if provided, else all.
    if city_key:
        if city_key in index.by_city:
            candidates = list(index.by_city[city_key])
        else:
            # Fall back to scanning all restaurants and matching the
            # city key against city/locality/address text.
            candidates = [r for r in index.all if _matches_city(r, city_key)]
    else:
        candidates = index.all

    # 2. Filter by cuisines (intersection logic: restaurant must match at least one requested cuisine).
    if cuisine_keys:
        wanted = set(cuisine_keys)

        def has_cuisine(r: Restaurant) -> bool:
            cuisines = {c.strip().lower() for c in r.cuisines}
            return not cuisines.isdisjoint(wanted)

        candidates = [r for r in candidates if has_cuisine(r)]

    # 3. Filter by minimum rating (strict).
    if prefs.min_rating is not None:
        candidates = [
            r
            for r in candidates
            if r.aggregate_rating is not None and r.aggregate_rating >= prefs.min_rating
        ]

    # 4. Filter by max price (INR for two).
    # Map UI price_range 1,2,3,4 to INR: 400, 800, 1500, no cap.
    # Use average_cost_for_two when present (strict).
    if prefs.max_price_range is not None:
        max_inr = {1: 400, 2: 800, 3: 1500, 4: 999999}.get(prefs.max_price_range, 999999)
        candidates = [
            r
            for r in candidates
            if r.average_cost_for_two is not None and r.average_cost_for_two <= max_inr
        ]

    # 5. Rank, deduplicate by logical identity (name + location), and limit.
    ranked = sorted(candidates, key=_score_restaurant, reverse=True)

    seen_keys = set()
    unique_ranked: List[Restaurant] = []
    for r in ranked:
        # Use name + locality/address as a logical identity to collapse
        # multiple rows for the same restaurant.
        location_part = (r.locality or r.address or r.city or "").strip().lower()
        key = (r.name.strip().lower(), location_part)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        unique_ranked.append(r)

    return unique_ranked[: max(prefs.max_results, 1)]


__all__ = ["UserPreferences", "query_restaurants"]

