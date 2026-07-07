"""In-process typed event bus for runtime orchestration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any
from uuid import uuid4


class RuntimeEventType(str, Enum):
    LIFECYCLE = "lifecycle"
    JOB = "job"
    TASK = "task"
    RETRY = "retry"
    HEALTH = "health"
    METRIC = "metric"


@dataclass(frozen=True)
class RuntimeEvent:
    event_type: RuntimeEventType
    source: str
    payload: dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def snapshot(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "source": self.source,
            "payload": dict(self.payload),
            "created_at": self.created_at.isoformat(),
        }


EventHandler = Callable[[RuntimeEvent], None]


class EventBus:
    """Synchronous local event bus with retained immutable history views."""

    def __init__(self) -> None:
        self._subscribers: dict[RuntimeEventType, list[EventHandler]] = {}
        self._history: list[RuntimeEvent] = []

    def subscribe(self, event_type: RuntimeEventType, handler: EventHandler) -> None:
        if not callable(handler):
            raise TypeError("event handler must be callable")
        self._subscribers.setdefault(event_type, []).append(handler)

    def publish(self, event: RuntimeEvent) -> RuntimeEvent:
        self._history.append(event)
        for handler in tuple(self._subscribers.get(event.event_type, ())):
            handler(event)
        return event

    def emit(self, event_type: RuntimeEventType, source: str, payload: dict[str, Any] | None = None) -> RuntimeEvent:
        return self.publish(RuntimeEvent(event_type=event_type, source=source, payload=dict(payload or {})))

    def history(self, event_type: RuntimeEventType | None = None) -> tuple[RuntimeEvent, ...]:
        if event_type is None:
            return tuple(self._history)
        return tuple(event for event in self._history if event.event_type is event_type)

    def subscriber_count(self) -> MappingProxyType[RuntimeEventType, int]:
        return MappingProxyType({event_type: len(handlers) for event_type, handlers in self._subscribers.items()})
