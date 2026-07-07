"""Sequential task scheduling with dependencies and priority."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .event_bus import EventBus, RuntimeEventType


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledTask:
    task_id: str
    action: Callable[[], Any]
    dependencies: tuple[str, ...] = ()
    priority: int = 0
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: str = ""
    sequence: int = 0

    def __post_init__(self) -> None:
        if not self.task_id.strip():
            raise ValueError("task_id is required")
        if not callable(self.action):
            raise TypeError("task action must be callable")


class TaskScheduler:
    """Runs ready tasks one at a time while preserving a parallel-ready model."""

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self._tasks: dict[str, ScheduledTask] = {}
        self._sequence = 0
        self._event_bus = event_bus

    def add_task(
        self,
        task_id: str,
        action: Callable[[], Any],
        dependencies: tuple[str, ...] = (),
        priority: int = 0,
    ) -> ScheduledTask:
        if task_id in self._tasks:
            raise KeyError(f"task already exists: {task_id}")
        self._sequence += 1
        task = ScheduledTask(task_id, action, tuple(dependencies), priority, sequence=self._sequence)
        self._tasks[task_id] = task
        self._publish(task)
        return task

    def cancel_task(self, task_id: str) -> ScheduledTask:
        task = self.get(task_id)
        if task.status in {TaskStatus.COMPLETED, TaskStatus.FAILED}:
            raise ValueError(f"cannot cancel {task.status.value} task: {task_id}")
        task.status = TaskStatus.CANCELLED
        self._publish(task)
        return task

    def get(self, task_id: str) -> ScheduledTask:
        try:
            return self._tasks[task_id]
        except KeyError as exc:
            raise KeyError(f"unknown task: {task_id}") from exc

    def ready_tasks(self) -> tuple[ScheduledTask, ...]:
        ready = [
            task
            for task in self._tasks.values()
            if task.status is TaskStatus.PENDING and all(self._tasks[dep].status is TaskStatus.COMPLETED for dep in task.dependencies)
        ]
        return tuple(sorted(ready, key=lambda task: (-task.priority, task.sequence)))

    def run_next(self) -> ScheduledTask | None:
        self._validate_dependencies()
        ready = self.ready_tasks()
        if not ready:
            if any(task.status is TaskStatus.PENDING for task in self._tasks.values()):
                raise RuntimeError("pending tasks cannot run because dependencies are incomplete")
            return None
        task = ready[0]
        task.status = TaskStatus.RUNNING
        self._publish(task)
        try:
            task.result = task.action()
        except Exception as exc:
            task.status = TaskStatus.FAILED
            task.error = str(exc)
            self._publish(task)
            raise
        task.status = TaskStatus.COMPLETED
        self._publish(task)
        return task

    def run_all(self) -> tuple[ScheduledTask, ...]:
        completed: list[ScheduledTask] = []
        while True:
            task = self.run_next()
            if task is None:
                return tuple(completed)
            completed.append(task)

    def tasks(self) -> tuple[ScheduledTask, ...]:
        return tuple(sorted(self._tasks.values(), key=lambda task: task.sequence))

    def _validate_dependencies(self) -> None:
        missing = sorted({dep for task in self._tasks.values() for dep in task.dependencies if dep not in self._tasks})
        if missing:
            raise KeyError(f"unknown task dependencies: {', '.join(missing)}")

    def _publish(self, task: ScheduledTask) -> None:
        if self._event_bus is not None:
            self._event_bus.emit(
                RuntimeEventType.TASK,
                "task_scheduler",
                {"task_id": task.task_id, "status": task.status.value, "priority": task.priority},
            )
