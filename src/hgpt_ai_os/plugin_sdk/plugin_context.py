"""Plugin host context."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from .plugin_permissions import PermissionSet


@dataclass(frozen=True)
class PluginContext:
    plugin_id: str
    sdk_version: str = "1.0.0"
    permissions: PermissionSet = field(default_factory=PermissionSet)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.plugin_id.strip():
            errors.append("plugin_id is required")
        if not self.sdk_version.strip():
            errors.append("sdk_version is required")
        errors.extend(self.permissions.validate())
        return tuple(errors)
