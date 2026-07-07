"""Plugin load, enable, disable, reload, shutdown, and health management."""

from __future__ import annotations

from dataclasses import dataclass
from time import monotonic

from .plugin_events import PluginEventBus, PluginEventType
from .plugin_lifecycle import PluginLifecycleState
from .plugin_loader import PluginLoader
from .plugin_manifest import PluginManifest
from .plugin_metrics import PluginMetrics
from .plugin_registry import PluginRegistry


@dataclass(frozen=True)
class PluginHealth:
    status: str
    plugin_count: int
    enabled_count: int
    failed_count: int
    metrics: dict[str, int | float]


class PluginManager:
    def __init__(
        self,
        registry: PluginRegistry | None = None,
        loader: PluginLoader | None = None,
        events: PluginEventBus | None = None,
        metrics: PluginMetrics | None = None,
    ) -> None:
        self.registry = registry or PluginRegistry()
        self.loader = loader or PluginLoader()
        self.events = events or PluginEventBus()
        self.metrics = metrics or PluginMetrics()

    def load(self, manifest: PluginManifest) -> None:
        started = monotonic()
        try:
            dependency_result = self.loader.validate_dependencies(manifest, self.registry)
            if not dependency_result.valid:
                raise ValueError(dependency_result.errors[0])
            registration = self.registry.register_plugin(manifest)
            registration.lifecycle.transition(PluginLifecycleState.LOADED)
            self.events.emit(PluginEventType.INSTALLED, manifest.plugin_id, {"version": str(manifest.version.version)})
        except Exception:
            self.metrics.record_failure()
            raise
        finally:
            self.metrics.record_load_time(monotonic() - started)
            self.metrics.set_plugin_count(len(self.registry.plugin_ids()))

    def enable(self, plugin_id: str) -> None:
        self.registry.set_state(plugin_id, PluginLifecycleState.ENABLED)
        self.metrics.record_enable()
        self.events.emit(PluginEventType.ENABLED, plugin_id)

    def disable(self, plugin_id: str) -> None:
        self.registry.set_state(plugin_id, PluginLifecycleState.DISABLED)
        self.metrics.record_disable()
        self.events.emit(PluginEventType.DISABLED, plugin_id)

    def reload(self, plugin_id: str) -> None:
        registration = self.registry.get(plugin_id)
        state = registration.lifecycle.state
        if state is PluginLifecycleState.ENABLED:
            self.disable(plugin_id)
        if registration.lifecycle.state is PluginLifecycleState.DISABLED:
            registration.lifecycle.transition(PluginLifecycleState.LOADED)
        if state is PluginLifecycleState.ENABLED:
            self.enable(plugin_id)
        self.events.emit(PluginEventType.UPDATED, plugin_id)

    def shutdown(self) -> None:
        for plugin_id in self.registry.plugin_ids():
            registration = self.registry.get(plugin_id)
            if registration.lifecycle.state is PluginLifecycleState.ENABLED:
                self.disable(plugin_id)

    def unload(self, plugin_id: str) -> None:
        self.registry.unregister_plugin(plugin_id)
        self.metrics.set_plugin_count(len(self.registry.plugin_ids()))
        self.events.emit(PluginEventType.REMOVED, plugin_id)

    def health(self) -> PluginHealth:
        states = tuple(self.registry.get(plugin_id).lifecycle.state for plugin_id in self.registry.plugin_ids())
        failed_count = sum(1 for state in states if state is PluginLifecycleState.FAILED)
        enabled_count = sum(1 for state in states if state is PluginLifecycleState.ENABLED)
        status = "degraded" if failed_count else "ready"
        return PluginHealth(
            status=status,
            plugin_count=len(states),
            enabled_count=enabled_count,
            failed_count=failed_count,
            metrics=self.metrics.snapshot(),
        )
