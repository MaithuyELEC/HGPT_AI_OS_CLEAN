"""Skill boundary contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, runtime_checkable

from .diagnostics_contract import ContractError, PlatformErrorCode

CONTRACT_VERSION = "2.0.0"
CONTRACT_LIFECYCLE = ("discovered", "loaded", "validated", "available", "disabled")
EXTENSION_RULES = (
    "Skills must publish capabilities before invocation.",
    "Skill inputs and outputs must remain serializable mappings.",
    "Host-specific state belongs in SkillContext.metadata.",
)
BACKWARD_COMPATIBILITY_NOTES = (
    "Skill contracts do not change existing content builders or agents.",
    "Unknown capabilities must be ignored by older hosts.",
)


class SkillCapability(str, Enum):
    READ = "read"
    WRITE = "write"
    TRANSFORM = "transform"
    ANALYZE = "analyze"
    GENERATE = "generate"


@dataclass(frozen=True)
class SkillContext:
    skill_id: str
    caller_id: str
    capabilities: tuple[SkillCapability, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(("SkillContext.skill_id", self.skill_id), ("SkillContext.caller_id", self.caller_id))


@dataclass(frozen=True)
class SkillInput:
    input_id: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(("SkillInput.input_id", self.input_id))


@dataclass(frozen=True)
class SkillOutput:
    input_id: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    errors: tuple[ContractError, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(("SkillOutput.input_id", self.input_id))


@runtime_checkable
class SkillValidator(Protocol):
    def validate_input(self, skill_input: SkillInput) -> tuple[ContractError, ...]:
        """Validate skill input before invocation."""


class Skill(ABC):
    @property
    @abstractmethod
    def skill_id(self) -> str:
        """Return the stable skill identifier."""

    @abstractmethod
    def capabilities(self) -> tuple[SkillCapability, ...]:
        """Return supported skill capabilities."""

    @abstractmethod
    def invoke(self, context: SkillContext, skill_input: SkillInput) -> SkillOutput:
        """Invoke the skill through the stable contract."""


def _require_text(*fields: tuple[str, str]) -> tuple[ContractError, ...]:
    return tuple(_validation_error(f"{name} is required") for name, value in fields if not value.strip())


def _validation_error(message: str) -> ContractError:
    return ContractError(PlatformErrorCode.CONTRACT_VALIDATION_FAILED, message, source="skill_contract")
