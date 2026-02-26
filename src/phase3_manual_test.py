from __future__ import annotations

from fastapi.testclient import TestClient

from src.api import create_app
from src.utils.logger import configure_logging, get_logger


def main() -> None:
    """
    Manual test for Phase 3: API design & request handling (without Gemini).

    This runs the FastAPI app in-process using TestClient, sends a sample
    /api/recommendations request, and prints the JSON response.

    Usage:
        # (optional) export HF_TOKEN=... if your dataset needs auth
        python -m src.phase3_manual_test
    """

    configure_logging("INFO")
    log = get_logger("phase3")

    app = create_app()
    client = TestClient(app)

    payload = {
        "city": None,  # e.g. "New Delhi"
        "price_range": 3,
        "min_rating": 4.0,
        "cuisines": ["Italian", "Pizza"],
        "max_results": 5,
    }

    log.info("Sending sample Phase 3 request to /api/recommendations: %s", payload)
    response = client.post("/api/recommendations", json=payload)

    print("=== Phase 3 Manual Test: /api/recommendations ===")
    print(f"Status code: {response.status_code}")

    if not response.ok:
        print("Error body:")
        print(response.text)
        print("=== End of Phase 3 Manual Test ===")
        return

    data = response.json()
    print("Response JSON:")
    print(data)
    print("=== End of Phase 3 Manual Test ===")


if __name__ == "__main__":  # pragma: no cover
    main()

