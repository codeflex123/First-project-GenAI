from __future__ import annotations

from typing import List

from src.data.models import Restaurant
from src.services.restaurant_query_service import UserPreferences


def build_recommendation_prompt(
    prefs: UserPreferences,
    restaurants: List[Restaurant],
) -> str:
    """
    Build a text prompt for Gemini to generate:
    - A short natural-language explanation.
    - A short summary per restaurant.

    The model is instructed to respond with pure JSON so we can parse it safely.
    """

    lines: list[str] = []
    lines.append(
        "You are an assistant that recommends restaurants based on user preferences."
    )
    lines.append(
        "Given the user preferences and a list of candidate restaurants, "
        "select the best ones and respond ONLY with valid JSON, no extra text."
    )
    lines.append("")
    lines.append("The JSON schema must be:")
    lines.append(
        '{ "explanation": string, "restaurants": [ { "id": string, "name": string, "summary": string } ] }'
    )
    lines.append("")
    lines.append("User preferences:")
    lines.append(f"- City: {prefs.city or 'Any'}")
    lines.append(f"- Cuisines: {', '.join(prefs.cuisines or []) or 'Any'}")
    lines.append(f"- Minimum rating: {prefs.min_rating or 'Any'}")
    lines.append(f"- Maximum price range: {prefs.max_price_range or 'Any'}")
    lines.append(f"- Maximum results: {prefs.max_results}")
    lines.append("")
    lines.append("Candidate restaurants:")

    for r in restaurants:
        lines.append(
            f"- id={r.id} | name={r.name} | city={r.city or 'Unknown'} | "
            f"cuisines={', '.join(r.cuisines) or 'N/A'} | price_range={r.price_range or 'N/A'} | "
            f"rating={r.aggregate_rating or 'N/A'} | votes={r.votes or 0}"
        )

    lines.append("")
    lines.append(
        "Important: respond ONLY with the JSON object, no backticks, no explanation outside the JSON."
    )

    return "\n".join(lines)


__all__ = ["build_recommendation_prompt"]

