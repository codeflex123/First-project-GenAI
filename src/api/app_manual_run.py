from __future__ import annotations

import uvicorn

from src.api import app
from src.config import load_config


def main() -> None:
    """
    Helper script to run the FastAPI app for manual testing.

    Usage:
        python -m src.api.app_manual_run
    Then open:
        http://127.0.0.1:8000/docs
    """

    cfg = load_config()
    port = cfg.port or 8000

    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":  # pragma: no cover
    main()

