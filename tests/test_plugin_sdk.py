from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from hgpt_ai_os.plugin_sdk import (
    ExecutionPolicy,
    IsolationModel,
    PermissionSet,
    PluginCompatibility,
    PluginEventBus,
    PluginEventType,
    PluginLifecycle,
    PluginLifecycleError,
    PluginLifecycleState,
    PluginLoader,
    PluginManager,
    PluginManifest,
    PluginMetrics,
    PluginPermission,
    PluginRegistry,
    PluginSandboxContract,
    PluginValidator,
    PluginVersion,
    SecurityBoundary,
    SemanticVersion,
)


def manifest(plugin_id: str = "excel-plugin") -> PluginManifest:
    return PluginManifest.from_dict(
        {
            "plugin_id": plugin_id,
            "name": "ExcelPlugin",
            "version": "1.0.0",
            "author": "LUCID",
            "description": "Metadata-only Microsoft Excel plugin declaration.",
            "capabilities": ["spreadsheet", "analytics"],
            "dependencies": [],
            "permissions": ["filesystem", "clipboard"],
            "platforms": ["universal"],
        }
    )


class PluginManifestTests(unittest.TestCase):
    def test_manifest_metadata_permissions_and_capabilities(self):
        metadata = manifest()

        self.assertEqual(metadata.plugin_id, "excel-plugin")
        self.assertTrue(metadata.supports("spreadsheet"))
        self.assertTrue(metadata.supports_platform("windows"))
        self.assertTrue(metadata.permissions.allows(PluginPermission.FILESYSTEM))
        self.assertEqual(metadata.version_metadata()["version"], "1.0.0")
        self.assertEqual(metadata.validate(), ())
        self.assertEqual(metadata.as_dict()["name"], "ExcelPlugin")

    def test_manifest_rejects_missing_required_fields(self):
        metadata = PluginManifest.from_dict({"plugin_id": "", "name": "", "version": "1.0.0", "capabilities": []})

        self.assertIn("plugin_id is required", metadata.validate())
        self.assertIn("name is required", metadata.validate())
        self.assertIn("at least one capability is required", metadata.validate())


class PluginRegistryTests(unittest.TestCase):
    def test_register_unregister_discover_and_metadata(self):
        registry = PluginRegistry()
        metadata = manifest()

        registration = registry.register_plugin(metadata)

        self.assertEqual(registration.lifecycle.state, PluginLifecycleState.INSTALLED)
        self.assertTrue(registry.contains("excel-plugin"))
        self.assertEqual(registry.metadata("excel-plugin"), metadata)
        self.assertEqual(registry.plugin_ids(), ("excel-plugin",))
        self.assertEqual(registry.version_metadata("excel-plugin")["version"], "1.0.0")
        self.assertEqual(registry.capability_metadata("excel-plugin"), ("spreadsheet", "analytics"))
        self.assertEqual(registry.discover_plugin("spreadsheet"), (metadata,))
        self.assertEqual(registry.unregister_plugin("excel-plugin").manifest, metadata)
        self.assertFalse(registry.contains("excel-plugin"))

    def test_rejects_duplicate_plugins(self):
        registry = PluginRegistry()
        registry.register_plugin(manifest())

        with self.assertRaises(KeyError):
            registry.register_plugin(manifest())


class PluginLoaderTests(unittest.TestCase):
    def test_manifest_loading_dependency_validation_and_discovery(self):
        loader = PluginLoader()
        registry = PluginRegistry()
        base = manifest("base-plugin")
        registry.register_plugin(base)
        data = {
            "plugin_id": "powerbi-plugin",
            "name": "PowerBIPlugin",
            "version": "1.0.0",
            "capabilities": ["analytics"],
            "dependencies": [{"plugin_id": "base-plugin", "min_version": "1.0.0"}],
            "permissions": ["diagnostics"],
        }

        metadata = loader.load_manifest(data)

        self.assertEqual(metadata.plugin_id, "powerbi-plugin")
        self.assertTrue(loader.validate_dependencies(metadata, registry).valid)
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "powerbi" / "plugin_manifest.json"
            path.parent.mkdir()
            path.write_text(json.dumps(data), encoding="utf-8")

            self.assertEqual(loader.discover(temp_dir), (path,))
            self.assertEqual(loader.load_manifest_file(path).plugin_id, "powerbi-plugin")

    def test_rejects_incompatible_manifest(self):
        loader = PluginLoader(sdk_version="1.0.0")

        with self.assertRaises(ValueError):
            loader.load_manifest(
                {
                    "plugin_id": "future",
                    "name": "Future",
                    "version": "2.0.0",
                    "min_sdk_version": "2.0.0",
                    "capabilities": ["diagnostic"],
                }
            )


