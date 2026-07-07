# Migration Plan: LUCID AUTO to LUCID PLATFORM

## Principle

LUCID PLATFORM replaces the product identity and long-term architecture, but it
does not break current LUCID AUTO production behavior. Migration is incremental,
tested, and sprint-bound.

## Sprint 01 Migration Notes

Current state:

- Existing LUCID AUTO production modules remain active.
- Packaging, GUI, AI provider code, knowledge retrieval, and content generation
  are not moved in Sprint 01.
- New platform APIs are available under `hgpt_ai_os.platform`.

Added compatibility path:

- New code can create `PlatformRuntime` without importing GUI or production
  modules.
- Future systems can register services through `PlatformServiceRegistry`.
- Lifecycle components can be started and stopped behind a stable protocol.

## Migration Order

1. Keep existing production entry points running.
2. Introduce platform abstractions as additive modules.
3. Wrap provider selection behind the platform runtime in Sprint 02.
4. Move knowledge registration behind platform contracts in Sprint 03.
5. Add agents and planner routing in Sprint 04.
6. Add plugin and marketplace boundaries in Sprints 05 and 06.
7. Add enterprise and digital factory architecture in Sprints 07 and 08.

## Backward Compatibility Checklist

- Do not remove current `hgpt_ai_os.production` entry points.
- Do not rename existing release artifacts during Sprint 01.
- Do not alter existing provider behavior during Sprint 01.
- Do not change GUI production workflow during Sprint 01.
- Keep new platform code importable with `PYTHONPATH=src`.
- Add tests before relying on a new platform contract.
