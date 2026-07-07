"""Planner intent and task graph contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, runtime_checkable

from .diagnostics_contract import ContractError, PlatformErrorCode

CONTRACT_VERSION = "2.0.0"
CONTRACT_LIFECYCLE = ("received", "interpreted", "planned", "validated", "returned")
EXTENSION_RULES = (
    "Planner outputs must preserve Intent, Plan, TaskGraph, and PlannerResult shapes.",
    "Task dependencies must reference task identifiers in the same graph.",
    "Planner-specific scoring belongs in metadata mappings.",
)
BACKWARD_COMPATIBILITY_NOTES = (
    "Planner contracts do not replace current planner validators.",
    "Older hosts may ignore PlannerResult.metadata while preserving plan and errors.",
)


class IntentKind(str, Enum):
    GENERATE = "generate"
    SEARCH = "search"
    TRANSFORM = "transform"
    DIAGNOSE = "diagnose"
    EXECUTE = "execute"


@dataclass(frozen=True)
class Intent:
    intent_id: str
    kind: IntentKind
    text: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(("Intent.intent_id", self.intent_id), ("Intent.text", self.text))


@dataclass(frozen=True)
class PlanTask:
    task_id: str
    description: str
    depends_on: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(("PlanTask.task_id", self.task_id), ("PlanTask.description", self.description))


@dataclass(frozen=True)
class TaskGraph:
    graph_id: str
    tasks: tuple[PlanTask, ...] = ()

    def validate(self) -> tuple[ContractError, ...]:
        errors = list(_require_text(("TaskGraph.graph_id", self.graph_id)))
        task_ids = {task.task_id for task in self.tasks}
        for task in self.tasks:
            errors.extend(task.validate())
            for dependency in task.depends_on:
                if dependency not in task_ids:
                    errors.append(_validation_error(f"PlanTask dependency is missing: {dependency}"))
        return tuple(errors)


@dataclass(frozen=True)
class Plan:
    plan_id: str
    intent: Intent
    graph: TaskGraph
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return (*_require_text(("Plan.plan_id", self.plan_id)), *self.intent.validate(), *self.graph.validate())


@dataclass(frozen=True)
class PlannerResult:
    intent: Intent
    plan: Plan | None = None
    errors: tuple[ContractError, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        errors = list(self.intent.validate())
        if self.plan is not None:
            errors.extend(self.plan.validate())
        return tuple(errors)


@runtime_checkable
class IntentClassifier(Protocol):
    def classify(self, text: str) -> Intent:
        """Return a typed intent for caller text."""


class Planner(ABC):
    @abstractmethod
    def plan(self, intent: Intent) -> PlannerResult:
        """Return a plan result for a validated intent."""

    @abstractmethod
    def validate(self, plan: Plan) -> tuple[ContractError, ...]:
        """Validate a plan before execution."""


def _require_text(*fields: tuple[str, str]) -> tuple[ContractError, ...]:
    return tuple(_validation_error(f"{name} is required") for name, value in fields if not value.strip())


def _validation_error(message: str) -> ContractError:
    return ContractError(PlatformErrorCode.CONTRACT_VALIDATION_FAILED, message, source="planner_contract")
