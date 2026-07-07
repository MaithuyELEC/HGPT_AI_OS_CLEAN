"""Universal agent permission model."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AgentPermission(str, Enum):
    FILESYSTEM = "filesystem"
    KNOWLEDGE = "knowledge"
    PROVIDER = "provider"
    PLUGIN = "plugin"
    WORKFLOW = "workflow"
    DIAGNOSTICS = "diagnostics"


@dataclass(frozen=True)
class AgentPermissionSet:
    permissions: tuple[AgentPermission, ...] = ()

    def allows(self, permission: AgentPermission) -> bool:
        return permission in self.permissions

    def require(self, requested: tuple[AgentPermission, ...]) -> bool:
        return all(permission in self.permissions for permission in requested)

    def names(self) -> tuple[str, ...]:
        return tuple(permission.value for permission in self.permissions)
