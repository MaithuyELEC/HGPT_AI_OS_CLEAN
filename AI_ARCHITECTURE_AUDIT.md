# AI Architecture Audit

Repository: `/Users/macos/Desktop/HGPT_AI_OS_CLEAN`

Scope: evidence-only audit of ProviderFactory implementations, AI clients, ProviderManager implementations, `generate()` entrypoints, reachable legacy paths, duplicate provider implementations, duplicate AI client implementations, and the desktop GUI production path.

No code was modified.

## Executive finding

There are two `ProviderFactory` implementations:

1. `src/hgpt_ai_os/ai/client.py::ProviderFactory` - ACTIVE for real production AI calls.
2. `src/hgpt_ai_os/providers/provider_factory.py::ProviderFactory` - ACTIVE only for provider metadata/adapter registry, but UNUSED for real production AI generation because its adapters do not implement transport.

Production should keep exactly one real generation factory:

**KEEP for production AI generation: `hgpt_ai_os.ai.client.ProviderFactory`.**

Reason: the desktop GUI production path enters `EngineeringGenerationPipeline`, which calls `ProviderManager.generate_real_ai()`, and that method explicitly delegates real AI generation to `LegacyProviderFactory.create(configured)`, where `LegacyProviderFactory` is imported from `hgpt_ai_os.ai.client.ProviderFactory`.

Evidence:

- `src/hgpt_ai_os/engineering_pipeline/pipeline.py:167` creates `ProviderManager()`.
- `src/hgpt_ai_os/engineering_pipeline/pipeline.py:230` calls `self.provider_manager.generate_real_ai(system_prompt, user_prompt)`.
- `src/hgpt_ai_os/providers/provider_manager.py:7` imports `ProviderFactory as LegacyProviderFactory` from `hgpt_ai_os.ai.client`.
- `src/hgpt_ai_os/providers/provider_manager.py:74` calls `LegacyProviderFactory.create(configured)`.
- `src/hgpt_ai_os/providers/provider_manager.py:85` calls `provider.generate(system_prompt, user_prompt)`.
- `src/hgpt_ai_os/providers/base_provider.py:71-74` shows the newer adapter stack raises `ProviderAdapterUnavailable` instead of implementing transport.

## Status legend

- ACTIVE: on the current desktop GUI production path or directly used for real provider calls.
- LEGACY: still reachable through older/manual/CLI-style flows or retained compatibility API, but not the current desktop GUI production path.
- UNUSED: importable or tested, but not reached by production GUI real AI generation.
- DEAD: no discovered runtime caller in `src`, `app`, `ui`, or root production entrypoints.

## 1. Every ProviderFactory

| Status | Factory | Evidence | Notes |
|---|---|---|---|
| ACTIVE | `src/hgpt_ai_os/ai/client.py::ProviderFactory` | Defined at `src/hgpt_ai_os/ai/client.py:768`; `create()` at `src/hgpt_ai_os/ai/client.py:772`; returns `OpenAIProvider`, `GeminiProvider`, `AnthropicProvider`, `OllamaProvider`, or `AIManager` at `src/hgpt_ai_os/ai/client.py:774-783`; called by production bridge at `src/hgpt_ai_os/providers/provider_manager.py:74`. | This is the real provider factory for production AI generation. Keep this path for production. |
| UNUSED for real AI generation / ACTIVE for metadata registry | `src/hgpt_ai_os/providers/provider_factory.py::ProviderFactory` | Defined at `src/hgpt_ai_os/providers/provider_factory.py:22`; registers adapter builders at `src/hgpt_ai_os/providers/provider_factory.py:25-31`; creates adapters at `src/hgpt_ai_os/providers/provider_factory.py:39-42`; used by `ProviderManager.initialize_providers()` at `src/hgpt_ai_os/providers/provider_manager.py:30-34`. | This factory creates contract-only adapters. It is not the production real-AI factory. |

