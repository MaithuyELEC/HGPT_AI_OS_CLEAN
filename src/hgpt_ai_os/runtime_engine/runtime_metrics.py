"""Runtime execution counters and elapsed-time accounting."""

from __future__ import annotations

from dataclasses import dataclass
from time import monotonic


@dataclass
class RuntimeMetrics:
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    retry_count: int = 0
    _started_at: float | None = None
    elapsed_time: float = 0.0

    def start_timer(self) -> None:
        if self._started_at is None:
            self._started_at = monotonic()

    def stop_timer(self) -> None:
        if self._started_at is not None:
            self.elapsed_time += monotonic() - self._started_at
            self._started_at = None

    def record_execution(self) -> None:
        self.execution_count += 1

    def record_success(self) -> None:
        self.success_count += 1

    def record_failure(self) -> None:
        self.failure_count += 1

    def record_retry(self) -> None:
        self.retry_count += 1

    def snapshot(self) -> dict[str, int | float]:
        elapsed = self.elapsed_time
        if self._started_at is not None:
            elapsed += monotonic() - self._started_at
        return {
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "retry_count": self.retry_count,
            "elapsed_time": elapsed,
        }
