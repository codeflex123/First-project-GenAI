from __future__ import annotations

from src.config import load_config
from src.data.indexes import RestaurantIndex
from src.data.loader import load_restaurants
from src.services.restaurant_query_service import UserPreferences, query_restaurants
from src.utils.logger import configure_logging, get_logger


def main() -> None:
    """
    Manual test for Phase 2: indexing & filtering.

    Usage:
        python -m src.phase2_manual_test
    """

    cfg = load_config()
    configure_logging(cfg.log_level)
    log = get_logger("phase2")

    log.info("Loading restaurants for Phase 2 manual test...")
    restaurants = load_restaurants(limit=100)
    log.info("Loaded %d restaurants", len(restaurants))

    index = RestaurantIndex(restaurants)
    log.info("Index built: %d total, %d cities, %d cuisines", len(index.all), len(index.by_city), len(index.by_cuisine))

    # Example preferences for manual check; adjust as you like when running.
    prefs = UserPreferences(
        city=None,  # e.g. "New Delhi" or "Bangalore" depending on dataset
        cuisines=["Italian", "Pizza"],
        min_rating=4.0,
        max_price_range=3,
        max_results=5,
    )

    log.info("Running query with preferences: %s", prefs)
    results = query_restaurants(index, prefs)

    print("=== Phase 2 Manual Test: Query Results ===")
    print(f"Total matches: {len(results)}")
    for idx, r in enumerate(results, start=1):
        print(f"{idx}. {r.name} ({r.city or 'Unknown city'})")
        print(f"   Cuisines: {', '.join(r.cuisines) or 'N/A'}")
        print(f"   Price range: {r.price_range or 'N/A'}")
        print(f"   Rating: {r.aggregate_rating or 'N/A'} (votes: {r.votes or 0})")
        print()
    print("=== End of Phase 2 Manual Test ===")


if __name__ == "__main__":  # pragma: no cover
    main()