## 2. Every AI Client / Provider Implementation

### Real AI clients and providers

| Status | Client / Provider | Evidence | Notes |
|---|---|---|---|
| ACTIVE | `OpenAIProvider` | Defined at `src/hgpt_ai_os/ai/client.py:199`; real HTTP `generate()` at `src/hgpt_ai_os/ai/client.py:217`; selected by factory at `src/hgpt_ai_os/ai/client.py:774-775`; direct settings test call at `src/hgpt_ai_os/settings/provider_test.py:37-41`. | Real OpenAI transport. |
| ACTIVE | `GeminiProvider` | Defined at `src/hgpt_ai_os/ai/client.py:118`; wraps `GeminiClient` at `src/hgpt_ai_os/ai/client.py:123-129`; `generate()` delegates to client at `src/hgpt_ai_os/ai/client.py:153-154`; selected by factory at `src/hgpt_ai_os/ai/client.py:776-777`. | Real Gemini provider wrapper. |
| ACTIVE | `GeminiClient` | Defined at `src/hgpt_ai_os/ai/gemini_client.py:64`; HTTP `generate()` at `src/hgpt_ai_os/ai/gemini_client.py:88`; endpoint construction at `src/hgpt_ai_os/ai/gemini_client.py:247-251`; settings test direct call at `src/hgpt_ai_os/settings/provider_test.py:31-36`. | Real Gemini transport. |
| ACTIVE | `AnthropicProvider` | Defined at `src/hgpt_ai_os/ai/client.py:361`; HTTP `generate()` at `src/hgpt_ai_os/ai/client.py:379`; selected by factory at `src/hgpt_ai_os/ai/client.py:778-779`; settings test direct call at `src/hgpt_ai_os/settings/provider_test.py:42-46`. | Real Anthropic transport, though config validation supports provider name `anthropic` while the metadata adapter stack uses `claude`. |
| ACTIVE | `OllamaProvider` | Defined at `src/hgpt_ai_os/ai/client.py:530`; local HTTP `generate()` at `src/hgpt_ai_os/ai/client.py:548`; selected by factory at `src/hgpt_ai_os/ai/client.py:780-781`; included in `AIManager` fallback at `src/hgpt_ai_os/ai/client.py:675-679`. | Real local Ollama transport, but `validate_ai_provider_config()` does not list `ollama` as a supported configured provider at `src/hgpt_ai_os/ai/config_resolver.py:14`. |
| LEGACY | `LucidAI` | Defined at `src/hgpt_ai_os/ai/client.py:750`; constructs provider via `ProviderFactory.create()` at `src/hgpt_ai_os/ai/client.py:753-755`; delegates `generate()` at `src/hgpt_ai_os/ai/client.py:757-762`; used by legacy `ContentGenerator` at `src/hgpt_ai_os/content/generator.py:357-370`. | Backward-compatible facade. Not on current GUI production path. |
| LEGACY | `AIManager` | Defined at `src/hgpt_ai_os/ai/client.py:669`; default providers at `src/hgpt_ai_os/ai/client.py:674-679`; failover loop at `src/hgpt_ai_os/ai/client.py:681-727`; selectable by factory for `manager`, `ai`, or `lucid` at `src/hgpt_ai_os/ai/client.py:782-783`. | Real failover manager, but not selected by the current config resolver unless explicitly requested outside normal supported provider values. |
| LEGACY | `GeminiAI` | Defined at `src/hgpt_ai_os/ai/gemini_client.py:311`; wraps `GeminiClient` at `src/hgpt_ai_os/ai/gemini_client.py:314-315`; calls `self.client.generate("", prompt)` at `src/hgpt_ai_os/ai/gemini_client.py:322`. | Backward-compatible older Gemini facade. No discovered production GUI caller. |

### Contract-only provider adapter implementations

