from __future__ import annotations

import os
from typing import Dict, List, Tuple, Optional

import google.generativeai as genai
from google.api_core.exceptions import NotFound

from src.data.models import Restaurant
from src.llm.prompts import build_recommendation_prompt
from src.llm.parser import parse_gemini_response
from src.services.restaurant_query_service import UserPreferences


def _get_gemini_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set in the environment.")
    return api_key


def _configure_gemini() -> None:
    api_key = _get_gemini_api_key()
    genai.configure(api_key=api_key)


def _pick_supported_model(preferred: Optional[str] = None) -> str:
    """
    Pick a model name that is available for this API key and supports generateContent.

    The google-generativeai library uses the Generative Language v1beta API under the hood.
    Model availability varies by account/project, so we auto-discover models rather than
    hardcoding one that might 404.
    """

    # If user explicitly provided a model name, try it first.
    if preferred:
        return preferred

    preferred_order = [
        "models/gemini-1.5-flash",
        "models/gemini-1.5-pro",
        "models/gemini-1.0-pro",
        "models/gemini-pro",
    ]

    try:
        models = list(genai.list_models())
    except Exception:
        # If model listing fails for any reason, fall back to a commonly available name.
        return "models/gemini-pro"

    # Keep only models that support generateContent.
    supported = []
    for m in models:
        name = getattr(m, "name", None)
        methods = getattr(m, "supported_generation_methods", None) or []
        if name and "generateContent" in methods:
            supported.append(name)

    for candidate in preferred_order:
        if candidate in supported:
            return candidate

    # Fallback to the first supported model.
    if supported:
        return supported[0]

    # Last-resort fallback.
    return "models/gemini-pro"


def call_gemini_for_recommendations(
    prefs: UserPreferences,
    restaurants: List[Restaurant],
    model_name: str = "models/gemini-1.5-flash",
) -> Tuple[str, Dict[str, str]]:
    """
    High-level Phase 4 API for Gemini:
    - Builds a prompt from user preferences + candidate restaurants.
    - Calls Gemini.
    - Parses the JSON response into (explanation, summaries_by_id).
    """

    if not restaurants:
        return "No restaurants matched the given filters.", {}

    _configure_gemini()
    prompt = build_recommendation_prompt(prefs, restaurants)

    # Allow overriding via GEMINI_MODEL_NAME (can be full "models/..." name).
    env_model = os.getenv("GEMINI_MODEL_NAME")
    model_id = _pick_supported_model(env_model or model_name)

    # Try once; if the model 404s, auto-pick another supported model and retry.
    try:
        model = genai.GenerativeModel(model_id)
        try:
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"},
            )
        except TypeError:
            # Older SDKs may not accept generation_config as a dict.
            response = model.generate_content(prompt)
    except NotFound:
        model_id = _pick_supported_model()
        model = genai.GenerativeModel(model_id)
        try:
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"},
            )
        except TypeError:
            response = model.generate_content(prompt)

    # Support both `.text` and candidates/parts style responses.
    if hasattr(response, "text") and isinstance(response.text, str):
        raw_text = response.text
    else:
        # Fallback: concatenate text parts from the first candidate.
        raw_text = ""
        try:
            candidate = response.candidates[0]
            parts = getattr(candidate, "content", candidate).parts  # type: ignore[attr-defined]
            raw_text = "".join(getattr(p, "text", "") for p in parts)
        except Exception:  # pragma: no cover - extremely defensive
            raw_text = ""

    return parse_gemini_response(raw_text, restaurants)


__all__ = ["call_gemini_for_recommendations"]

