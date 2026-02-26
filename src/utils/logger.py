from __future__ import annotations

import logging
from typing import Optional


def configure_logging(level: str = "INFO") -> None:
    """
    Configure root logging for the application.

    Phase 0 keeps this simple: a single console handler with a concise format.
    """

    numeric_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a logger with the given name."""

    return logging.getLogger(name or __name__)


__all__ = ["configure_logging", "get_logger"]

