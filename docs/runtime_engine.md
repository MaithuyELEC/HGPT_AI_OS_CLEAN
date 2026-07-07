# Runtime Engine

Sprint 04 adds `hgpt_ai_os.runtime_engine` as an additive orchestration layer for
the LUCID PLATFORM runtime. It does not replace the existing production
workflow, GUI, provider layer, contract package, or AI generation path.

## Scope

The runtime engine coordinates runtime-only concerns:

- lifecycle: initialize, start, pause, resume, shutdown, dispose
- job state: queued, running, waiting, retrying, completed, failed, cancelled
- sequential task scheduling with dependency ordering, cancellation, and priority
- synchronous in-process event publishing, subscription, and history
- formal state transition rejection for illegal runtime and job moves
- retry policy modeling with exponential backoff calculations
- runtime health snapshots with provider health report aggregation
- execution metrics for counts, retries, and elapsed time

The package contains no HTTP code, SDK code, provider-specific implementation,
AI generation logic, GUI integration, or business workflow changes.

## Modules

- `runtime_engine.py` wires the runtime services into a small facade.
- `job_manager.py` owns runtime job records and lifecycle transitions.
- `task_scheduler.py` runs ready tasks sequentially and keeps a future
  parallel-ready task model.
- `event_bus.py` provides typed in-process events and retained history.
- `state_machine.py` enforces explicit legal transitions.
- `retry_manager.py` calculates retry eligibility and backoff delays.
- `health_monitor.py` reports runtime health, provider health, memory tracking
  status, and execution statistics.
- `lifecycle_manager.py` owns runtime lifecycle transitions and callbacks.
- `execution_context.py` carries runtime and correlation identifiers.
- `runtime_metrics.py` records execution, success, failure, retry, and elapsed
  time metrics.

## Compatibility

The engine is intentionally additive. Existing production entry points continue
to compile and run without importing `hgpt_ai_os.runtime_engine`. Provider
health is accepted as contract `HealthReport` values supplied by caller-owned
integration code; the engine does not inspect provider SDKs or call providers.

## Example

```python
from hgpt_ai_os.runtime_engine import RuntimeEngine

engine = RuntimeEngine()
engine.initialize()
engine.start()
engine.submit_job("job-1")
engine.start_job("job-1")
engine.add_task("prepare", lambda: "ready", priority=10)
engine.run_all_tasks()
engine.complete_job("job-1")
health = engine.health()
engine.shutdown()
engine.dispose()
```
