"""Runtime execution context values."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class ExecutionContext:
    runtime_id: str = field(default_factory=lambda: str(uuid4()))
    correlation_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def child(self, **metadata: Any) -> "ExecutionContext":
        merged = dict(self.metadata)
        merged.update(metadata)
        return ExecutionContext(correlation_id=self.correlation_id, metadata=merged)
