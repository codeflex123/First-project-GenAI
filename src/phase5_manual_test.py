from __future__ import annotations

from fastapi.testclient import TestClient

from src.api import create_app
from src.utils.logger import configure_logging, get_logger


def main() -> None:
    """
    Manual test for Phase 5: frontend integration.

    This does a lightweight check that the HTML UI is served correctly
    and prints a short snippet of the page.

    Usage:
        python -m src.phase5_manual_test

    For a full manual test, run:
        python -m src.api.app_manual_run
    then open http://127.0.0.1:8000/ in your browser.
    """

    configure_logging("INFO")
    log = get_logger("phase5")

    app = create_app()
    client = TestClient(app)

    resp = client.get("/")
    log.info("GET / returned status %s", resp.status_code)

    print("=== Phase 5 Manual Test: Frontend ===")
    print(f"Status code: {resp.status_code}")
    if not resp.ok:
        print("Body:")
        print(resp.text)
        print("=== End of Phase 5 Manual Test ===")
        return

    text = resp.text
    print("First 400 characters of HTML:")
    print(text[:400])
    print("\n(If you see a valid HTML page snippet, the frontend is being served.)")
    print("=== End of Phase 5 Manual Test ===")


if __name__ == "__main__":  # pragma: no cover
    main()

