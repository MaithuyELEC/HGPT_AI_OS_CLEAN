"""Plugin lifecycle states and transition rules."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PluginLifecycleState(str, Enum):
    INSTALLED = "installed"
    LOADED = "loaded"
    ENABLED = "enabled"
    DISABLED = "disabled"
    FAILED = "failed"
    UNINSTALLED = "uninstalled"


PLUGIN_LIFECYCLE_TRANSITIONS: dict[PluginLifecycleState, frozenset[PluginLifecycleState]] = {
    PluginLifecycleState.INSTALLED: frozenset({
        PluginLifecycleState.LOADED,
        PluginLifecycleState.UNINSTALLED,
        PluginLifecycleState.FAILED,
    }),
    PluginLifecycleState.LOADED: frozenset({
        PluginLifecycleState.ENABLED,
        PluginLifecycleState.DISABLED,
        PluginLifecycleState.FAILED,
        PluginLifecycleState.UNINSTALLED,
    }),
    PluginLifecycleState.ENABLED: frozenset({
        PluginLifecycleState.DISABLED,
        PluginLifecycleState.FAILED,
        PluginLifecycleState.UNINSTALLED,
    }),
    PluginLifecycleState.DISABLED: frozenset({
        PluginLifecycleState.ENABLED,
        PluginLifecycleState.LOADED,
        PluginLifecycleState.UNINSTALLED,
        PluginLifecycleState.FAILED,
    }),
    PluginLifecycleState.FAILED: frozenset({
        PluginLifecycleState.DISABLED,
        PluginLifecycleState.UNINSTALLED,
    }),
    PluginLifecycleState.UNINSTALLED: frozenset(),
}


class PluginLifecycleError(ValueError):
    pass


@dataclass
class PluginLifecycle:
    state: PluginLifecycleState = PluginLifecycleState.INSTALLED

    def can_transition(self, target: PluginLifecycleState) -> bool:
        return target in PLUGIN_LIFECYCLE_TRANSITIONS[self.state]

    def transition(self, target: PluginLifecycleState) -> PluginLifecycleState:
        if not self.can_transition(target):
            raise PluginLifecycleError(f"illegal plugin lifecycle transition: {self.state.value} -> {target.value}")
        self.state = target
        return self.state
