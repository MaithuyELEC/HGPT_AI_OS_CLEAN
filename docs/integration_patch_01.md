# Integration Patch 01: Desktop to Platform Runtime

## Old Flow

The Desktop application previously entered the legacy production pipeline
directly:

```text
Desktop
-> ProductionWorker
-> ProductionService
-> production.build_outputs()
```

`ProductionService` selected the next day, called `production.build_outputs()`,
collected generated `.docx` files from the returned directory, and returned the
same `ProductionResult` consumed by the GUI.

## New Flow

The Desktop application now enters production through `PlatformRuntime`:

```text
Desktop
-> ProductionWorker
-> ProductionService
-> PlatformRuntime
-> LegacyProductionAdapter
-> production.build_outputs()
```

`PlatformRuntime` registers `LegacyProductionAdapter` as the default
`legacy.production` service. `ProductionService` retrieves that adapter from the
runtime registry and delegates output generation to it. The adapter preserves the
existing production behavior by calling `production.next_day()` and
`production.build_outputs(day, topic, open_output_folder=False)`.

## Migration

This patch is integration-only. It does not change GUI behavior, generated
output, DOCX generation, AI prompts, provider selection, knowledge retrieval,
plugin behavior, or marketplace behavior.

Existing callers can continue using `ProductionService.run(topic)`. Tests and
future runtime integrations can inject a `PlatformRuntime` with a registered
`legacy.production` adapter to verify or replace the production entry point
without touching Desktop UI code.
