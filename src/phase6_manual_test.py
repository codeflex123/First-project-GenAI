from __future__ import annotations

from fastapi.testclient import TestClient

from src.api import create_app
from src.utils.logger import configure_logging, get_logger


def main() -> None:
    """
    Manual test for Phase 6: observability & metrics.

    - Sends some sample requests.
    - Fetches /metrics and prints the snapshot.

    Usage:
        python -m src.phase6_manual_test
    """

    configure_logging("INFO")
    log = get_logger("phase6")

    app = create_app()
    client = TestClient(app)

    # Generate some traffic.
    log.info("Sending sample /health and /metrics requests...")
    client.get("/health")
    client.get("/health")
    client.get("/metrics")

    resp = client.get("/metrics")

    print("=== Phase 6 Manual Test: /metrics ===")
    print(f"Status code: {resp.status_code}")
    if not resp.ok:
        print("Body:")
        print(resp.text)
        print("=== End of Phase 6 Manual Test ===")
        return

    data = resp.json()
    print("Metrics snapshot:")
    print(data)
    print("=== End of Phase 6 Manual Test ===")


if __name__ == "__main__":  # pragma: no cover
    main()

