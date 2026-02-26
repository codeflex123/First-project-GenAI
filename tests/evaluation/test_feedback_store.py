from __future__ import annotations

from src.evaluation.feedback import record_feedback, get_feedback_snapshot


def test_feedback_store_aggregates_likes_and_dislikes():
    # Record a mix of feedback for two restaurants and two variants.
    record_feedback("1", "baseline", liked=True)
    record_feedback("1", "baseline", liked=False)
    record_feedback("1", "gemini", liked=True)
    record_feedback("2", "gemini", liked=False)

    snap = get_feedback_snapshot()

    assert "restaurants" in snap
    assert "variants" in snap

    r1 = snap["restaurants"]["1"]
    assert r1["likes"] == 2  # two likes for restaurant 1
    assert r1["dislikes"] == 1
    assert r1["total"] == 3

    gemini = snap["variants"]["gemini"]
    assert gemini["likes"] >= 1
    assert gemini["dislikes"] >= 1