All classes below extend `BaseProviderAdapter`, whose `generate()` raises `ProviderAdapterUnavailable` at `src/hgpt_ai_os/providers/base_provider.py:71-74`.

| Status | Adapter | Evidence | Notes |
|---|---|---|---|
| UNUSED for real AI generation | `OpenAIAdapter` | `src/hgpt_ai_os/providers/adapters/openai_adapter.py:7-20`; registered at `src/hgpt_ai_os/providers/provider_factory.py:26`. | Duplicate OpenAI provider identity, no transport. |
| UNUSED for real AI generation | `GeminiAdapter` | `src/hgpt_ai_os/providers/adapters/gemini_adapter.py:7-17`; registered at `src/hgpt_ai_os/providers/provider_factory.py:25`. | Duplicate Gemini provider identity, no transport. |
| UNUSED for real AI generation | `OllamaAdapter` | `src/hgpt_ai_os/providers/adapters/ollama_adapter.py:7-19`; registered at `src/hgpt_ai_os/providers/provider_factory.py:29`. | Duplicate Ollama provider identity, no transport. |
| UNUSED for real AI generation | `ClaudeAdapter` | `src/hgpt_ai_os/providers/adapters/claude_adapter.py:7-17`; registered at `src/hgpt_ai_os/providers/provider_factory.py:27`. | Duplicate Anthropic/Claude concept with different naming from `AnthropicProvider`. |
| UNUSED for real AI generation | `DeepSeekAdapter` | `src/hgpt_ai_os/providers/adapters/deepseek_adapter.py:7-17`; registered at `src/hgpt_ai_os/providers/provider_factory.py:30`. | Metadata-only adapter. |
| UNUSED for real AI generation | `OpenRouterAdapter` | `src/hgpt_ai_os/providers/adapters/openrouter_adapter.py:7-16`; registered at `src/hgpt_ai_os/providers/provider_factory.py:28`. | Metadata-only adapter. |
| UNUSED for real AI generation | `QwenAdapter` | `src/hgpt_ai_os/providers/adapters/qwen_adapter.py:7-17`; registered at `src/hgpt_ai_os/providers/provider_factory.py:31`. | Metadata-only adapter. |

## 3. Every ProviderManager

| Status | ProviderManager | Evidence | Notes |
|---|---|---|---|
| ACTIVE | `src/hgpt_ai_os/providers/provider_manager.py::ProviderManager` | Defined at `src/hgpt_ai_os/providers/provider_manager.py:20`; instantiated by production pipeline at `src/hgpt_ai_os/engineering_pipeline/pipeline.py:167`; `generate_real_ai()` at `src/hgpt_ai_os/providers/provider_manager.py:54-89`; contract adapter `execute()` at `src/hgpt_ai_os/providers/provider_manager.py:91-112`. | This is the only discovered ProviderManager. It has two roles: production bridge to legacy real providers, and adapter registry executor. |

No other `ProviderManager` class was found in `src`, `app`, `ui`, or root `production.py`.

## 4. Every generate() Path

### Desktop GUI production path

Status: ACTIVE

