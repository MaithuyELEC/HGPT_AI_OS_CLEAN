"""Architecture-only plugin sandbox contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping

from .plugin_manifest import PluginManifest


class IsolationModel(str, Enum):
    IN_PROCESS_METADATA = "in_process_metadata"
    OUT_OF_PROCESS = "out_of_process"
    REMOTE_EXECUTION = "remote_execution"


class SecurityBoundary(str, Enum):
    HOST_API = "host_api"
    PERMISSION_GATE = "permission_gate"
    DATA_BOUNDARY = "data_boundary"
    EXECUTION_BOUNDARY = "execution_boundary"


class ExecutionPolicy(str, Enum):
    METADATA_ONLY = "metadata_only"
    DECLARED_PERMISSIONS_ONLY = "declared_permissions_only"
    HOST_MEDIATED = "host_mediated"


@dataclass(frozen=True)
class PluginSandboxContract:
    permission_model: tuple[str, ...]
    isolation_model: IsolationModel = IsolationModel.IN_PROCESS_METADATA
    security_boundaries: tuple[SecurityBoundary, ...] = (
        SecurityBoundary.HOST_API,
        SecurityBoundary.PERMISSION_GATE,
        SecurityBoundary.DATA_BOUNDARY,
    )
    future_execution_policy: ExecutionPolicy = ExecutionPolicy.METADATA_ONLY
    metadata: Mapping[str, object] = field(default_factory=dict)

    @classmethod
    def for_manifest(cls, manifest: PluginManifest) -> "PluginSandboxContract":
        return cls(permission_model=manifest.permissions.as_tuple())

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if len(set(self.permission_model)) != len(self.permission_model):
            errors.append("permission model entries must be unique")
        if not self.security_boundaries:
            errors.append("at least one security boundary is required")
        return tuple(errors)
