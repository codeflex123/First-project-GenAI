from __future__ import annotations

from typing import List, Optional

import anyio
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, conint, confloat

from src.config import load_config
from src.data.indexes import RestaurantIndex
from src.data.loader import load_restaurants
from src.data.models import Restaurant
from src.llm.client import call_gemini_for_recommendations
from src.services.restaurant_query_service import UserPreferences, query_restaurants
from src.utils.logger import configure_logging, get_logger
from src.evaluation.feedback import record_feedback, get_feedback_snapshot
from src.observability.metrics import get_metrics_store


router = APIRouter(tags=["recommendations"])

_index: Optional[RestaurantIndex] = None
_logger = get_logger("api.recommendations")


class RecommendationRequest(BaseModel):
    city: Optional[str] = Field(
        default=None,
        description="City or area to search in (e.g., 'New Delhi').",
    )
    price_range: Optional[conint(ge=1, le=4)] = Field(
        default=None,
        description="Maximum Zomato-style price range (1=cheapest, 4=most expensive).",
    )
    min_rating: Optional[confloat(ge=0, le=5)] = Field(
        default=None,
        description="Minimum aggregate rating required (0–5).",
    )
    cuisines: Optional[List[str]] = Field(
        default=None,
        description="List of desired cuisines (e.g., ['Italian', 'Pizza']).",
    )
    max_results: conint(ge=1, le=20) = Field(
        default=5,
        description="Maximum number of recommendations to return.",
    )


class RestaurantRecommendation(BaseModel):
    name: str
    address: Optional[str]
    city: Optional[str]
    cuisines: List[str]
    price_range: Optional[int]
    average_cost_for_two: Optional[int]
    rating: Optional[float]
    votes: Optional[int]
    source_id: str
    summary: str


class RecommendationResponse(BaseModel):
    recommendations: List[RestaurantRecommendation]
    explanation: str


class FeedbackRequest(BaseModel):
    restaurant_id: str = Field(..., description="The recommended restaurant's source_id.")
    liked: bool = Field(..., description="True if the user liked the recommendation.")
    variant: str = Field(
        default="gemini",
        description="Recommendation variant (e.g., 'baseline' or 'gemini').",
    )
    reason: Optional[str] = Field(
        default=None,
        description="Optional free-text reason for the feedback.",
    )


class FeedbackResponse(BaseModel):
    success: bool
    snapshot: dict


def _get_index() -> RestaurantIndex:
    """
    Lazy-load and cache the restaurant index.

    This uses the Phase 1 loader and Phase 2 indexer to prepare data
    for API queries.
    """

    global _index
    if _index is None:
        cfg = load_config()
        configure_logging(cfg.log_level)
        _logger.info("Building RestaurantIndex for the first time...")
        restaurants = load_restaurants()  # full dataset
        _index = RestaurantIndex(restaurants)
        _logger.info(
            "RestaurantIndex built: %d restaurants, %d cities, %d cuisines",
            len(_index.all),
            len(_index.by_city),
            len(_index.by_cuisine),
        )
    return _index


def _restaurant_to_recommendation(r: Restaurant) -> RestaurantRecommendation:
    # Simple heuristic summary for Phase 3;
    # Gemini-generated summaries will replace this in Phase 4.
    summary_parts = []
    if r.aggregate_rating is not None:
        summary_parts.append(f"Rated {r.aggregate_rating:.1f}")
    if r.votes is not None:
        summary_parts.append(f"based on {r.votes} votes")
    if r.price_range is not None:
        summary_parts.append(f"price range {r.price_range}")
    if r.cuisines:
        summary_parts.append(f"serves {', '.join(r.cuisines)}")
    summary = ", ".join(summary_parts) if summary_parts else "No detailed summary available."

    return RestaurantRecommendation(
        name=r.name,
        address=r.address,
        # Prefer locality as a more specific area label; fall back to city.
        city=r.locality or r.city,
        cuisines=r.cuisines,
        price_range=r.price_range,
        average_cost_for_two=r.average_cost_for_two,
        rating=r.aggregate_rating,
        votes=r.votes,
        source_id=r.id,
        summary=summary,
    )


@router.post(
    "/recommendations",
    response_model=RecommendationResponse,
    summary="Get restaurant recommendations",
)
async def create_recommendations(
    payload: RecommendationRequest,
    index: RestaurantIndex = Depends(_get_index),
) -> RecommendationResponse:
    """
    Phase 4 endpoint:
    - Validates user preferences.
    - Uses Phase 2 query service to find candidate restaurants.
    - If a Gemini API key is configured, calls Gemini to generate
      natural-language summaries and an explanation.
    - Falls back to heuristic summaries if Gemini is unavailable.
    """

    prefs = UserPreferences(
        city=payload.city,
        cuisines=payload.cuisines,
        min_rating=float(payload.min_rating) if payload.min_rating is not None else None,
        max_price_range=int(payload.price_range) if payload.price_range is not None else None,
        max_results=int(payload.max_results),
    )

    _logger.info("Received recommendation request: %s", prefs)

    # If no filters are provided at all, fall back to returning
    # the first N restaurants from the index instead of applying
    # any filtering logic. This guarantees we show something.
    filters_empty = (
        not prefs.city
        and not prefs.cuisines
        and prefs.min_rating is None
        and prefs.max_price_range is None
    )

    if filters_empty:
        # No filters: just show the first N restaurants from the index.
        results = index.all[: prefs.max_results]
    else:
        # With filters: do real filtering (strict). If nothing matches,
        # the client will see "No restaurants matched the given filters."
        results = query_restaurants(index, prefs)

    # Default: heuristic summaries and explanation.
    recos = [_restaurant_to_recommendation(r) for r in results]
    if not recos:
        explanation = "No restaurants matched the given filters."
        return RecommendationResponse(recommendations=recos, explanation=explanation)

    explanation = (
        "Restaurants are selected based on your filters (city, cuisines, rating, price range) "
        "and ranked by rating and popularity."
    )

    # Phase 4: attempt to enhance with Gemini if configured.
    cfg = load_config()
    if cfg.gemini_api_key and cfg.enable_gemini:
        try:
            store = get_metrics_store()
            with store.track_llm_call():
                with anyio.fail_after(cfg.gemini_timeout_seconds):
                    llm_explanation, summaries_by_id = await anyio.to_thread.run_sync(
                        lambda: call_gemini_for_recommendations(prefs, results)
                    )
            if llm_explanation:
                explanation = llm_explanation

            # Override summaries where Gemini provided them.
            for r in recos:
                custom = summaries_by_id.get(r.source_id)
                if custom:
                    r.summary = custom
        except Exception as exc:  # pragma: no cover - defensive around external API
            _logger.warning("Gemini call failed, using heuristic summaries. Error: %r", exc)

    return RecommendationResponse(recommendations=recos, explanation=explanation)


@router.post(
    "/feedback",
    response_model=FeedbackResponse,
    summary="Submit feedback for a recommendation",
)
async def submit_feedback(payload: FeedbackRequest) -> FeedbackResponse:
    """
    Phase 7 endpoint:
    - Accepts thumbs up/down feedback for a single restaurant recommendation.
    - Records the feedback in the in-memory feedback store.
    - Returns an aggregated snapshot so clients can inspect stats.
    """

    record_feedback(
        restaurant_id=payload.restaurant_id,
        variant=payload.variant,
        liked=payload.liked,
        reason=payload.reason,
    )
    snapshot = get_feedback_snapshot()
    return FeedbackResponse(success=True, snapshot=snapshot)

