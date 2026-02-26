from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Resolve to the `src` directory (where `.env` lives)
SRC_DIR = Path(__file__).resolve().parents[1]
# Load environment variables from src/.env if present so GEMINI_API_KEY and others
# are available when the app starts (including for manual tests).
load_dotenv(SRC_DIR / ".env", override=False)

@dataclass
class AppConfig:
    """Phase 0 application configuration."""

    env: str
    port: int
    log_level: str
    hf_token: Optional[str]
    gemini_api_key: Optional[str]
    enable_gemini: bool
    gemini_timeout_seconds: float


def _get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(name)
    return value if value is not None else default


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _get_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _get_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def load_config() -> AppConfig:
    """Load configuration from environment variables with sensible defaults."""

    env = _get_env("APP_ENV", "development") or "development"
    port = _get_int("APP_PORT", 8000)
    log_level = (_get_env("LOG_LEVEL", "INFO") or "INFO").upper()

    hf_token = _get_env("HF_TOKEN") or _get_env("HUGGINGFACE_TOKEN")
    gemini_api_key = _get_env("GEMINI_API_KEY")
    enable_gemini = _get_bool("ENABLE_GEMINI", False)
    gemini_timeout_seconds = _get_float("GEMINI_TIMEOUT_SECONDS", 8.0)

    return AppConfig(
        env=env,
        port=port,
        log_level=log_level,
        hf_token=hf_token,
        gemini_api_key=gemini_api_key,
        enable_gemini=enable_gemini,
        gemini_timeout_seconds=gemini_timeout_seconds,
    )


__all__ = ["AppConfig", "load_config"]

