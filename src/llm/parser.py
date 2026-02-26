from __future__ import annotations

import json
import re
from typing import Dict, List, Tuple

from src.data.models import Restaurant


def _extract_json_object(text: str) -> str | None:
    """
    Try to extract a JSON object from a possibly messy LLM response.

    Handles common cases like:
    - markdown code fences ```json ... ```
    - extra prose before/after the JSON
    """

    if not text:
        return None

    cleaned = text.strip()

    # Remove common fenced code blocks.
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    # Try simplest case first.
    if cleaned.startswith("{") and cleaned.endswith("}"):
        return cleaned

    # Fallback: take substring from first { to last }.
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        return cleaned[start : end + 1]
    return None


def parse_gemini_response(
    raw_text: str, restaurants: List[Restaurant]
) -> Tuple[str, Dict[str, str]]:
    """
    Parse Gemini JSON response into:
    - explanation string
    - mapping from restaurant id -> summary

    If parsing fails, returns a generic explanation and empty mapping.
    """

    candidate = _extract_json_object(raw_text) or raw_text
    try:
        data = json.loads(candidate)
    except json.JSONDecodeError:
        return (
            "AI explanation unavailable due to invalid response format. "
            "Falling back to heuristic summaries.",
            {},
        )

    explanation = str(data.get("explanation") or "").strip()
    items = data.get("restaurants") or []

    # Build name lookup as a fallback when id is missing.
    by_name = {r.name.lower(): r.id for r in restaurants}

    summaries: Dict[str, str] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        rid = item.get("id")
        name = item.get("name")
        summary = (item.get("summary") or "").strip()

        if not rid and name:
            rid = by_name.get(str(name).lower())

        if not rid or not summary:
            continue

        summaries[str(rid)] = summary

    if not explanation:
        explanation = (
            "These restaurants were selected based on your preferences, "
            "and the AI provided concise summaries for each one."
        )

    return explanation, summaries


__all__ = ["parse_gemini_response"]