1. `src/hgpt_ai_os/gui/main_window.py:713` - `MainWindow.generate()` is the generate button handler.
2. `src/hgpt_ai_os/gui/main_window.py:789-795` - constructs and starts `ProductionWorker(topic)`.
3. `src/hgpt_ai_os/gui/worker.py:60-68` - `ProductionWorker.run()` creates `ProductionService()` and calls `service.run(self.topic)`.
4. `src/hgpt_ai_os/gui/production_service.py:16-24` - `ProductionService.run()` calls `PlatformRuntime.execute(...)`.
5. `src/hgpt_ai_os/platform/runtime.py:106-122` - `PlatformRuntime.execute()` gets `LegacyProductionAdapter` and calls `adapter.execute(...)`.
6. `src/hgpt_ai_os/platform/legacy_production_adapter.py:17-30` - `LegacyProductionAdapter.execute()` calls `production.build_outputs(...)`.
7. `src/hgpt_ai_os/production.py:27-75` - `build_outputs()` constructs `EngineeringGenerationPipeline()`.
8. `src/hgpt_ai_os/production.py:105-112` - `build_outputs()` calls `pipeline.generate_documents(...)`.
9. `src/hgpt_ai_os/engineering_pipeline/pipeline.py:183-201` - `generate_documents()` calls `build_record()`.
10. `src/hgpt_ai_os/engineering_pipeline/pipeline.py:203-212` - `build_record()` calls `_ai_record()`.
11. `src/hgpt_ai_os/engineering_pipeline/pipeline.py:214-230` - `_ai_record()` calls either injected `self.ai.generate(...)` or, in production, `self.provider_manager.generate_real_ai(...)`.
12. `src/hgpt_ai_os/providers/provider_manager.py:54-89` - `generate_real_ai()` validates config, calls `LegacyProviderFactory.create(configured)`, then calls the selected real provider's `generate()`.
13. `src/hgpt_ai_os/ai/client.py:772-785` - legacy factory chooses `OpenAIProvider`, `GeminiProvider`, `AnthropicProvider`, `OllamaProvider`, or `AIManager`.

### Real provider generate methods

| Status | Method | Evidence | Reachability |
|---|---|---|---|
| ACTIVE | `GeminiClient.generate()` | `src/hgpt_ai_os/ai/gemini_client.py:88-227` | Called by `GeminiProvider.generate()` and settings connection test. |
| ACTIVE | `GeminiProvider.generate()` | `src/hgpt_ai_os/ai/client.py:131-164` | Called when factory selects `gemini`. |
| ACTIVE | `OpenAIProvider.generate()` | `src/hgpt_ai_os/ai/client.py:217-307` | Called when factory selects `openai`. |
| ACTIVE | `AnthropicProvider.generate()` | `src/hgpt_ai_os/ai/client.py:379-470` | Called when factory selects `anthropic`. |
| ACTIVE | `OllamaProvider.generate()` | `src/hgpt_ai_os/ai/client.py:548-638` | Called when factory selects `ollama` or `AIManager` failover uses Ollama. |
| LEGACY | `AIManager.generate()` | `src/hgpt_ai_os/ai/client.py:681-727` | Selectable by factory aliases `manager`, `ai`, `lucid`; not part of normal config-supported desktop provider set. |
| LEGACY | `LucidAI.generate()` | `src/hgpt_ai_os/ai/client.py:757-762` | Used by legacy `ContentGenerator` when not in free desktop mode. |

### Provider adapter generate methods

| Status | Method | Evidence | Reachability |
|---|---|---|---|
| UNUSED for real AI generation | `BaseProviderAdapter.generate()` | `src/hgpt_ai_os/providers/base_provider.py:71-74` | Raises unavailable. Called only through `ProviderManager.execute()` at `src/hgpt_ai_os/providers/provider_manager.py:91-122` if adapter registry execution is used. |
| UNUSED for real AI generation | `ProviderManager._try_generate()` | `src/hgpt_ai_os/providers/provider_manager.py:114-135` | Calls adapter `provider.generate(request)`, not the real provider clients. |

### Legacy content generate methods