class PluginManagerTests(unittest.TestCase):
    def test_load_enable_disable_reload_shutdown_and_health(self):
        events = PluginEventBus()
        seen: list[PluginEventType] = []
        events.subscribe(PluginEventType.ENABLED, lambda event: seen.append(event.event_type))
        manager = PluginManager(events=events)
        metadata = manifest()

        manager.load(metadata)
        manager.enable("excel-plugin")
        manager.reload("excel-plugin")
        health = manager.health()
        manager.shutdown()

        self.assertIn(PluginEventType.ENABLED, seen)
        self.assertEqual(health.status, "ready")
        self.assertEqual(health.plugin_count, 1)
        self.assertEqual(health.enabled_count, 1)
        self.assertGreaterEqual(health.metrics["load_time"], 0.0)
        self.assertEqual(manager.registry.get("excel-plugin").lifecycle.state, PluginLifecycleState.DISABLED)

    def test_load_failure_records_metric(self):
        manager = PluginManager()
        bad = PluginManifest.from_dict(
            {
                "plugin_id": "dependent",
                "name": "Dependent",
                "version": "1.0.0",
                "capabilities": ["diagnostic"],
                "dependencies": ["missing"],
            }
        )

        with self.assertRaises(ValueError):
            manager.load(bad)
        self.assertEqual(manager.metrics.failure_count, 1)


class PluginLifecycleTests(unittest.TestCase):
    def test_lifecycle_states_and_illegal_transition(self):
        lifecycle = PluginLifecycle()

        self.assertEqual(lifecycle.transition(PluginLifecycleState.LOADED), PluginLifecycleState.LOADED)
        self.assertEqual(lifecycle.transition(PluginLifecycleState.ENABLED), PluginLifecycleState.ENABLED)
        self.assertEqual(lifecycle.transition(PluginLifecycleState.DISABLED), PluginLifecycleState.DISABLED)
        self.assertEqual(lifecycle.transition(PluginLifecycleState.UNINSTALLED), PluginLifecycleState.UNINSTALLED)
        with self.assertRaises(PluginLifecycleError):
            lifecycle.transition(PluginLifecycleState.ENABLED)


class PluginContractsMetricsCompatibilityTests(unittest.TestCase):
    def test_permissions_sandbox_metrics_compatibility_and_version(self):
        permissions = PermissionSet.from_values((PluginPermission.NETWORK, "future_permission"))
        sandbox = PluginSandboxContract(
            permission_model=permissions.as_tuple(),
            isolation_model=IsolationModel.IN_PROCESS_METADATA,
            security_boundaries=(SecurityBoundary.HOST_API, SecurityBoundary.PERMISSION_GATE),
            future_execution_policy=ExecutionPolicy.METADATA_ONLY,
        )
        metrics = PluginMetrics()
        version = PluginVersion.from_strings("1.1.0", min_sdk_version="1.0.0", migration_targets=("2.0.0",))

        metrics.set_plugin_count(2)
        metrics.record_load_time(0.25)
        metrics.record_failure()
        metrics.record_enable()
        metrics.record_disable()

        self.assertTrue(permissions.allows("future_permission"))
        self.assertEqual(permissions.validate(), ())
        self.assertEqual(sandbox.validate(), ())
        self.assertEqual(sandbox.isolation_model, IsolationModel.IN_PROCESS_METADATA)
        self.assertEqual(metrics.snapshot()["plugin_count"], 2)
        self.assertEqual(str(SemanticVersion.parse("1.2.3")), "1.2.3")
        self.assertEqual(version.compatibility_with_sdk("1.2.0"), PluginCompatibility.COMPATIBLE)
        self.assertEqual(version.compatibility_with_sdk("2.0.0"), PluginCompatibility.MIGRATION_AVAILABLE)
        self.assertEqual(version.compatibility_with_sdk("0.9.0"), PluginCompatibility.INCOMPATIBLE)
        self.assertTrue(version.migration_supported("2.0.0"))

    def test_validator_reports_platform_and_dependency_errors(self):
        validator = PluginValidator(platform="linux")
        registry = PluginRegistry()
        metadata = PluginManifest.from_dict(
            {
                "plugin_id": "word-plugin",
                "name": "WordPlugin",
                "version": "1.0.0",
                "capabilities": ["document"],
                "dependencies": ["missing"],
                "permissions": ["filesystem"],
                "platforms": ["windows"],
            }
        )

        self.assertFalse(validator.validate_manifest(metadata).valid)
        self.assertFalse(validator.validate_dependencies(metadata, registry).valid)


if __name__ == "__main__":
    unittest.main()
