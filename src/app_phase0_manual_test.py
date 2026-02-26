from __future__ import annotations

from src.config import load_config
from src.utils.logger import configure_logging, get_logger


def main() -> None:
    """
    Manual test for Phase 0: configuration & logging foundations.

    Usage:
        python -m src.app_phase0_manual_test
    """

    cfg = load_config()
    configure_logging(cfg.log_level)
    log = get_logger("phase0")

    log.info("Starting Phase 0 manual test")
    log.info("Environment: %s", cfg.env)
    log.info("Port: %s", cfg.port)
    log.info("Log level: %s", cfg.log_level)
    log.info("HF token present: %s", bool(cfg.hf_token))
    log.info("Gemini API key present: %s", bool(cfg.gemini_api_key))

    print("=== Phase 0 Manual Test Summary ===")
    print(f"env={cfg.env}")
    print(f"port={cfg.port}")
    print(f"log_level={cfg.log_level}")
    print(f"hf_token_present={bool(cfg.hf_token)}")
    print(f"gemini_api_key_present={bool(cfg.gemini_api_key)}")
    print("===================================")


if __name__ == "__main__":  # pragma: no cover
    main()