| Status | Method | Evidence | Reachability |
|---|---|---|---|
| LEGACY | `ContentGenerator.generate()` | `src/hgpt_ai_os/content/generator.py:394-416` | Used by `LucidOrchestrator`, not by current desktop GUI production. |
| LEGACY | `ContentGenerator._generate_with_llm()` | `src/hgpt_ai_os/content/generator.py:493-567` | Calls `self.ai.generate(...)` at `src/hgpt_ai_os/content/generator.py:510`; `self.ai` can be `LucidAI` from `src/hgpt_ai_os/content/generator.py:357-370`. |
| LEGACY | `ContentGenerator.generate_facebook()` | `src/hgpt_ai_os/content/generator.py:418-419` | Called by `LucidOrchestrator` at `src/hgpt_ai_os/orchestrator/lucid_orchestrator.py:41-44`. |
| LEGACY | `ContentGenerator.generate_tiktok()` | `src/hgpt_ai_os/content/generator.py:421-422` | Called by `LucidOrchestrator` at `src/hgpt_ai_os/orchestrator/lucid_orchestrator.py:58`. |
| LEGACY | `ContentGenerator.generate_image_prompt()` | `src/hgpt_ai_os/content/generator.py:424-425` | Called by `LucidOrchestrator` at `src/hgpt_ai_os/orchestrator/lucid_orchestrator.py:59`. |
| LEGACY | `ContentGenerator.generate_video_prompt()` | `src/hgpt_ai_os/content/generator.py:427-428` | Called by `LucidOrchestrator` at `src/hgpt_ai_os/orchestrator/lucid_orchestrator.py:60`. |
| LEGACY | `ContentGenerator.generate_hashtags()` | `src/hgpt_ai_os/content/generator.py:430-449` | Called by `LucidOrchestrator` at `src/hgpt_ai_os/orchestrator/lucid_orchestrator.py:61`. |
| LEGACY | `ContentGenerator.generate_checklist()` | `src/hgpt_ai_os/content/generator.py:451-461` | Called by `LucidOrchestrator` at `src/hgpt_ai_os/orchestrator/lucid_orchestrator.py:62`. |
| LEGACY | `ContentGenerator.generate_seo()` | `src/hgpt_ai_os/content/generator.py:463-464` | Called by `LucidOrchestrator` at `src/hgpt_ai_os/orchestrator/lucid_orchestrator.py:46-49`. |

### Non-AI generate methods discovered

These are not AI provider paths.

| Status | Method | Evidence | Notes |
|---|---|---|---|
| UNUSED for AI architecture | `ProjectGenerator.generate()` | `src/hgpt_ai_os/builder/generator.py:8` | Project scaffolding, not AI generation. |
| UNUSED for AI architecture | `TopicIntelligenceEngine.generate()` | `src/hgpt_ai_os/topic_engine/__init__.py:84` | Offline/topic-aware content generation, not provider client transport. |

## 5. Which Path the GUI Actually Calls

The current desktop GUI calls the production engineering pipeline, not the legacy marketing `ContentGenerator`.

Actual GUI path:

`MainWindow.generate()` -> `ProductionWorker.run()` -> `ProductionService.run()` -> `PlatformRuntime.execute()` -> `LegacyProductionAdapter.execute()` -> `hgpt_ai_os.production.build_outputs()` -> `EngineeringGenerationPipeline.generate_documents()` -> `EngineeringGenerationPipeline._ai_record()` -> `ProviderManager.generate_real_ai()` -> `hgpt_ai_os.ai.client.ProviderFactory.create()` -> selected real provider `generate()`.

Evidence:

- GUI button handler and worker start: `src/hgpt_ai_os/gui/main_window.py:713-795`.
- Worker service call: `src/hgpt_ai_os/gui/worker.py:60-68`.
- Production service runtime call: `src/hgpt_ai_os/gui/production_service.py:16-24`.
- Runtime adapter call: `src/hgpt_ai_os/platform/runtime.py:106-122`.
- Legacy adapter calls production module: `src/hgpt_ai_os/platform/legacy_production_adapter.py:17-30`.
- Production module initializes pipeline: `src/hgpt_ai_os/production.py:74-75`.
- Production module calls `pipeline.generate_documents(...)`: `src/hgpt_ai_os/production.py:105-112`.
- Pipeline calls `ProviderManager.generate_real_ai(...)`: `src/hgpt_ai_os/engineering_pipeline/pipeline.py:214-230`.
- ProviderManager calls legacy factory and selected provider generate: `src/hgpt_ai_os/providers/provider_manager.py:54-89`.

