# HGPT_AI_OS Architecture Map

## Current Status

| Module | Status | Note |
|---|---:|---|
| CLI | ✅ DONE | help / version / status / maintenance run |
| Kernel | ✅ DONE | HGPTKernel |
| AgentManager | ✅ DONE | Register / run agent |
| ServiceContainer | ✅ DONE | Basic DI |
| Registry | ✅ DONE | Central registry |
| Runtime | ✅ EXISTS | Need final check later |
| Queue | ✅ EXISTS | Freeze for now |
| Task | ✅ EXISTS | Checked OK |
| Workflow | 🟡 EXISTS | Not checked |
| Database | 🟡 EXISTS | engine/schema/repository exist |
| Models | 🟡 EXISTS | Empty or pending |
| Services | 🟡 EXISTS | Pending |
| Knowledge | 🟡 EXISTS | Pending |
| Memory | ✅ BASIC | Simple memory |
| MaintenanceAgent | ✅ DONE | First agent running |

## Frozen Modules

Do not modify unless required:

- cli
- kernel
- task
- queue
- runtime
- maintenance agent

## Next Priority

Fastest path to finish HGPT_AI_OS Core:

1. Confirm Database works.
2. Connect Task to Database.
3. Add CLI command for task.
4. Add File Output Engine later.
5. Add Automation Agent later.

## Current Boot Command

```bash
PYTHONPATH=src python3 -m hgpt_ai_os.cli.main maintenance run
