"""Platform request contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, runtime_checkable

from .diagnostics_contract import ContractError, PlatformErrorCode

CONTRACT_VERSION = "2.0.0"
CONTRACT_LIFECYCLE = ("created", "validated", "authorized", "dispatched", "completed", "rejected")
EXTENSION_RULES = (
    "Requests must preserve request_id, requester, and operation fields.",
    "Request payloads must be serializable mappings.",
    "Authorization decisions must use ContractError for denials.",
)
BACKWARD_COMPATIBILITY_NOTES = (
    "Request contracts do not modify current CLI, GUI, or service request paths.",
    "Older dispatchers may reject unknown operations with CONTRACT_VALIDATION_FAILED.",
)


class RequestPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


@dataclass(frozen=True)
class PlatformRequest:
    request_id: str
    requester: str
    operation: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    priority: RequestPriority = RequestPriority.NORMAL
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(
            ("PlatformRequest.request_id", self.request_id),
            ("PlatformRequest.requester", self.requester),
            ("PlatformRequest.operation", self.operation),
        )


@dataclass(frozen=True)
class RequestEnvelope:
    request: PlatformRequest
    correlation_id: str | None = None
    errors: tuple[ContractError, ...] = ()

    def validate(self) -> tuple[ContractError, ...]:
        return self.request.validate()


@runtime_checkable
class RequestAuthorizer(Protocol):
    def authorize(self, request: PlatformRequest) -> tuple[ContractError, ...]:
        """Return authorization errors for a request."""


class RequestDispatcher(ABC):
    @abstractmethod
    def dispatch(self, envelope: RequestEnvelope) -> None:
        """Dispatch a validated request envelope."""

    @abstractmethod
    def validate(self, request: PlatformRequest) -> tuple[ContractError, ...]:
        """Validate a request before dispatch."""


def _require_text(*fields: tuple[str, str]) -> tuple[ContractError, ...]:
    return tuple(_validation_error(f"{name} is required") for name, value in fields if not value.strip())


def _validation_error(message: str) -> ContractError:
    return ContractError(PlatformErrorCode.CONTRACT_VALIDATION_FAILED, message, source="request_contract")