## 6. Legacy AI Paths Still Reachable

| Status | Path | Evidence | Why it is legacy |
|---|---|---|---|
| LEGACY | Root `production.py` -> `LucidOrchestrator().run()` -> `ContentGenerator` -> `LucidAI` | Root `production.py:1-4` calls `LucidOrchestrator`; orchestrator imports `ContentGenerator` at `src/hgpt_ai_os/orchestrator/lucid_orchestrator.py:10`, instantiates it at `src/hgpt_ai_os/orchestrator/lucid_orchestrator.py:39`, and calls its generate wrappers at `src/hgpt_ai_os/orchestrator/lucid_orchestrator.py:41-62`. | This is older marketing-document generation. It does not match the current desktop GUI production path. |
| LEGACY | `ContentGenerator` -> `LucidAI` -> `ProviderFactory` | `ContentGenerator.__init__()` may construct `LucidAI()` at `src/hgpt_ai_os/content/generator.py:357-370`; `_generate_with_llm()` calls `self.ai.generate(...)` at `src/hgpt_ai_os/content/generator.py:510`; `LucidAI.generate()` delegates to its provider at `src/hgpt_ai_os/ai/client.py:757-762`. | Still reachable from `LucidOrchestrator`; not used by `MainWindow.generate()`. |
| LEGACY | `GeminiAI` facade | `src/hgpt_ai_os/ai/gemini_client.py:311-326`; exported at `src/hgpt_ai_os/ai/__init__.py:20-25`. | Compatibility facade; no discovered production GUI caller. |
| LEGACY | `AIManager` failover alias | `src/hgpt_ai_os/ai/client.py:669-727`; factory aliases at `src/hgpt_ai_os/ai/client.py:782-783`. | Real code, but not selected by normal config values in `SUPPORTED_PROVIDERS` at `src/hgpt_ai_os/ai/config_resolver.py:14`. |

## 7. Duplicate Provider Implementations

| Provider concept | Real implementation | Duplicate adapter implementation | Status |
|---|---|---|---|
| OpenAI | `OpenAIProvider` in `src/hgpt_ai_os/ai/client.py:199-359` | `OpenAIAdapter` in `src/hgpt_ai_os/providers/adapters/openai_adapter.py:7-20` | Duplicate. Real implementation ACTIVE; adapter UNUSED for real AI generation. |
| Gemini | `GeminiProvider` in `src/hgpt_ai_os/ai/client.py:118-197` plus `GeminiClient` in `src/hgpt_ai_os/ai/gemini_client.py:64-309` | `GeminiAdapter` in `src/hgpt_ai_os/providers/adapters/gemini_adapter.py:7-17` | Duplicate. Real implementation ACTIVE; adapter UNUSED for real AI generation. |
| Ollama | `OllamaProvider` in `src/hgpt_ai_os/ai/client.py:530-667` | `OllamaAdapter` in `src/hgpt_ai_os/providers/adapters/ollama_adapter.py:7-19` | Duplicate. Real implementation ACTIVE as factory/AIManager option; adapter UNUSED for real AI generation. |
| Anthropic / Claude | `AnthropicProvider` in `src/hgpt_ai_os/ai/client.py:361-528` | `ClaudeAdapter` in `src/hgpt_ai_os/providers/adapters/claude_adapter.py:7-17` | Duplicate concept with naming mismatch. Real implementation ACTIVE when configured as `anthropic`; adapter UNUSED for real AI generation and registered as `claude`. |

## 8. Duplicate AI Client Implementations

