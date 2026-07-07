"""Agent execution contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, runtime_checkable

from .diagnostics_contract import ContractError, PlatformErrorCode

CONTRACT_VERSION = "2.0.0"
CONTRACT_LIFECYCLE = ("registered", "authorized", "prepared", "executing", "completed", "failed")
EXTENSION_RULES = (
    "Agents must declare permissions before execution.",
    "Memory access must be scoped by AgentContext.memory_scope.",
    "Approval behavior must be explicit and auditable.",
)
BACKWARD_COMPATIBILITY_NOTES = (
    "Agent contracts are additive and do not alter existing agent modules.",
    "New permission values must be treated as denied by older hosts.",
)


class AgentPermission(str, Enum):
    READ_CONTEXT = "read_context"
    WRITE_OUTPUT = "write_output"
    READ_MEMORY = "read_memory"
    WRITE_MEMORY = "write_memory"
    USE_PROVIDER = "use_provider"
    USE_TOOL = "use_tool"


class ApprovalPolicy(str, Enum):
    NEVER = "never"
    ON_RISK = "on_risk"
    ALWAYS = "always"


class MemoryScope(str, Enum):
    NONE = "none"
    SESSION = "session"
    PROJECT = "project"
    KNOWLEDGE = "knowledge"


@dataclass(frozen=True)
class AgentContext:
    agent_id: str
    session_id: str
    permissions: tuple[AgentPermission, ...] = ()
    approval_policy: ApprovalPolicy = ApprovalPolicy.ON_RISK
    memory_scope: MemoryScope = MemoryScope.SESSION
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(("AgentContext.agent_id", self.agent_id), ("AgentContext.session_id", self.session_id))


@dataclass(frozen=True)
class AgentExecution:
    execution_id: str
    intent: str
    context: AgentContext
    inputs: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return (*_require_text(("AgentExecution.execution_id", self.execution_id), ("AgentExecution.intent", self.intent)), *self.context.validate())


@dataclass(frozen=True)
class AgentResult:
    execution_id: str
    success: bool
    output: Mapping[str, Any] = field(default_factory=dict)
    errors: tuple[ContractError, ...] = ()

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(("AgentResult.execution_id", self.execution_id))


@runtime_checkable
class AgentRuntimeView(Protocol):
    def request_approval(self, execution: AgentExecution) -> bool:
        """Ask the host whether an execution requiring approval may proceed."""


class Agent(ABC):
    @property
    @abstractmethod
    def agent_id(self) -> str:
        """Return the stable agent identifier."""

    @abstractmethod
    def permissions(self) -> tuple[AgentPermission, ...]:
        """Return permissions required by this agent."""

    @abstractmethod
    def execute(self, execution: AgentExecution) -> AgentResult:
        """Execute an agent request within the supplied context."""


def _require_text(*fields: tuple[str, str]) -> tuple[ContractError, ...]:
    return tuple(_validation_error(f"{name} is required") for name, value in fields if not value.strip())


def _validation_error(message: str) -> ContractError:
    return ContractError(PlatformErrorCode.CONTRACT_VALIDATION_FAILED, message, source="agent_contract")
