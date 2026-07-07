# Universal Provider Layer

The provider layer lives in `src/hgpt_ai_os/providers/` and is built on the
Sprint 02 provider contracts in `src/hgpt_ai_os/contracts/provider_contract.py`.
It does not replace the existing production AI path, does not modify runtime
contracts, and does not introduce HTTP or SDK calls.

## Architecture

- `base_provider.py` defines contract-only adapter behavior and shared adapter
  metadata.
- `provider_registry.py` registers, unregisters, discovers, and exposes provider
  metadata.
- `provider_factory.py` instantiates adapters only.
- `provider_manager.py` initializes providers, reports health, checks
  availability, and wraps retry attempts.
- `provider_selector.py` chooses providers and models from metadata.
- `provider_policy.py` defines free, paid, offline, enterprise, and privacy
  policy modes.
- `provider_health.py` maps provider health to Ready, Unavailable,
  QuotaExceeded, Offline, and Disabled states.
- `provider_request.py`, `provider_result.py`, and
  `provider_capabilities.py` hold provider-layer data objects.

## Adapters

The initial adapters are skeletons for Gemini, OpenAI, Claude, OpenRouter,
Ollama, DeepSeek, and Qwen. They expose stable metadata through the Sprint 02
provider contract and report `disabled` health by default. They do not perform
API calls, HTTP calls, SDK calls, or vendor-specific generation.

## Selection Strategy

`ProviderSelector` ranks registered providers using metadata only:

- Free-first favors providers marked as free.
- Offline preference favors local providers.
- Latency preference sorts by the adapter latency rank.
- Cost preference sorts by the adapter cost rank.
- Enterprise policy can restrict selection to approved provider IDs.
- Privacy policy requires privacy-preserving metadata, currently represented by
  offline/local providers.

The selector also returns a fallback chain as an ordered list of provider IDs.
That chain is a design artifact for future execution flow and is not a vendor
failover implementation.

## Compatibility

The provider package is additive. Existing `hgpt_ai_os.ai` imports, GUI code,
runtime code, and business logic continue to use their current paths. Future
provider implementations should be added inside adapter modules while preserving
the Sprint 02 provider contracts.
