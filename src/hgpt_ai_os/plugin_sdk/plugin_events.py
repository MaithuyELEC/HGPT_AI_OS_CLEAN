"""Plugin event records and in-memory event bus."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from time import time
from typing import Any, Mapping


class PluginEventType(str, Enum):
    INSTALLED = "installed"
    UPDATED = "updated"
    ENABLED = "enabled"
    DISABLED = "disabled"
    REMOVED = "removed"


@dataclass(frozen=True)
class PluginEvent:
    event_type: PluginEventType
    plugin_id: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time)


class PluginEventBus:
    def __init__(self) -> None:
        self._subscribers: dict[PluginEventType, list[Callable[[PluginEvent], None]]] = {}
        self._history: list[PluginEvent] = []

    def subscribe(self, event_type: PluginEventType, callback: Callable[[PluginEvent], None]) -> None:
        self._subscribers.setdefault(event_type, []).append(callback)

    def emit(
        self,
        event_type: PluginEventType,
        plugin_id: str,
        payload: Mapping[str, Any] | None = None,
    ) -> PluginEvent:
        event = PluginEvent(event_type, plugin_id, payload or {})
        self._history.append(event)
        for callback in tuple(self._subscribers.get(event_type, ())):
            callback(event)
        return event

    def history(self, event_type: PluginEventType | None = None) -> tuple[PluginEvent, ...]:
        if event_type is None:
            return tuple(self._history)
        return tuple(event for event in self._history if event.event_type is event_type)
