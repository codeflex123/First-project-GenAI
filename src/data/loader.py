from __future__ import annotations

from typing import Iterable, List, Mapping, Any, Optional
import re

from .hf_client import load_raw_restaurants
from .models import Restaurant


def _parse_int(value: Any) -> Optional[int]:
    """
    Parse an integer, accepting strings with commas (e.g. "1,000").
    """

    try:
        if value is None:
            return None
        if isinstance(value, str):
            text = value.replace(",", "").strip()
            if not text:
                return None
            # Strip common currency / formatting characters (e.g. "₹800", "Rs. 800").
            text = re.sub(r"[^\d-]+", "", text)
            if not text:
                return None
            return int(text)
        return int(value)
    except (TypeError, ValueError):
        return None


def _parse_float(value: Any) -> Optional[float]:
    """
    Parse a float from common Zomato-style fields.

    Handles:
    - plain numbers (e.g. \"4.1\")
    - strings like \"4.1/5\"
    - ignores placeholders like \"NEW\" or \"-\".
    """

    if value is None:
        return None

    if isinstance(value, str):
        text = value.strip()
        if not text or text in {"NEW", "-"}:
            return None
        # Handle \"4.1/5\" style ratings.
        if "/" in text:
            text = text.split("/", 1)[0].strip()
        try:
            return float(text)
        except ValueError:
            return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _split_cuisines(raw: Any) -> List[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(c).strip() for c in raw if str(c).strip()]
    # Many Zomato-style datasets encode cuisines as a comma-separated string.
    return [part.strip() for part in str(raw).split(",") if part.strip()]


def _map_row_to_restaurant(row: Mapping[str, Any]) -> Restaurant:
    """
    Map a raw dataset row into our normalized `Restaurant` model.

    The exact field names depend on the dataset, so we defensively fetch
    from multiple likely keys where appropriate.
    """

    # ID – prefer a stable unique key if available, fall back to restaurant name + city.
    # The dataset is expected to contain a unique identifier; common options are:
    # - "Restaurant ID", "restaurant_id", or "id".
    raw_id = (
        row.get("Restaurant ID")
        or row.get("restaurant_id")
        or row.get("id")
        or row.get("res_id")
    )
    name = row.get("Restaurant Name") or row.get("name") or "Unknown"

    city = row.get("City") or row.get("city")
    address = row.get("Address") or row.get("address")
    locality = row.get("Locality") or row.get("locality")

    cuisines = _split_cuisines(row.get("Cuisines") or row.get("cuisines"))

    price_range = _parse_int(row.get("Price range") or row.get("price_range"))

    # Cost columns can appear under several names; handle common variants.
    avg_cost_for_two = _parse_int(
        row.get("Average Cost for two")
        or row.get("average_cost_for_two")
        or row.get("approx_cost(for two people)")
        or row.get("Approx Cost for two")
    )

    # Rating can be stored as a numeric value or as strings like \"4.1/5\".
    aggregate_rating = _parse_float(
        row.get("Aggregate rating") or row.get("aggregate_rating") or row.get("rate")
    )
    rating_text = row.get("Rating text") or row.get("rating_text") or row.get("rate")
    votes = _parse_int(row.get("Votes") or row.get("votes"))

    if raw_id is None:
        # Fall back to a synthetic ID if the dataset doesn't include one.
        raw_id = f"{name}-{city or 'unknown'}"

    return Restaurant(
        id=str(raw_id),
        name=str(name),
        city=str(city) if city is not None else None,
        address=str(address) if address is not None else None,
        locality=str(locality) if locality is not None else None,
        cuisines=cuisines,
        price_range=price_range,
        average_cost_for_two=avg_cost_for_two,
        aggregate_rating=aggregate_rating,
        rating_text=str(rating_text) if rating_text is not None else None,
        votes=votes,
    )


def load_restaurants(limit: Optional[int] = None) -> List[Restaurant]:
    """
    High-level Phase 1 API: load and normalize restaurants from Hugging Face.

    - Uses `hf_client.load_raw_restaurants` to retrieve dataset rows.
    - Maps each row into a `Restaurant` instance.
    - Optionally limits the number of restaurants returned (useful for local tests).
    """

    restaurants: List[Restaurant] = []
    for row in load_raw_restaurants():
        restaurants.append(_map_row_to_restaurant(row))
        if limit is not None and len(restaurants) >= limit:
            break
    return restaurants


__all__ = ["load_restaurants"]

