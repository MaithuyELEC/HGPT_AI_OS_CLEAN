"""Capability declaration and negotiation contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, runtime_checkable

from .diagnostics_contract import ContractError, PlatformErrorCode

CONTRACT_VERSION = "2.0.0"
CONTRACT_LIFECYCLE = ("declared", "validated", "negotiated", "granted", "revoked")
EXTENSION_RULES = (
    "Capability names must be stable strings.",
    "Requirements must state whether they are optional or required.",
    "Negotiation errors must use the unified platform error taxonomy.",
)
BACKWARD_COMPATIBILITY_NOTES = (
    "Capability contracts are additive across the 2.x platform line.",
    "Older hosts must reject unknown required capabilities and may ignore optional ones.",
)


class CapabilityStatus(str, Enum):
    DECLARED = "declared"
    GRANTED = "granted"
    DENIED = "denied"
    REVOKED = "revoked"


@dataclass(frozen=True)
class Capability:
    name: str
    version: str = CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(("Capability.name", self.name), ("Capability.version", self.version))


@dataclass(frozen=True)
class CapabilityRequirement:
    capability: Capability
    required: bool = True
    reason: str = ""

    def validate(self) -> tuple[ContractError, ...]:
        return self.capability.validate()


@dataclass(frozen=True)
class CapabilityGrant:
    capability: Capability
    status: CapabilityStatus = CapabilityStatus.DECLARED
    errors: tuple[ContractError, ...] = ()

    def validate(self) -> tuple[ContractError, ...]:
        return self.capability.validate()


@runtime_checkable
class CapabilityProvider(Protocol):
    def capabilities(self) -> tuple[Capability, ...]:
        """Return capabilities declared by a component."""


class CapabilityNegotiator(ABC):
    @abstractmethod
    def negotiate(self, requirements: tuple[CapabilityRequirement, ...]) -> tuple[CapabilityGrant, ...]:
        """Resolve capability requirements into grants or denials."""


def _require_text(*fields: tuple[str, str]) -> tuple[ContractError, ...]:
    return tuple(_validation_error(f"{name} is required") for name, value in fields if not value.strip())


def _validation_error(message: str) -> ContractError:
    return ContractError(PlatformErrorCode.CONTRACT_VALIDATION_FAILED, message, source="capability_contract")
