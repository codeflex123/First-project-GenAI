from __future__ import annotations

from src.observability.metrics import get_metrics_store, get_metrics_snapshot


def test_request_metrics_tracking():
  store = get_metrics_store()

  # Simulate two successful requests and one failing.
  with store.track_request("/test"):
    pass
  try:
    with store.track_request("/test"):
      raise RuntimeError("boom")
  except RuntimeError:
    pass

  snap = get_metrics_snapshot()
  assert snap["requests"]["total"] >= 2
  assert snap["requests"]["per_path"]["/test"] >= 2


def test_llm_metrics_tracking():
  store = get_metrics_store()

  with store.track_llm_call():
    pass
  try:
    with store.track_llm_call():
      raise RuntimeError("fail")
  except RuntimeError:
    pass

  snap = get_metrics_snapshot()
  assert snap["llm"]["total_calls"] >= 2
  assert snap["llm"]["failures"] >= 1

