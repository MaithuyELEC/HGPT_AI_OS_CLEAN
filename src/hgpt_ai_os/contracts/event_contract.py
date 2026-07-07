"""Platform event contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, runtime_checkable

from .diagnostics_contract import ContractError, PlatformErrorCode

CONTRACT_VERSION = "2.0.0"
CONTRACT_LIFECYCLE = ("created", "published", "delivered", "acknowledged", "failed")
EXTENSION_RULES = (
    "Events must include stable identifiers, type names, and source names.",
    "Event payloads must be immutable from the consumer perspective.",
    "Unknown event types must be safely ignored by older consumers.",
)
BACKWARD_COMPATIBILITY_NOTES = (
    "Event contracts do not replace current core event utilities.",
    "New event types are additive within the 2.x contract line.",
)


class EventType(str, Enum):
    LIFECYCLE = "lifecycle"
    JOB = "job"
    PROVIDER = "provider"
    WORKFLOW = "workflow"
    DIAGNOSTIC = "diagnostic"


@dataclass(frozen=True)
class PlatformEvent:
    event_id: str
    event_type: EventType
    source: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    correlation_id: str | None = None

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(("PlatformEvent.event_id", self.event_id), ("PlatformEvent.source", self.source))


@dataclass(frozen=True)
class EventSubscription:
    subscriber_id: str
    event_types: tuple[EventType, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(("EventSubscription.subscriber_id", self.subscriber_id))


@dataclass(frozen=True)
class EventDelivery:
    event: PlatformEvent
    delivered: bool
    errors: tuple[ContractError, ...] = ()

    def validate(self) -> tuple[ContractError, ...]:
        return self.event.validate()


@runtime_checkable
class EventHandler(Protocol):
    def handle(self, event: PlatformEvent) -> None:
        """Handle a platform event."""


class EventBus(ABC):
    @abstractmethod
    def publish(self, event: PlatformEvent) -> EventDelivery:
        """Publish an event to subscribers."""

    @abstractmethod
    def subscribe(self, subscription: EventSubscription, handler: EventHandler) -> None:
        """Subscribe a handler to platform events."""


def _require_text(*fields: tuple[str, str]) -> tuple[ContractError, ...]:
    return tuple(_validation_error(f"{name} is required") for name, value in fields if not value.strip())


def _validation_error(message: str) -> ContractError:
    return ContractError(PlatformErrorCode.CONTRACT_VALIDATION_FAILED, message, source="event_contract")
