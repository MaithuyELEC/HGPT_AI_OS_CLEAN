"""Plugin manifest metadata model and parsing."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from .plugin_permissions import PermissionSet, PluginPermission
from .plugin_version import PluginCompatibility, PluginVersion


class PluginCapability(str, Enum):
    DOCUMENT = "document"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"
    CAD = "cad"
    ERP = "erp"
    DESIGN = "design"
    EMAIL = "email"
    ANALYTICS = "analytics"
    DIAGNOSTIC = "diagnostic"


@dataclass(frozen=True)
class PluginDependency:
    plugin_id: str
    min_version: str = "1.0.0"
    optional: bool = False

    @classmethod
    def from_value(cls, value: str | Mapping[str, Any]) -> "PluginDependency":
        if isinstance(value, str):
            return cls(plugin_id=value)
        return cls(
            plugin_id=str(value.get("plugin_id", "")).strip(),
            min_version=str(value.get("min_version", "1.0.0")).strip(),
            optional=bool(value.get("optional", False)),
        )

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.plugin_id:
            errors.append("dependency plugin_id is required")
        try:
            PluginVersion.from_strings(self.min_version)
        except ValueError as exc:
            errors.append(str(exc))
        return tuple(errors)

    def as_dict(self) -> Mapping[str, object]:
        return {
            "plugin_id": self.plugin_id,
            "min_version": self.min_version,
            "optional": self.optional,
        }


@dataclass(frozen=True)
class PluginManifest:
    plugin_id: str
    name: str
    version: PluginVersion
    author: str = ""
    description: str = ""
    capabilities: tuple[str, ...] = ()
    dependencies: tuple[PluginDependency, ...] = ()
    permissions: PermissionSet = field(default_factory=PermissionSet)
    platforms: tuple[str, ...] = ("universal",)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "PluginManifest":
        permissions = tuple(data.get("permissions", ()))
        dependencies = tuple(PluginDependency.from_value(value) for value in data.get("dependencies", ()))
        return cls(
            plugin_id=str(data.get("plugin_id", "")).strip(),
            name=str(data.get("name", "")).strip(),
            version=PluginVersion.from_strings(
                str(data.get("version", "")).strip(),
                min_sdk_version=str(data.get("min_sdk_version", "1.0.0")).strip(),
                migration_targets=tuple(str(value) for value in data.get("migration_targets", ())),
            ),
            author=str(data.get("author", "")).strip(),
            description=str(data.get("description", "")).strip(),
            capabilities=tuple(str(value).strip().lower() for value in data.get("capabilities", ())),
            dependencies=dependencies,
            permissions=PermissionSet.from_values(permissions),
            platforms=tuple(str(value).strip().lower() for value in data.get("platforms", ("universal",))),
            metadata=dict(data.get("metadata", {})),
        )

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.plugin_id:
            errors.append("plugin_id is required")
        if not self.name:
            errors.append("name is required")
        if not self.capabilities:
            errors.append("at least one capability is required")
        if not self.platforms:
            errors.append("at least one platform is required")
        if len(set(self.capabilities)) != len(self.capabilities):
            errors.append("capabilities must be unique")
        if len(set(self.platforms)) != len(self.platforms):
            errors.append("platforms must be unique")
        errors.extend(self.permissions.validate())
        for dependency in self.dependencies:
            errors.extend(dependency.validate())
        return tuple(errors)

    def supports(self, capability: str | PluginCapability) -> bool:
        value = capability.value if isinstance(capability, PluginCapability) else capability.strip().lower()
        return value in self.capabilities

    def supports_platform(self, platform: str) -> bool:
        normalized = platform.strip().lower()
        return "universal" in self.platforms or normalized in self.platforms

    def compatibility_with_sdk(self, sdk_version: str) -> PluginCompatibility:
        return self.version.compatibility_with_sdk(sdk_version)

    def version_metadata(self) -> Mapping[str, object]:
        return self.version.as_metadata()

    def capability_metadata(self) -> tuple[str, ...]:
        return self.capabilities

    def as_dict(self) -> Mapping[str, object]:
        return {
            "plugin_id": self.plugin_id,
            "name": self.name,
            "version": str(self.version.version),
            "min_sdk_version": str(self.version.min_sdk_version),
            "author": self.author,
            "description": self.description,
            "capabilities": self.capabilities,
            "dependencies": tuple(dependency.as_dict() for dependency in self.dependencies),
            "permissions": self.permissions.as_tuple(),
            "platforms": self.platforms,
            "metadata": dict(self.metadata),
        }


def permission_values() -> tuple[str, ...]:
    return tuple(permission.value for permission in PluginPermission)
