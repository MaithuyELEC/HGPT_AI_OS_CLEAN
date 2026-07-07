"""Runtime boundary contracts for LUCID PLATFORM."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, runtime_checkable

from .diagnostics_contract import ContractError, HealthReport, PlatformErrorCode

CONTRACT_VERSION = "2.0.0"
CONTRACT_LIFECYCLE = ("created", "configured", "starting", "running", "stopping", "stopped", "failed")
EXTENSION_RULES = (
    "Runtime components must be registered through stable component identifiers.",
    "State transitions must be observable as Event records.",
    "Host-specific fields belong in metadata mappings.",
)
BACKWARD_COMPATIBILITY_NOTES = (
    "This contract does not replace the existing runtime module.",
    "Future runtimes must preserve Job, Task, Event, Cancellation, Retry, Shutdown, and HealthCheck names.",
)


class RuntimeState(str, Enum):
    CREATED = "created"
    CONFIGURED = "configured"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


class TaskState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class Event:
    event_id: str
    name: str
    source: str
    payload: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(
            ("Event.event_id", self.event_id),
            ("Event.name", self.name),
            ("Event.source", self.source),
        )


@dataclass(frozen=True)
class Cancellation:
    requested: bool = False
    reason: str = ""
    requested_by: str = "system"

    def validate(self) -> tuple[ContractError, ...]:
        if self.requested and not self.reason.strip():
            return (_validation_error("Cancellation.reason is required when cancellation is requested"),)
        return ()


@dataclass(frozen=True)
class Retry:
    max_attempts: int = 1
    attempt: int = 0
    retryable_errors: tuple[PlatformErrorCode, ...] = ()

    def validate(self) -> tuple[ContractError, ...]:
        if self.max_attempts < 1:
            return (_validation_error("Retry.max_attempts must be at least 1"),)
        if self.attempt < 0 or self.attempt > self.max_attempts:
            return (_validation_error("Retry.attempt must be between 0 and max_attempts"),)
        return ()


@dataclass(frozen=True)
class Task:
    task_id: str
    name: str
    state: TaskState = TaskState.PENDING
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(("Task.task_id", self.task_id), ("Task.name", self.name))


@dataclass(frozen=True)
class Job:
    job_id: str
    tasks: tuple[Task, ...] = ()
    cancellation: Cancellation = field(default_factory=Cancellation)
    retry: Retry = field(default_factory=Retry)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        errors = list(_require_text(("Job.job_id", self.job_id)))
        errors.extend(self.cancellation.validate())
        errors.extend(self.retry.validate())
        for task in self.tasks:
            errors.extend(task.validate())
        return tuple(errors)


@dataclass(frozen=True)
class Shutdown:
    graceful: bool = True
    timeout_seconds: float = 30.0
    reason: str = "normal"

    def validate(self) -> tuple[ContractError, ...]:
        if self.timeout_seconds < 0:
            return (_validation_error("Shutdown.timeout_seconds cannot be negative"),)
        return ()


@dataclass(frozen=True)
class HealthCheck:
    component: str
    required: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(("HealthCheck.component", self.component))


@runtime_checkable
class RuntimeObserver(Protocol):
    def on_event(self, event: Event) -> None:
        """Receive runtime lifecycle and task events."""


@runtime_checkable
class LifecycleComponent(Protocol):
    @property
    def component_id(self) -> str:
        """Stable component identifier."""

    def start(self) -> None:
        """Enter the running lifecycle state."""

    def stop(self) -> None:
        """Enter the stopped lifecycle state."""

    def health(self) -> HealthReport:
        """Return component health using the diagnostics contract."""


class Runtime(ABC):
    @property
    @abstractmethod
    def state(self) -> RuntimeState:
        """Return the current runtime state."""

    @abstractmethod
    def register(self, component: LifecycleComponent) -> None:
        """Register a lifecycle component before startup."""

    @abstractmethod
    def submit(self, job: Job) -> None:
        """Submit a job that satisfies the runtime job contract."""

    @abstractmethod
    def cancel(self, job_id: str, cancellation: Cancellation) -> None:
        """Request cancellation for a job."""

    @abstractmethod
    def shutdown(self, request: Shutdown) -> None:
        """Request runtime shutdown."""


def _require_text(*fields: tuple[str, str]) -> tuple[ContractError, ...]:
    return tuple(_validation_error(f"{name} is required") for name, value in fields if not value.strip())


def _validation_error(message: str) -> ContractError:
    return ContractError(PlatformErrorCode.CONTRACT_VALIDATION_FAILED, message, source="runtime_contract")
