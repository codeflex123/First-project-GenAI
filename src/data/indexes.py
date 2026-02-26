from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from .models import Restaurant


class RestaurantIndex:
    """
    Simple in-memory indexes over restaurants for efficient Phase 2 queries.

    - Index by city (case-insensitive).
    - Index by cuisine (case-insensitive, individual cuisine tokens).
    """

    def __init__(self, restaurants: List[Restaurant]) -> None:
        self._restaurants: List[Restaurant] = restaurants
        self.by_city: Dict[str, List[Restaurant]] = defaultdict(list)
        self.by_cuisine: Dict[str, List[Restaurant]] = defaultdict(list)
        self._build_indexes()

    def _build_indexes(self) -> None:
        for r in self._restaurants:
            # City index
            if r.city:
                city_key = r.city.strip().lower()
                self.by_city[city_key].append(r)

            # Cuisine index
            for c in r.cuisines:
                cuisine_key = c.strip().lower()
                if cuisine_key:
                    self.by_cuisine[cuisine_key].append(r)

    @property
    def all(self) -> List[Restaurant]:
        """Return all restaurants contained in this index."""

        return list(self._restaurants)


__all__ = ["RestaurantIndex"]

