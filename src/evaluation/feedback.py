from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class FeedbackStats:
    likes: int = 0
    dislikes: int = 0

    @property
    def total(self) -> int:
        return self.likes + self.dislikes

    @property
    def like_rate(self) -> float:
        return self.likes / self.total if self.total else 0.0


@dataclass
class FeedbackStore:
    """
    In-memory feedback store for Phase 7.

    Tracks:
    - Per-restaurant stats.
    - Per-variant stats (e.g., 'baseline', 'gemini').
    """

    per_restaurant: Dict[str, FeedbackStats] = field(default_factory=dict)
    per_variant: Dict[str, FeedbackStats] = field(default_factory=dict)


class _FeedbackRegistry:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._store = FeedbackStore()

    def record_feedback(
        self,
        restaurant_id: str,
        variant: str,
        liked: bool,
        reason: Optional[str] = None,  # reason kept for future use
    ) -> None:
        variant = variant or "default"
        with self._lock:
            r_stats = self._store.per_restaurant.setdefault(restaurant_id, FeedbackStats())
            v_stats = self._store.per_variant.setdefault(variant, FeedbackStats())

            if liked:
                r_stats.likes += 1
                v_stats.likes += 1
            else:
                r_stats.dislikes += 1
                v_stats.dislikes += 1

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "restaurants": {
                    rid: {
                        "likes": s.likes,
                        "dislikes": s.dislikes,
                        "total": s.total,
                        "like_rate": round(s.like_rate, 3),
                    }
                    for rid, s in self._store.per_restaurant.items()
                },
                "variants": {
                    name: {
                        "likes": s.likes,
                        "dislikes": s.dislikes,
                        "total": s.total,
                        "like_rate": round(s.like_rate, 3),
                    }
                    for name, s in self._store.per_variant.items()
                },
            }


_REGISTRY = _FeedbackRegistry()


def record_feedback(
    restaurant_id: str,
    variant: str,
    liked: bool,
    reason: Optional[str] = None,
) -> None:
    _REGISTRY.record_feedback(restaurant_id, variant, liked, reason)


def get_feedback_snapshot() -> dict:
    return _REGISTRY.snapshot()


__all__ = ["record_feedback", "get_feedback_snapshot"]

