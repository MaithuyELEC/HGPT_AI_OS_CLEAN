# Integration Patch 03

## Goal

Make `PlatformRuntime` the only orchestration entry that invokes the legacy
production adapter.

## Result

The desktop path remains unchanged:

Desktop
-> ProductionWorker
-> ProductionService
-> PlatformRuntime.execute()
-> platform legacy adapter
-> legacy production builder

The legacy adapter is no longer exported from `hgpt_ai_os.platform`.
Tests exercise production execution through `PlatformRuntime` only.

## Boundary

No GUI behavior, output generation, DOCX generation, prompts, providers,
runtime contracts, agents, knowledge, plugins, or marketplace code changed.
