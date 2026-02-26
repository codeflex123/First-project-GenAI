from __future__ import annotations

import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class RequestMetrics:
    total_requests: int = 0
    total_errors: int = 0
    total_latency_ms: float = 0.0

    per_path_requests: Dict[str, int] = field(default_factory=dict)


@dataclass
class LlmMetrics:
    total_calls: int = 0
    total_failures: int = 0


class _MetricsStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.requests = RequestMetrics()
        self.llm = LlmMetrics()

    @contextmanager
    def track_request(self, path: str):
        start = time.time()
        error_occurred = False
        try:
            with self._lock:
                self.requests.total_requests += 1
                self.requests.per_path_requests[path] = (
                    self.requests.per_path_requests.get(path, 0) + 1
                )
            yield
        except Exception:
            error_occurred = True
            with self._lock:
                self.requests.total_errors += 1
            raise
        finally:
            duration_ms = (time.time() - start) * 1000.0
            with self._lock:
                self.requests.total_latency_ms += duration_ms
                if error_occurred:
                    self.requests.total_errors += 0  # already incremented

    @contextmanager
    def track_llm_call(self):
        with self._lock:
            self.llm.total_calls += 1
        try:
            yield
        except Exception:
            with self._lock:
                self.llm.total_failures += 1
            raise

    def snapshot(self) -> dict:
        with self._lock:
            avg_latency = (
                self.requests.total_latency_ms / self.requests.total_requests
                if self.requests.total_requests
                else 0.0
            )
            return {
                "requests": {
                    "total": self.requests.total_requests,
                    "errors": self.requests.total_errors,
                    "average_latency_ms": round(avg_latency, 2),
                    "per_path": dict(self.requests.per_path_requests),
                },
                "llm": {
                    "total_calls": self.llm.total_calls,
                    "failures": self.llm.total_failures,
                },
            }


_STORE = _MetricsStore()


def get_metrics_store() -> _MetricsStore:
    return _STORE


def get_metrics_snapshot() -> dict:
    return _STORE.snapshot()


__all__ = ["get_metrics_store", "get_metrics_snapshot"]

