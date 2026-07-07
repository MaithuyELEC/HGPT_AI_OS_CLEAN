"""Platform job contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, runtime_checkable

from .diagnostics_contract import ContractError, PlatformErrorCode

CONTRACT_VERSION = "2.0.0"
CONTRACT_LIFECYCLE = ("accepted", "queued", "running", "completed", "failed", "cancelled")
EXTENSION_RULES = (
    "Job identifiers must remain stable across queues and runtimes.",
    "Job payloads must be serializable mappings.",
    "Scheduling hints must not change required validation semantics.",
)
BACKWARD_COMPATIBILITY_NOTES = (
    "Job contracts are additive and do not replace current run queue internals.",
    "Unknown job priorities must be treated as normal priority by older hosts.",
)


class JobPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class JobStatus(str, Enum):
    ACCEPTED = "accepted"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class JobRequest:
    job_id: str
    kind: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    priority: JobPriority = JobPriority.NORMAL
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(("JobRequest.job_id", self.job_id), ("JobRequest.kind", self.kind))


@dataclass(frozen=True)
class JobState:
    job_id: str
    status: JobStatus = JobStatus.ACCEPTED
    progress: float = 0.0
    errors: tuple[ContractError, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        errors = list(_require_text(("JobState.job_id", self.job_id)))
        if not 0 <= self.progress <= 1:
            errors.append(_validation_error("JobState.progress must be between 0 and 1"))
        return tuple(errors)


@dataclass(frozen=True)
class JobReceipt:
    job_id: str
    accepted: bool
    state: JobState

    def validate(self) -> tuple[ContractError, ...]:
        return (*_require_text(("JobReceipt.job_id", self.job_id)), *self.state.validate())


@runtime_checkable
class JobQueue(Protocol):
    def enqueue(self, request: JobRequest) -> JobReceipt:
        """Accept a validated job request into a platform queue."""


class JobController(ABC):
    @abstractmethod
    def submit(self, request: JobRequest) -> JobReceipt:
        """Submit a job request."""

    @abstractmethod
    def status(self, job_id: str) -> JobState:
        """Return current job state."""

    @abstractmethod
    def cancel(self, job_id: str, reason: str) -> JobState:
        """Cancel a job by stable identifier."""


def _require_text(*fields: tuple[str, str]) -> tuple[ContractError, ...]:
    return tuple(_validation_error(f"{name} is required") for name, value in fields if not value.strip())


def _validation_error(message: str) -> ContractError:
    return ContractError(PlatformErrorCode.CONTRACT_VALIDATION_FAILED, message, source="job_contract")
