"""Universal runtime orchestration facade."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .event_bus import EventBus, RuntimeEventType
from .execution_context import ExecutionContext
from .health_monitor import HealthMonitor, RuntimeHealth
from .job_manager import JobLifecycleState, JobManager, RuntimeJob
from .lifecycle_manager import LifecycleManager, RuntimeLifecycleState
from .retry_manager import RetryManager, RetryPolicy
from .runtime_metrics import RuntimeMetrics
from .task_scheduler import ScheduledTask, TaskScheduler


class RuntimeEngine:
    """Coordinates runtime services without provider, GUI, or generation logic."""

    def __init__(self, retry_policy: RetryPolicy | None = None, context: ExecutionContext | None = None) -> None:
        self.context = context or ExecutionContext()
        self.event_bus = EventBus()
        self.metrics = RuntimeMetrics()
        self.lifecycle = LifecycleManager(self.event_bus)
        self.jobs = JobManager(self.event_bus)
        self.scheduler = TaskScheduler(self.event_bus)
        self.retry_manager = RetryManager(retry_policy)
        self.health_monitor = HealthMonitor(self.metrics)
        self.lifecycle.on_shutdown(self.metrics.stop_timer)
        self.lifecycle.on_dispose(self.metrics.stop_timer)

    @property
    def state(self) -> RuntimeLifecycleState:
        return self.lifecycle.state

    def initialize(self) -> RuntimeLifecycleState:
        return self.lifecycle.initialize()

    def start(self) -> RuntimeLifecycleState:
        self.metrics.start_timer()
        return self.lifecycle.start()

    def pause(self) -> RuntimeLifecycleState:
        return self.lifecycle.pause()

    def resume(self) -> RuntimeLifecycleState:
        return self.lifecycle.resume()

    def shutdown(self) -> RuntimeLifecycleState:
        return self.lifecycle.shutdown()

    def dispose(self) -> RuntimeLifecycleState:
        return self.lifecycle.dispose()

    def submit_job(self, job_id: str, priority: int = 0, metadata: dict[str, Any] | None = None) -> RuntimeJob:
        self.metrics.record_execution()
        return self.jobs.create(job_id, priority, metadata)

    def start_job(self, job_id: str) -> RuntimeJob:
        return self.jobs.transition(job_id, JobLifecycleState.RUNNING)

    def complete_job(self, job_id: str) -> RuntimeJob:
        self.metrics.record_success()
        return self.jobs.transition(job_id, JobLifecycleState.COMPLETED)

    def fail_job(self, job_id: str, error: str) -> RuntimeJob:
        self.metrics.record_failure()
        return self.jobs.transition(job_id, JobLifecycleState.FAILED, error)

    def retry_job(self, job_id: str, error: Exception | str | None = None) -> RuntimeJob:
        job = self.jobs.get(job_id)
        decision = self.retry_manager.evaluate(max(job.attempts, 1), error)
        if not decision.should_retry:
            self.metrics.record_failure()
            return self.jobs.transition(job_id, JobLifecycleState.FAILED, decision.reason)
        self.metrics.record_retry()
        self.event_bus.emit(
            RuntimeEventType.RETRY,
            "runtime_engine",
            {"job_id": job_id, "attempt": decision.attempt, "delay_seconds": decision.delay_seconds},
        )
        return self.jobs.transition(job_id, JobLifecycleState.RETRYING, decision.reason)

    def cancel_job(self, job_id: str, reason: str = "cancelled") -> RuntimeJob:
        return self.jobs.cancel(job_id, reason)

    def add_task(
        self,
        task_id: str,
        action: Callable[[], Any],
        dependencies: tuple[str, ...] = (),
        priority: int = 0,
    ) -> ScheduledTask:
        return self.scheduler.add_task(task_id, action, dependencies, priority)

    def run_next_task(self) -> ScheduledTask | None:
        return self.scheduler.run_next()

    def run_all_tasks(self) -> tuple[ScheduledTask, ...]:
        return self.scheduler.run_all()

    def health(self) -> RuntimeHealth:
        health = self.health_monitor.snapshot()
        self.event_bus.emit(RuntimeEventType.HEALTH, "runtime_engine", {"status": health.status})
        return health
