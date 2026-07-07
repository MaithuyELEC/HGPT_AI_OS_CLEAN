# Integration Patch 02: Runtime Orchestration Entry

## Flow

```text
Desktop
-> ProductionWorker
-> ProductionService
-> PlatformRuntime.execute()
-> LegacyProductionAdapter.execute()
-> production.build_outputs()
```

`ProductionService` now delegates production execution to
`PlatformRuntime.execute(...)`. The runtime owns legacy production orchestration:
it selects the legacy adapter, resolves the next production day, calls the
adapter, collects generated `.docx` files from the returned output directory,
and returns the same `ProductionResult` consumed by Desktop.

`LegacyProductionAdapter` is intentionally thin. It forwards the day, topic, and
open-folder flag to the existing `production.build_outputs(...)` function
without owning orchestration decisions.

## Compatibility

This patch does not change Desktop behavior, `ProductionWorker`, GUI rendering,
provider selection, runtime contracts, knowledge retrieval, marketplace,
plugins, AI prompts, DOCX generation, or generated output.
