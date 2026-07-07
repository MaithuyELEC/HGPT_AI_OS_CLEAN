"""Plugin validation helpers."""

from __future__ import annotations

from dataclasses import dataclass

from .plugin_manifest import PluginManifest
from .plugin_registry import PluginRegistry
from .plugin_version import PluginCompatibility


@dataclass(frozen=True)
class PluginValidationResult:
    valid: bool
    errors: tuple[str, ...] = ()


class PluginValidator:
    def __init__(self, sdk_version: str = "1.0.0", platform: str = "universal") -> None:
        self.sdk_version = sdk_version
        self.platform = platform

    def validate_manifest(self, manifest: PluginManifest) -> PluginValidationResult:
        errors = list(manifest.validate())
        if manifest.compatibility_with_sdk(self.sdk_version) is PluginCompatibility.INCOMPATIBLE:
            errors.append("plugin is incompatible with this SDK version")
        if not manifest.supports_platform(self.platform):
            errors.append(f"plugin does not support platform: {self.platform}")
        return PluginValidationResult(valid=not errors, errors=tuple(errors))

    def validate_dependencies(self, manifest: PluginManifest, registry: PluginRegistry) -> PluginValidationResult:
        errors: list[str] = []
        for dependency in manifest.dependencies:
            if dependency.optional and not registry.contains(dependency.plugin_id):
                continue
            if not registry.contains(dependency.plugin_id):
                errors.append(f"missing plugin dependency: {dependency.plugin_id}")
                continue
            current = registry.metadata(dependency.plugin_id).version.version
            if not current.is_compatible_with(dependency.min_version):
                errors.append(f"incompatible plugin dependency: {dependency.plugin_id}")
        return PluginValidationResult(valid=not errors, errors=tuple(errors))
