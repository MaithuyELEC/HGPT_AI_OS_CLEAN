"""Universal Plugin SDK metadata, registry, lifecycle, and validation APIs."""

from .plugin_api import PluginAPI
from .plugin_context import PluginContext
from .plugin_events import PluginEvent, PluginEventBus, PluginEventType
from .plugin_lifecycle import PluginLifecycle, PluginLifecycleError, PluginLifecycleState
from .plugin_loader import PluginLoader
from .plugin_manager import PluginHealth, PluginManager
from .plugin_manifest import PluginCapability, PluginDependency, PluginManifest, permission_values
from .plugin_metrics import PluginMetrics
from .plugin_permissions import PermissionSet, PluginPermission
from .plugin_registry import PluginRegistration, PluginRegistry
from .plugin_sandbox import ExecutionPolicy, IsolationModel, PluginSandboxContract, SecurityBoundary
from .plugin_validator import PluginValidationResult, PluginValidator
from .plugin_version import PluginCompatibility, PluginVersion, SemanticVersion

__all__ = [
    "ExecutionPolicy",
    "IsolationModel",
    "PermissionSet",
    "PluginAPI",
    "PluginCapability",
    "PluginCompatibility",
    "PluginContext",
    "PluginDependency",
    "PluginEvent",
    "PluginEventBus",
    "PluginEventType",
    "PluginHealth",
    "PluginLifecycle",
    "PluginLifecycleError",
    "PluginLifecycleState",
    "PluginLoader",
    "PluginManager",
    "PluginManifest",
    "PluginMetrics",
    "PluginPermission",
    "PluginRegistration",
    "PluginRegistry",
    "PluginSandboxContract",
    "PluginValidationResult",
    "PluginValidator",
    "PluginVersion",
    "SecurityBoundary",
    "SemanticVersion",
    "permission_values",
]
