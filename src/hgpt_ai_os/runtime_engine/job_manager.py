"""Runtime job lifecycle management."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .event_bus import EventBus, RuntimeEventType
from .state_machine import StateMachine


class JobLifecycleState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    WAITING = "waiting"
    RETRYING = "retrying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


JOB_TRANSITIONS: dict[JobLifecycleState, frozenset[JobLifecycleState]] = {
    JobLifecycleState.QUEUED: frozenset({JobLifecycleState.RUNNING, JobLifecycleState.CANCELLED}),
    JobLifecycleState.RUNNING: frozenset(
        {
            JobLifecycleState.WAITING,
            JobLifecycleState.RETRYING,
            JobLifecycleState.COMPLETED,
            JobLifecycleState.FAILED,
            JobLifecycleState.CANCELLED,
        }
    ),
    JobLifecycleState.WAITING: frozenset({JobLifecycleState.RUNNING, JobLifecycleState.CANCELLED}),
    JobLifecycleState.RETRYING: frozenset({JobLifecycleState.RUNNING, JobLifecycleState.FAILED, JobLifecycleState.CANCELLED}),
    JobLifecycleState.COMPLETED: frozenset(),
    JobLifecycleState.FAILED: frozenset(),
    JobLifecycleState.CANCELLED: frozenset(),
}


@dataclass
class RuntimeJob:
    job_id: str
    priority: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    state: JobLifecycleState = JobLifecycleState.QUEUED
    attempts: int = 0
    error: str = ""

    def __post_init__(self) -> None:
        if not self.job_id.strip():
            raise ValueError("job_id is required")


class JobManager:
    """Owns job records and legal lifecycle transitions."""

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self._jobs: dict[str, RuntimeJob] = {}
        self._machines: dict[str, StateMachine[JobLifecycleState]] = {}
        self._event_bus = event_bus

    def create(self, job_id: str, priority: int = 0, metadata: dict[str, Any] | None = None) -> RuntimeJob:
        if job_id in self._jobs:
            raise KeyError(f"job already exists: {job_id}")
        job = RuntimeJob(job_id=job_id, priority=priority, metadata=dict(metadata or {}))
        self._jobs[job_id] = job
        self._machines[job_id] = StateMachine(job.state, JOB_TRANSITIONS)
        self._publish(job)
        return job

    def get(self, job_id: str) -> RuntimeJob:
        try:
            return self._jobs[job_id]
        except KeyError as exc:
            raise KeyError(f"unknown job: {job_id}") from exc

    def transition(self, job_id: str, target: JobLifecycleState, error: str = "") -> RuntimeJob:
        job = self.get(job_id)
        machine = self._machines[job_id]
        job.state = machine.transition(target)
        if target in {JobLifecycleState.RUNNING, JobLifecycleState.RETRYING}:
            job.attempts += 1
        if error:
            job.error = error
        self._publish(job)
        return job

    def cancel(self, job_id: str, reason: str = "cancelled") -> RuntimeJob:
        return self.transition(job_id, JobLifecycleState.CANCELLED, reason)

    def all(self) -> tuple[RuntimeJob, ...]:
        return tuple(self._jobs.values())

    def _publish(self, job: RuntimeJob) -> None:
        if self._event_bus is not None:
            self._event_bus.emit(
                RuntimeEventType.JOB,
                "job_manager",
                {"job_id": job.job_id, "state": job.state.value, "attempts": job.attempts},
            )
