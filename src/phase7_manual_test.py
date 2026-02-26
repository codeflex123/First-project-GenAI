from __future__ import annotations

from fastapi.testclient import TestClient

from src.api import create_app
from src.utils.logger import configure_logging, get_logger


def main() -> None:
    """
    Manual test for Phase 7: feedback collection & evaluation.

    - Sends a sample feedback payload to /api/feedback.
    - Prints the aggregated snapshot returned by the API.

    Usage:
        python -m src.phase7_manual_test
    """

    configure_logging("INFO")
    log = get_logger("phase7")

    app = create_app()
    client = TestClient(app)

    payload = {
        "restaurant_id": "demo-restaurant",
        "liked": True,
        "variant": "gemini",
        "reason": "Great suggestion for my preferences.",
    }

    log.info("Sending feedback: %s", payload)
    resp = client.post("/api/feedback", json=payload)

    print("=== Phase 7 Manual Test: /api/feedback ===")
    print(f"Status code: {resp.status_code}")
    if not resp.ok:
        print("Body:")
        print(resp.text)
        print("=== End of Phase 7 Manual Test ===")
        return

    data = resp.json()
    print("Response JSON:")
    print(data)
    print("=== End of Phase 7 Manual Test ===")


if __name__ == "__main__":  # pragma: no cover
    main()

