"""Plugin manifest, lifecycle, permission, and sandbox contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, runtime_checkable

from .diagnostics_contract import ContractError, PlatformErrorCode

CONTRACT_VERSION = "2.0.0"
CONTRACT_LIFECYCLE = ("discovered", "installed", "validated", "enabled", "disabled", "uninstalled")
EXTENSION_RULES = (
    "Plugins must declare permissions and sandbox requirements before activation.",
    "Plugin capabilities must be additive across minor versions.",
    "Host-specific plugin data belongs in metadata mappings.",
)
BACKWARD_COMPATIBILITY_NOTES = (
    "This contract does not install or execute plugins.",
    "Older hosts must reject unknown required permissions and may ignore optional capabilities.",
)


class PluginPermission(str, Enum):
    READ_WORKSPACE = "read_workspace"
    WRITE_WORKSPACE = "write_workspace"
    NETWORK = "network"
    EXECUTE_TOOL = "execute_tool"
    READ_MEMORY = "read_memory"


class PluginLifecycle(str, Enum):
    DISCOVERED = "discovered"
    INSTALLED = "installed"
    VALIDATED = "validated"
    ENABLED = "enabled"
    DISABLED = "disabled"
    UNINSTALLED = "uninstalled"


class PluginCapability(str, Enum):
    PROVIDER = "provider"
    SKILL = "skill"
    WORKFLOW = "workflow"
    CONNECTOR = "connector"
    DIAGNOSTIC = "diagnostic"


@dataclass(frozen=True)
class SandboxRequirements:
    filesystem: str = "read-only"
    network: bool = False
    subprocess: bool = False
    allowed_paths: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        if self.filesystem not in {"none", "read-only", "workspace-write"}:
            return (_validation_error("SandboxRequirements.filesystem is invalid"),)
        return ()


@dataclass(frozen=True)
class PluginManifest:
    plugin_id: str
    name: str
    version: str
    permissions: tuple[PluginPermission, ...] = ()
    capabilities: tuple[PluginCapability, ...] = ()
    sandbox: SandboxRequirements = field(default_factory=SandboxRequirements)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return (
            *_require_text(
                ("PluginManifest.plugin_id", self.plugin_id),
                ("PluginManifest.name", self.name),
                ("PluginManifest.version", self.version),
            ),
            *self.sandbox.validate(),
        )


@dataclass(frozen=True)
class PluginContext:
    plugin_id: str
    lifecycle: PluginLifecycle = PluginLifecycle.DISCOVERED
    host_version: str = CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(("PluginContext.plugin_id", self.plugin_id), ("PluginContext.host_version", self.host_version))


@runtime_checkable
class PluginSandbox(Protocol):
    def authorize(self, manifest: PluginManifest) -> tuple[ContractError, ...]:
        """Return sandbox or permission errors for the supplied manifest."""


class Plugin(ABC):
    @property
    @abstractmethod
    def manifest(self) -> PluginManifest:
        """Return the plugin manifest."""

    @abstractmethod
    def activate(self, context: PluginContext) -> None:
        """Activate the plugin within a validated host context."""

    @abstractmethod
    def deactivate(self, context: PluginContext) -> None:
        """Deactivate the plugin within a validated host context."""


def _require_text(*fields: tuple[str, str]) -> tuple[ContractError, ...]:
    return tuple(_validation_error(f"{name} is required") for name, value in fields if not value.strip())


def _validation_error(message: str) -> ContractError:
    return ContractError(PlatformErrorCode.CONTRACT_VALIDATION_FAILED, message, source="plugin_contract")
