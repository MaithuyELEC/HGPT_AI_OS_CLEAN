"""Plugin registration, discovery, and metadata lookup."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .plugin_lifecycle import PluginLifecycle, PluginLifecycleState
from .plugin_manifest import PluginManifest


@dataclass
class PluginRegistration:
    manifest: PluginManifest
    lifecycle: PluginLifecycle = field(default_factory=PluginLifecycle)

    @property
    def enabled(self) -> bool:
        return self.lifecycle.state is PluginLifecycleState.ENABLED


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, PluginRegistration] = {}

    def register_plugin(self, manifest: PluginManifest) -> PluginRegistration:
        errors = manifest.validate()
        if errors:
            raise ValueError(errors[0])
        if manifest.plugin_id in self._plugins:
            raise KeyError(f"plugin already registered: {manifest.plugin_id}")
        registration = PluginRegistration(manifest=manifest)
        self._plugins[manifest.plugin_id] = registration
        return registration

    def unregister_plugin(self, plugin_id: str) -> PluginRegistration:
        registration = self.get(plugin_id)
        registration.lifecycle.transition(PluginLifecycleState.UNINSTALLED)
        return self._plugins.pop(plugin_id)

    def contains(self, plugin_id: str) -> bool:
        return plugin_id in self._plugins

    def get(self, plugin_id: str) -> PluginRegistration:
        if plugin_id not in self._plugins:
            raise KeyError(f"plugin not registered: {plugin_id}")
        return self._plugins[plugin_id]

    def metadata(self, plugin_id: str) -> PluginManifest:
        return self.get(plugin_id).manifest

    def plugin_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._plugins))

    def discover_plugin(
        self,
        capability: str | None = None,
        *,
        platform: str | None = None,
        enabled_only: bool = False,
    ) -> tuple[PluginManifest, ...]:
        discovered: list[PluginManifest] = []
        for plugin_id in self.plugin_ids():
            registration = self._plugins[plugin_id]
            manifest = registration.manifest
            if enabled_only and not registration.enabled:
                continue
            if capability is not None and not manifest.supports(capability):
                continue
            if platform is not None and not manifest.supports_platform(platform):
                continue
            discovered.append(manifest)
        return tuple(discovered)

    def version_metadata(self, plugin_id: str) -> Mapping[str, object]:
        manifest = self.metadata(plugin_id)
        return {"plugin_id": manifest.plugin_id, **manifest.version_metadata()}

    def capability_metadata(self, plugin_id: str) -> tuple[str, ...]:
        return self.metadata(plugin_id).capability_metadata()

    def set_state(self, plugin_id: str, state: PluginLifecycleState) -> PluginRegistration:
        registration = self.get(plugin_id)
        registration.lifecycle.transition(state)
        return registration
