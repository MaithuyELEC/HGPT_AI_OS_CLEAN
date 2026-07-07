"""Platform result contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, runtime_checkable

from .diagnostics_contract import ContractError, PlatformErrorCode

CONTRACT_VERSION = "2.0.0"
CONTRACT_LIFECYCLE = ("created", "validated", "stored", "delivered", "expired")
EXTENSION_RULES = (
    "Results must include a stable result identifier and producer name.",
    "Result data must be carried as serializable mappings.",
    "Errors must use the unified diagnostics contract taxonomy.",
)
BACKWARD_COMPATIBILITY_NOTES = (
    "Result contracts do not change existing production result objects.",
    "Older consumers must preserve result_id, producer, success, and errors.",
)


class ResultStatus(str, Enum):
    CREATED = "created"
    VALIDATED = "validated"
    STORED = "stored"
    DELIVERED = "delivered"
    FAILED = "failed"


@dataclass(frozen=True)
class PlatformResult:
    result_id: str
    producer: str
    success: bool
    status: ResultStatus = ResultStatus.CREATED
    data: Mapping[str, Any] = field(default_factory=dict)
    errors: tuple[ContractError, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(("PlatformResult.result_id", self.result_id), ("PlatformResult.producer", self.producer))


@dataclass(frozen=True)
class ResultReference:
    result_id: str
    locator: str
    media_type: str = "application/octet-stream"

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(("ResultReference.result_id", self.result_id), ("ResultReference.locator", self.locator))


@runtime_checkable
class ResultConsumer(Protocol):
    def consume(self, result: PlatformResult) -> None:
        """Consume a validated platform result."""


class ResultStore(ABC):
    @abstractmethod
    def store(self, result: PlatformResult) -> ResultReference:
        """Store a platform result and return a stable reference."""

    @abstractmethod
    def load(self, reference: ResultReference) -> PlatformResult:
        """Load a platform result from a stable reference."""


def _require_text(*fields: tuple[str, str]) -> tuple[ContractError, ...]:
    return tuple(_validation_error(f"{name} is required") for name, value in fields if not value.strip())


def _validation_error(message: str) -> ContractError:
    return ContractError(PlatformErrorCode.CONTRACT_VALIDATION_FAILED, message, source="result_contract")