| Status | Implementation | Evidence | Notes |
|---|---|---|---|
| ACTIVE | `GeminiClient` transport | `src/hgpt_ai_os/ai/gemini_client.py:64-309` | Dedicated Gemini HTTP client used by `GeminiProvider`. |
| ACTIVE | Provider transports embedded in `ai/client.py` | `OpenAIProvider.generate()` at `src/hgpt_ai_os/ai/client.py:217-307`; `AnthropicProvider.generate()` at `src/hgpt_ai_os/ai/client.py:379-470`; `OllamaProvider.generate()` at `src/hgpt_ai_os/ai/client.py:548-638`. | These are provider clients implemented as provider classes, not split into separate client modules. |
| LEGACY | `LucidAI` facade | `src/hgpt_ai_os/ai/client.py:750-765` | Compatibility client/facade over `ProviderFactory`. |
| LEGACY | `GeminiAI` facade | `src/hgpt_ai_os/ai/gemini_client.py:311-326` | Compatibility facade over `GeminiClient`. |
| UNUSED for real AI generation | Adapter stack | `BaseProviderAdapter.generate()` raises at `src/hgpt_ai_os/providers/base_provider.py:71-74`. | Duplicate provider-client abstraction without working transport. |

## 9. ACTIVE / DEAD / LEGACY / UNUSED Summary

### ACTIVE

- `src/hgpt_ai_os/gui/main_window.py::MainWindow.generate`
- `src/hgpt_ai_os/gui/worker.py::ProductionWorker.run`
- `src/hgpt_ai_os/gui/production_service.py::ProductionService.run`
- `src/hgpt_ai_os/platform/runtime.py::PlatformRuntime.execute`
- `src/hgpt_ai_os/platform/legacy_production_adapter.py::LegacyProductionAdapter.execute`
- `src/hgpt_ai_os/production.py::build_outputs`
- `src/hgpt_ai_os/engineering_pipeline/pipeline.py::EngineeringGenerationPipeline`
- `src/hgpt_ai_os/providers/provider_manager.py::ProviderManager.generate_real_ai`
- `src/hgpt_ai_os/ai/client.py::ProviderFactory`
- `src/hgpt_ai_os/ai/client.py::OpenAIProvider`
- `src/hgpt_ai_os/ai/client.py::GeminiProvider`
- `src/hgpt_ai_os/ai/gemini_client.py::GeminiClient`
- `src/hgpt_ai_os/ai/client.py::AnthropicProvider`
- `src/hgpt_ai_os/ai/client.py::OllamaProvider`

### LEGACY

- `src/hgpt_ai_os/content/generator.py::ContentGenerator`
- `src/hgpt_ai_os/ai/client.py::LucidAI`
- `src/hgpt_ai_os/ai/client.py::AIManager`
- `src/hgpt_ai_os/ai/gemini_client.py::GeminiAI`
- `src/hgpt_ai_os/orchestrator/lucid_orchestrator.py::LucidOrchestrator`
- Root `production.py` entrypoint that calls `LucidOrchestrator`

### UNUSED

- `src/hgpt_ai_os/providers/provider_factory.py::ProviderFactory` for real AI generation
- `src/hgpt_ai_os/providers/base_provider.py::BaseProviderAdapter.generate` for real AI generation
- `src/hgpt_ai_os/providers/adapters/*Adapter` for real AI generation
- `src/hgpt_ai_os/providers/provider_manager.py::ProviderManager.execute` for real AI generation

### DEAD

No provider factory, provider manager, or real provider client was classified as fully DEAD based on this audit, because each is either reachable from production, reachable from legacy/manual flows, exported as compatibility API, used by settings/provider tests, or used by the adapter registry. The dead-risk area is architectural duplication, not a confirmed unreachable provider file.

## Final recommendation

Production should keep `hgpt_ai_os.ai.client.ProviderFactory` as the single real provider factory.

The `hgpt_ai_os.providers.ProviderFactory` stack should not be treated as production AI generation until its adapters implement real transport or are intentionally wired as the sole provider abstraction. Today it is a metadata/contract adapter layer, while production real AI generation still depends on the legacy factory in `hgpt_ai_os.ai.client`.
