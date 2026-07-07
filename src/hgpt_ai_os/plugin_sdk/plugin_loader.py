"""Manifest loading, dependency validation, and compatibility checks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

from .plugin_manifest import PluginManifest
from .plugin_registry import PluginRegistry
from .plugin_validator import PluginValidationResult, PluginValidator


class PluginLoader:
    def __init__(self, sdk_version: str = "1.0.0", platform: str = "universal") -> None:
        self.validator = PluginValidator(sdk_version=sdk_version, platform=platform)

    def load_manifest(self, data: Mapping[str, object]) -> PluginManifest:
        manifest = PluginManifest.from_dict(data)
        result = self.validator.validate_manifest(manifest)
        if not result.valid:
            raise ValueError(result.errors[0])
        return manifest

    def load_manifest_file(self, path: str | Path) -> PluginManifest:
        manifest_path = Path(path)
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("plugin manifest must be a JSON object")
        return self.load_manifest(data)

    def discover(self, root: str | Path, filename: str = "plugin_manifest.json") -> tuple[Path, ...]:
        return tuple(sorted(Path(root).glob(f"*/{filename}")))

    def validate_dependencies(self, manifest: PluginManifest, registry: PluginRegistry) -> PluginValidationResult:
        return self.validator.validate_dependencies(manifest, registry)

    def validate_compatibility(self, manifest: PluginManifest) -> PluginValidationResult:
        return self.validator.validate_manifest(manifest)
