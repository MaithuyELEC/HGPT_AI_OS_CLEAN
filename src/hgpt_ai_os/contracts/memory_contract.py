"""Memory scope contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, runtime_checkable

from .diagnostics_contract import ContractError, PlatformErrorCode

CONTRACT_VERSION = "2.0.0"
CONTRACT_LIFECYCLE = ("created", "read", "written", "compacted", "expired", "deleted")
EXTENSION_RULES = (
    "Memory records must remain scoped to their declared memory type.",
    "Persistent memory must expose retention metadata.",
    "Unknown metadata must not change access decisions.",
)
BACKWARD_COMPATIBILITY_NOTES = (
    "Memory contracts do not migrate current memory stores.",
    "Older hosts must reject writes to unknown memory scopes.",
)


class MemoryRetention(str, Enum):
    EPHEMERAL = "ephemeral"
    SESSION = "session"
    PROJECT = "project"
    KNOWLEDGE = "knowledge"


@dataclass(frozen=True)
class ConversationMemory:
    memory_id: str
    conversation_id: str
    content: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(
            ("ConversationMemory.memory_id", self.memory_id),
            ("ConversationMemory.conversation_id", self.conversation_id),
        )


@dataclass(frozen=True)
class SessionMemory:
    memory_id: str
    session_id: str
    retention: MemoryRetention = MemoryRetention.SESSION
    content: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(("SessionMemory.memory_id", self.memory_id), ("SessionMemory.session_id", self.session_id))


@dataclass(frozen=True)
class ProjectMemory:
    memory_id: str
    project_id: str
    retention: MemoryRetention = MemoryRetention.PROJECT
    content: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(("ProjectMemory.memory_id", self.memory_id), ("ProjectMemory.project_id", self.project_id))


@dataclass(frozen=True)
class KnowledgeMemory:
    memory_id: str
    package_id: str
    retention: MemoryRetention = MemoryRetention.KNOWLEDGE
    content: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(("KnowledgeMemory.memory_id", self.memory_id), ("KnowledgeMemory.package_id", self.package_id))


@runtime_checkable
class MemoryReader(Protocol):
    def read(self, memory_id: str) -> Mapping[str, Any]:
        """Read memory content by stable identifier."""


class MemoryStore(ABC):
    @abstractmethod
    def write_session(self, memory: SessionMemory) -> tuple[ContractError, ...]:
        """Write session-scoped memory after validation."""

    @abstractmethod
    def write_project(self, memory: ProjectMemory) -> tuple[ContractError, ...]:
        """Write project-scoped memory after validation."""

    @abstractmethod
    def delete(self, memory_id: str) -> tuple[ContractError, ...]:
        """Delete memory by stable identifier."""


def _require_text(*fields: tuple[str, str]) -> tuple[ContractError, ...]:
    return tuple(_validation_error(f"{name} is required") for name, value in fields if not value.strip())


def _validation_error(message: str) -> ContractError:
    return ContractError(PlatformErrorCode.CONTRACT_VALIDATION_FAILED, message, source="memory_contract")
