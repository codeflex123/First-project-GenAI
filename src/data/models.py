from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Restaurant:
    """
    Normalized restaurant representation used internally by the service.

    The underlying Hugging Face dataset may contain additional fields; this
    model focuses on the core attributes needed for recommendation logic.
    """

    id: str
    name: str
    city: Optional[str]
    address: Optional[str]
    locality: Optional[str]
    cuisines: List[str]
    price_range: Optional[int]
    average_cost_for_two: Optional[int]
    aggregate_rating: Optional[float]
    rating_text: Optional[str]
    votes: Optional[int]


__all__ = ["Restaurant"]

