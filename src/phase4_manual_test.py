from __future__ import annotations

from src.config import load_config
from src.data.indexes import RestaurantIndex
from src.data.loader import load_restaurants
from src.services.restaurant_query_service import UserPreferences, query_restaurants
from src.llm.client import call_gemini_for_recommendations
from src.utils.logger import configure_logging, get_logger


def main() -> None:
    """
    Manual test for Phase 4: Gemini integration.

    Usage:
        export GEMINI_API_KEY=your_api_key_here
        python -m src.phase4_manual_test
    """

    cfg = load_config()
    configure_logging(cfg.log_level)
    log = get_logger("phase4")

    if not cfg.gemini_api_key:
        log.error(
            "GEMINI_API_KEY is not set. Please configure it before running this test."
        )
        return

    log.info("Loading restaurants for Phase 4 manual test...")
    restaurants = load_restaurants(limit=50)
    index = RestaurantIndex(restaurants)

    prefs = UserPreferences(
        city=None,
        cuisines=["Italian", "Pizza"],
        min_rating=4.0,
        max_price_range=3,
        max_results=5,
    )
    log.info("Querying index with preferences: %s", prefs)
    candidates = query_restaurants(index, prefs)

    if not candidates:
        print("No candidates found for the given preferences.")
        return

    log.info("Calling Gemini for recommendations...")
    explanation, summaries_by_id = call_gemini_for_recommendations(prefs, candidates)

    print("=== Phase 4 Manual Test: Gemini Recommendations ===")
    print(f"Explanation:\n{explanation}\n")
    print("Restaurants:")
    for r in candidates:
        summary = summaries_by_id.get(r.id, "(no Gemini summary)")
        print(f"- {r.name} ({r.city or 'Unknown city'})")
        print(f"  Cuisines: {', '.join(r.cuisines) or 'N/A'}")
        print(f"  Rating: {r.aggregate_rating or 'N/A'} (votes: {r.votes or 0})")
        print(f"  Gemini summary: {summary}")
        print()
    print("=== End of Phase 4 Manual Test ===")


if __name__ == "__main__":  # pragma: no cover
    main()

