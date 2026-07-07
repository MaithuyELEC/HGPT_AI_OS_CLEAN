"""Runtime lifecycle orchestration."""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum

from .event_bus import EventBus, RuntimeEventType
from .state_machine import StateMachine


class RuntimeLifecycleState(str, Enum):
    CREATED = "created"
    INITIALIZED = "initialized"
    RUNNING = "running"
    PAUSED = "paused"
    SHUTDOWN = "shutdown"
    DISPOSED = "disposed"


LIFECYCLE_TRANSITIONS: dict[RuntimeLifecycleState, frozenset[RuntimeLifecycleState]] = {
    RuntimeLifecycleState.CREATED: frozenset({RuntimeLifecycleState.INITIALIZED, RuntimeLifecycleState.DISPOSED}),
    RuntimeLifecycleState.INITIALIZED: frozenset({RuntimeLifecycleState.RUNNING, RuntimeLifecycleState.DISPOSED}),
    RuntimeLifecycleState.RUNNING: frozenset({RuntimeLifecycleState.PAUSED, RuntimeLifecycleState.SHUTDOWN}),
    RuntimeLifecycleState.PAUSED: frozenset({RuntimeLifecycleState.RUNNING, RuntimeLifecycleState.SHUTDOWN}),
    RuntimeLifecycleState.SHUTDOWN: frozenset({RuntimeLifecycleState.DISPOSED}),
    RuntimeLifecycleState.DISPOSED: frozenset(),
}


class LifecycleManager:
    """Coordinates initialize/start/pause/resume/shutdown/dispose callbacks."""

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self._machine = StateMachine(RuntimeLifecycleState.CREATED, LIFECYCLE_TRANSITIONS)
        self._event_bus = event_bus
        self._shutdown_callbacks: list[Callable[[], None]] = []
        self._dispose_callbacks: list[Callable[[], None]] = []

    @property
    def state(self) -> RuntimeLifecycleState:
        return self._machine.state

    def on_shutdown(self, callback: Callable[[], None]) -> None:
        self._shutdown_callbacks.append(callback)

    def on_dispose(self, callback: Callable[[], None]) -> None:
        self._dispose_callbacks.append(callback)

    def initialize(self) -> RuntimeLifecycleState:
        return self._transition(RuntimeLifecycleState.INITIALIZED)

    def start(self) -> RuntimeLifecycleState:
        return self._transition(RuntimeLifecycleState.RUNNING)

    def pause(self) -> RuntimeLifecycleState:
        return self._transition(RuntimeLifecycleState.PAUSED)

    def resume(self) -> RuntimeLifecycleState:
        return self._transition(RuntimeLifecycleState.RUNNING)

    def shutdown(self) -> RuntimeLifecycleState:
        state = self._transition(RuntimeLifecycleState.SHUTDOWN)
        for callback in tuple(self._shutdown_callbacks):
            callback()
        return state

    def dispose(self) -> RuntimeLifecycleState:
        state = self._transition(RuntimeLifecycleState.DISPOSED)
        for callback in tuple(self._dispose_callbacks):
            callback()
        return state

    def _transition(self, target: RuntimeLifecycleState) -> RuntimeLifecycleState:
        state = self._machine.transition(target)
        if self._event_bus is not None:
            self._event_bus.emit(RuntimeEventType.LIFECYCLE, "lifecycle_manager", {"state": state.value})
        return state
