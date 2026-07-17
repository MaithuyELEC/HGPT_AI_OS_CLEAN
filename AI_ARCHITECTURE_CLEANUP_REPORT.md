# AI Architecture Cleanup Report

Date: 2026-07-14
Repository: `/Users/macos/Desktop/HGPT_AI_OS_CLEAN`

## Mission Result

PASS.

The duplicate provider-adapter architecture has been removed from source. The remaining production path is:

`EngineeringGenerationPipeline -> ProviderManager -> hgpt_ai_os.ai.client.ProviderFactory -> production provider`

## Kept

- `src/hgpt_ai_os/ai/client.py`
- `hgpt_ai_os.ai.client.ProviderFactory`
- `hgpt_ai_os.ai.client.AIManager`
- Production provider implementations in `hgpt_ai_os.ai.client`
- `src/hgpt_ai_os/providers/provider_manager.py` as the single manager boundary used by the engineering pipeline

## Removed

Dead AI plumbing removed from source:

- `src/hgpt_ai_os/providers/provider_factory.py`
- `src/hgpt_ai_os/providers/provider_registry.py`
- `src/hgpt_ai_os/providers/provider_selector.py`
- `src/hgpt_ai_os/providers/provider_policy.py`
- `src/hgpt_ai_os/providers/provider_request.py`
- `src/hgpt_ai_os/providers/provider_result.py`
- `src/hgpt_ai_os/providers/provider_capabilities.py`
- `src/hgpt_ai_os/providers/provider_health.py`
- `src/hgpt_ai_os/providers/base_provider.py`
- `src/hgpt_ai_os/providers/adapters/*.py`
- `tests/test_provider_layer.py`

## Scope Guard

No intentional changes were made to:

- GUI
- DOCX/export
- Packaging
- Installer
- Topic Engine

Existing dirty worktree changes in those areas were left untouched.

## Static Audit

Commands run from repo root:

```bash
PYTHONPATH=src PYTHONPYCACHEPREFIX=/private/tmp/lucid_pycache \
  python3 -m compileall -q src/hgpt_ai_os/ai src/hgpt_ai_os/providers src/hgpt_ai_os/engineering_pipeline

rg -n "^class ProviderFactory\b" src/hgpt_ai_os tests --glob '!**/__pycache__/**' | wc -l
rg -n "^class ProviderManager\b" src/hgpt_ai_os tests --glob '!**/__pycache__/**' | wc -l
rg -n "^class EngineeringGenerationPipeline\b" src/hgpt_ai_os/engineering_pipeline tests --glob '!**/__pycache__/**' | wc -l
find src/hgpt_ai_os/ai -maxdepth 1 -type f -name 'client.py' | wc -l
rg -n "hgpt_ai_os\.providers\.(provider_factory|provider_registry|provider_selector|provider_policy|provider_request|provider_result|provider_capabilities|provider_health|base_provider|adapters)|ProviderRegistry|ProviderSelector|ProviderSelectionPolicy|ProviderPolicyMode|BaseProviderAdapter|ProviderAdapterUnavailable" src/hgpt_ai_os tests --glob '!**/__pycache__/**' | wc -l
rg -ni "LegacyProviderFactory|legacy provider|legacy ai|ai legacy" src/hgpt_ai_os/ai src/hgpt_ai_os/providers src/hgpt_ai_os/engineering_pipeline tests --glob '!**/__pycache__/**' | wc -l
```

Results:

- ProviderFactory = 1
- ProviderManager = 1
- Engineering Pipeline = 1
- AI Client = 1
- Dead provider imports = 0
- AI legacy path refs = 0

## Verification

PASS:

```bash
PYTHONPATH=src PYTHONPYCACHEPREFIX=/private/tmp/lucid_pycache \
  python3 -m compileall -q src/hgpt_ai_os/ai src/hgpt_ai_os/providers src/hgpt_ai_os/engineering_pipeline
```

PASS:

```bash
PYTHONPATH=src PYTHONPYCACHEPREFIX=/private/tmp/lucid_pycache \
  python3 -m unittest tests.test_engineering_pipeline_v2
```

Result: `Ran 3 tests ... OK`

Known unrelated failures:

```bash
PYTHONPATH=src PYTHONPYCACHEPREFIX=/private/tmp/lucid_pycache \
  python3 -m unittest tests.test_engineering_pipeline_v2 tests.test_ai_config_resolver tests.test_content_generator_ai_routing
```

Result: failed in existing config/free-desktop expectations:

- `tests.test_ai_config_resolver.AIConfigResolverTests.test_is_free_desktop_mode_uses_config_manager_validation`
- `tests.test_ai_config_resolver.AIConfigResolverTests.test_missing_config_creates_default_config_and_enters_free_desktop_mode`
- `tests.test_ai_config_resolver.AIConfigResolverTests.test_provider_without_api_key_enters_free_desktop_mode`
- `tests.test_content_generator_ai_routing.ContentGeneratorAIRoutingTests.test_disabled_provider_does_not_call_ai`
- `tests.test_content_generator_ai_routing.ContentGeneratorAIRoutingTests.test_free_desktop_mode_does_not_call_ai`

Those failures were not modified in this cleanup because fixing them would cross into config/generator behavior outside the AI architecture cleanup scope.

## Final Architecture

Exactly one production AI architecture remains:

```text
EngineeringGenerationPipeline
  -> ProviderManager.generate_real_ai()
    -> validate_ai_provider_config()
    -> hgpt_ai_os.ai.client.ProviderFactory.create()
    -> OpenAIProvider / GeminiProvider / AnthropicProvider / OllamaProvider / AIManager
```

No separate adapter registry, selector, skeleton adapter factory, or legacy provider manager path remains in source.
