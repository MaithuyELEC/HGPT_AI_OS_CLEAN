"""Retry policy modeling for runtime-managed work."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 1.0
    multiplier: float = 2.0
    max_delay_seconds: float = 60.0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if self.base_delay_seconds < 0:
            raise ValueError("base_delay_seconds cannot be negative")
        if self.multiplier < 1:
            raise ValueError("multiplier must be at least 1")
        if self.max_delay_seconds < self.base_delay_seconds:
            raise ValueError("max_delay_seconds must be greater than or equal to base_delay_seconds")


@dataclass(frozen=True)
class RetryDecision:
    should_retry: bool
    attempt: int
    delay_seconds: float
    reason: str


class RetryManager:
    """Calculates retry eligibility and exponential backoff delays."""

    def __init__(self, policy: RetryPolicy | None = None) -> None:
        self.policy = policy or RetryPolicy()

    def evaluate(self, attempt: int, error: Exception | str | None = None) -> RetryDecision:
        if attempt < 1:
            raise ValueError("attempt must be at least 1")
        if attempt >= self.policy.max_attempts:
            return RetryDecision(False, attempt, 0.0, "maximum retry attempts reached")
        delay = min(
            self.policy.base_delay_seconds * (self.policy.multiplier ** (attempt - 1)),
            self.policy.max_delay_seconds,
        )
        reason = str(error) if error is not None else "retry permitted"
        return RetryDecision(True, attempt + 1, delay, reason)
