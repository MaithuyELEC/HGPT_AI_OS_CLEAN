"""Workflow graph and execution contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, runtime_checkable

from .diagnostics_contract import ContractError, PlatformErrorCode

CONTRACT_VERSION = "2.0.0"
CONTRACT_LIFECYCLE = ("defined", "validated", "scheduled", "running", "completed", "failed")
EXTENSION_RULES = (
    "Workflow nodes must have stable node identifiers.",
    "Workflow execution state must be externally observable.",
    "Node-specific configuration belongs in metadata mappings.",
)
BACKWARD_COMPATIBILITY_NOTES = (
    "Workflow contracts are graph definitions only.",
    "Existing workflow modules are not modified by this contract package.",
)


class WorkflowExecutionState(str, Enum):
    DEFINED = "defined"
    VALIDATED = "validated"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class WorkflowNode:
    node_id: str
    kind: str
    depends_on: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(("WorkflowNode.node_id", self.node_id), ("WorkflowNode.kind", self.kind))


@dataclass(frozen=True)
class Workflow:
    workflow_id: str
    version: str
    nodes: tuple[WorkflowNode, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        errors = list(_require_text(("Workflow.workflow_id", self.workflow_id), ("Workflow.version", self.version)))
        node_ids = {node.node_id for node in self.nodes}
        for node in self.nodes:
            errors.extend(node.validate())
            for dependency in node.depends_on:
                if dependency not in node_ids:
                    errors.append(_validation_error(f"WorkflowNode dependency is missing: {dependency}"))
        return tuple(errors)


@dataclass(frozen=True)
class WorkflowContext:
    workflow_id: str
    execution_id: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(("WorkflowContext.workflow_id", self.workflow_id), ("WorkflowContext.execution_id", self.execution_id))


@dataclass(frozen=True)
class WorkflowExecution:
    context: WorkflowContext
    state: WorkflowExecutionState = WorkflowExecutionState.DEFINED
    current_node_id: str | None = None
    errors: tuple[ContractError, ...] = ()

    def validate(self) -> tuple[ContractError, ...]:
        return self.context.validate()


@runtime_checkable
class WorkflowStore(Protocol):
    def load(self, workflow_id: str) -> Workflow:
        """Load a workflow definition by stable identifier."""


class WorkflowRunner(ABC):
    @abstractmethod
    def validate(self, workflow: Workflow) -> tuple[ContractError, ...]:
        """Validate a workflow definition before execution."""

    @abstractmethod
    def execute(self, workflow: Workflow, context: WorkflowContext) -> WorkflowExecution:
        """Execute a workflow through the stable execution contract."""


def _require_text(*fields: tuple[str, str]) -> tuple[ContractError, ...]:
    return tuple(_validation_error(f"{name} is required") for name, value in fields if not value.strip())


def _validation_error(message: str) -> ContractError:
    return ContractError(PlatformErrorCode.CONTRACT_VALIDATION_FAILED, message, source="workflow_contract")
