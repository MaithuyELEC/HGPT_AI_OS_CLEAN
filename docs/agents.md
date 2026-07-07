# Universal Agent System

Sprint 05 adds `hgpt_ai_os.agents_core` as an isolated Universal Agent System built on the frozen platform foundation, contracts, provider layer, and runtime engine. It does not modify GUI, providers, runtime engine, production workflow, or AI generation.

## Package

The package lives at `src/hgpt_ai_os/agents_core/` and contains:

- `agent_registry.py` for registering, unregistering, discovering, and reading version/capability metadata.
- `agent_manager.py` for load, initialize, enable, disable, health, and shutdown lifecycle actions.
- `agent_factory.py` for instantiating agent skeletons only.
- `agent_executor.py` for execution orchestration only.
- `agent_context.py` for execution context, memory scope, permissions, inputs, and metadata.
- `agent_permissions.py` for filesystem, knowledge, provider, plugin, workflow, and diagnostics permissions.
- `agent_memory_scope.py` for conversation, session, project, temporary, and read-only scopes.
- `agent_result.py` for execution results.
- `agent_capability.py` for reasoning, writing, coding, knowledge, vision, automation, and planning capabilities.
- `agent_health.py` for ready, busy, disabled, failed, and offline health states.

## Built-In Skeletons

The package exports metadata-only built-in skeletons:

- `EngineeringAgent`
- `OfficeAgent`
- `MarketingAgent`
- `EducationAgent`
- `FinanceAgent`
- `HealthAgent`
- `LegalAgent`
- `ProgrammingAgent`
- `TravelAgent`
- `CookingAgent`
- `DailyLifeAgent`
- `DigitalFactoryAgent`
- `SteelEngineeringAgent`

These skeletons declare identifiers, display names, versions, permissions, capabilities, and descriptions. They contain no prompts, provider calls, AI logic, HTTP, SDK usage, or domain implementation.

## Execution Boundary

`AgentExecutor` performs orchestration only. It checks registry state, agent health, and declared permissions, then delegates to a supplied handler or an already-loaded agent object when one exposes `execute`. Metadata-only skeletons succeed as non-executed skeletons when invoked without a handler.

## Compatibility

Sprint 05 is additive. Existing contracts, providers, runtime engine, GUI, production workflow, and AI generation modules are not changed by the Universal Agent System.
