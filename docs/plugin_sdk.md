# Universal Plugin SDK

Sprint 07 adds a metadata-first plugin SDK for registering, validating, and managing future platform extensions. The SDK is intentionally isolated from contracts, providers, the runtime engine, agents, the knowledge engine, GUI code, production workflow, and AI generation.

## Scope

- `src/hgpt_ai_os/plugin_sdk/` contains the SDK surface.
- Plugin examples are metadata-only declarations.
- No plugin code is executed.
- No HTTP, connector, or third-party integration behavior is included.
- The sandbox and stable API are contracts only.

## Modules

- `plugin_manifest.py` defines plugin ID, name, version, author, description, capabilities, dependencies, permissions, platform compatibility, and metadata.
- `plugin_registry.py` registers, unregisters, discovers, and reports plugin metadata, version metadata, and capability metadata.
- `plugin_loader.py` loads JSON manifests, discovers `plugin_manifest.json` files, validates dependencies, and validates SDK/platform compatibility.
- `plugin_manager.py` coordinates load, enable, disable, reload, shutdown, unload, and health.
- `plugin_permissions.py` defines filesystem, knowledge, provider, workflow, network, clipboard, diagnostics, and future permission values.
- `plugin_lifecycle.py` defines installed, loaded, enabled, disabled, failed, and uninstalled states.
- `plugin_sandbox.py` defines the permission model, isolation model, security boundaries, and future execution policy.
- `plugin_api.py` defines a stable extension interface without implementation.
- `plugin_events.py` emits installed, updated, enabled, disabled, and removed events.
- `plugin_metrics.py` tracks plugin count, load time, failure count, enable count, and disable count.
- `plugin_version.py` provides semantic versioning, compatibility matrix checks, and migration support.
- `plugin_context.py` defines host context passed to future extension implementations.
- `plugin_validator.py` centralizes manifest, dependency, platform, and compatibility validation.

## Metadata-Only Examples

These examples are declarations only and have no executable integration logic.

```json
{
  "plugin_id": "excel-plugin",
  "name": "ExcelPlugin",
  "version": "1.0.0",
  "author": "LUCID",
  "description": "Metadata-only Microsoft Excel plugin declaration.",
  "capabilities": ["spreadsheet", "analytics"],
  "dependencies": [],
  "permissions": ["filesystem", "clipboard"],
  "platforms": ["universal"]
}
```

```json
{
  "plugin_id": "powerbi-plugin",
  "name": "PowerBIPlugin",
  "version": "1.0.0",
  "author": "LUCID",
  "description": "Metadata-only Microsoft Power BI plugin declaration.",
  "capabilities": ["analytics", "presentation"],
  "dependencies": [],
  "permissions": ["filesystem", "diagnostics"],
  "platforms": ["universal"]
}
```

```json
{
  "plugin_id": "autocad-plugin",
  "name": "AutoCADPlugin",
  "version": "1.0.0",
  "author": "LUCID",
  "description": "Metadata-only AutoCAD plugin declaration.",
  "capabilities": ["cad", "document"],
  "dependencies": [],
  "permissions": ["filesystem"],
  "platforms": ["universal"]
}
```

```json
{
  "plugin_id": "solidworks-plugin",
  "name": "SolidWorksPlugin",
  "version": "1.0.0",
  "author": "LUCID",
  "description": "Metadata-only SolidWorks plugin declaration.",
  "capabilities": ["cad", "document"],
  "dependencies": [],
  "permissions": ["filesystem"],
  "platforms": ["universal"]
}
```

```json
{
  "plugin_id": "sap-plugin",
  "name": "SAPPlugin",
  "version": "1.0.0",
  "author": "LUCID",
  "description": "Metadata-only SAP plugin declaration.",
  "capabilities": ["erp", "workflow"],
  "dependencies": [],
  "permissions": ["workflow", "diagnostics"],
  "platforms": ["universal"]
}
```

```json
{
  "plugin_id": "canva-plugin",
  "name": "CanvaPlugin",
  "version": "1.0.0",
  "author": "LUCID",
  "description": "Metadata-only Canva plugin declaration.",
  "capabilities": ["design", "presentation"],
  "dependencies": [],
  "permissions": ["filesystem", "clipboard"],
  "platforms": ["universal"]
}
```

```json
{
  "plugin_id": "outlook-plugin",
  "name": "OutlookPlugin",
  "version": "1.0.0",
  "author": "LUCID",
  "description": "Metadata-only Microsoft Outlook plugin declaration.",
  "capabilities": ["email", "workflow"],
  "dependencies": [],
  "permissions": ["clipboard", "diagnostics"],
  "platforms": ["universal"]
}
```

```json
{
  "plugin_id": "word-plugin",
  "name": "WordPlugin",
  "version": "1.0.0",
  "author": "LUCID",
  "description": "Metadata-only Microsoft Word plugin declaration.",
  "capabilities": ["document"],
  "dependencies": [],
  "permissions": ["filesystem", "clipboard"],
  "platforms": ["universal"]
}
```

## Compatibility

Plugin versions use semantic versioning. A plugin is compatible when the host SDK major version matches the plugin minimum SDK major version and the host SDK is greater than or equal to the minimum SDK version. Migration targets allow a host to report `migration_available` for future major-version bridges.

## Sandbox Contract

The sandbox is architecture-only in Sprint 07. It records declared permissions, in-process metadata isolation, host API and permission-gate boundaries, data boundaries, and a metadata-only future execution policy. Runtime enforcement and external execution are intentionally outside this sprint.
