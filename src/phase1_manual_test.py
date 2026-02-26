from __future__ import annotations

import os

from src.data.loader import load_restaurants
from src.data.hf_client import DATASET_ID, DATASET_SPLIT


def main() -> None:
    """Simple manual check for Phase 1 data ingestion & modeling.

    Usage:
        python -m src.phase1_manual_test

    Optional environment:
        HF_TOKEN / HUGGINGFACE_TOKEN  - Hugging Face access token (if required).
    """

    print("=== Phase 1 Manual Test: Data Ingestion & Modeling ===")
    print(f"Dataset: {DATASET_ID} (split={DATASET_SPLIT})")
    token_present = bool(os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN"))
    print(f"Hugging Face token present: {token_present}")

    try:
        restaurants = load_restaurants(limit=5)
    except Exception as exc:  # pragma: no cover - for manual diagnostics
        print("\nError while loading restaurants from Hugging Face:")
        print(repr(exc))
        return

    print(f"\nLoaded {len(restaurants)} restaurant(s). Showing details:\n")
    for idx, r in enumerate(restaurants, start=1):
        print(f"{idx}. {r.name} ({r.city or 'Unknown city'})")
        print(f"   Cuisines: {', '.join(r.cuisines) or 'N/A'}")
        print(f"   Price range: {r.price_range or 'N/A'}")
        print(f"   Avg cost for two: {r.average_cost_for_two or 'N/A'}")
        print(f"   Rating: {r.aggregate_rating or 'N/A'} ({r.rating_text or 'N/A'})")
        print(f"   Votes: {r.votes or 0}")
        print()

    print("=== Phase 1 Manual Test Complete ===")


if __name__ == "__main__":  # pragma: no cover
    main()

