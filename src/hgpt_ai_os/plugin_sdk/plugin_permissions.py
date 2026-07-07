"""Plugin permission model."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class PluginPermission(str, Enum):
    FILESYSTEM = "filesystem"
    KNOWLEDGE = "knowledge"
    PROVIDER = "provider"
    WORKFLOW = "workflow"
    NETWORK = "network"
    CLIPBOARD = "clipboard"
    DIAGNOSTICS = "diagnostics"


@dataclass(frozen=True)
class PermissionSet:
    permissions: tuple[str, ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)

    @classmethod
    def from_values(cls, values: tuple[str | PluginPermission, ...]) -> "PermissionSet":
        return cls(tuple(_normalize_permission(value) for value in values))

    def allows(self, permission: str | PluginPermission) -> bool:
        return _normalize_permission(permission) in self.permissions

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if len(set(self.permissions)) != len(self.permissions):
            errors.append("permissions must be unique")
        for permission in self.permissions:
            if not permission.strip():
                errors.append("permission values must be non-empty")
        return tuple(errors)

    def as_tuple(self) -> tuple[str, ...]:
        return self.permissions


def _normalize_permission(permission: str | PluginPermission) -> str:
    if isinstance(permission, PluginPermission):
        return permission.value
    return permission.strip().lower()
