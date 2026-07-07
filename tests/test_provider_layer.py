from __future__ import annotations

import unittest

from hgpt_ai_os.contracts.diagnostics_contract import HealthReport
from hgpt_ai_os.contracts.provider_contract import (
    Provider,
    ProviderCapability,
    ProviderHealth,
    ProviderMetadata,
    ProviderRequest,
    ProviderResponse,
)
from hgpt_ai_os.providers import (
    ProviderFactory,
    ProviderHealthStatus,
    ProviderManager,
    ProviderPolicyMode,
    ProviderRegistry,
    ProviderSelectionPolicy,
    ProviderSelector,
)
from hgpt_ai_os.providers.adapters import (
    ClaudeAdapter,
    DeepSeekAdapter,
    GeminiAdapter,
    OllamaAdapter,
    OpenAIAdapter,
    OpenRouterAdapter,
    QwenAdapter,
)


class EchoProvider(Provider):
    def __init__(
        self,
        provider_id: str = "echo",
        *,
        free: bool = False,
        offline: bool = False,
        cost_rank: int = 50,
        latency_rank: int = 50,
        enterprise: bool = False,
    ) -> None:
        self._metadata = ProviderMetadata(
            provider_id=provider_id,
            display_name=provider_id.title(),
            version="1.0",
            capabilities=(ProviderCapability.TEXT_GENERATION,),
            metadata={
                "default_model": f"{provider_id}-model",
                "models": (f"{provider_id}-model", f"{provider_id}-fast"),
                "enabled": True,
                "free": free,
                "offline": offline,
                "cost_rank": cost_rank,
                "latency_rank": latency_rank,
                "enterprise": enterprise,
                "privacy_preserving": offline,
            },
        )

    @property
    def metadata(self) -> ProviderMetadata:
        return self._metadata

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        return ProviderResponse(request_id=request.request_id, text=request.prompt)

    def health(self) -> ProviderHealth:
        return ProviderHealth(
            metadata=self.metadata,
            report=HealthReport(component=self.metadata.provider_id, status="ready"),
        )


class ProviderRegistryTests(unittest.TestCase):
    def test_register_unregister_discover_and_metadata(self):
        registry = ProviderRegistry()
        provider = EchoProvider("echo", free=True)

        registry.register(provider)

        self.assertTrue(registry.contains("echo"))
        self.assertEqual(registry.get("echo"), provider)
        self.assertEqual(registry.provider_ids(), ("echo",))
        self.assertEqual(registry.metadata("echo").display_name, "Echo")
        self.assertEqual(registry.discover(ProviderCapability.TEXT_GENERATION)[0].provider_id, "echo")
        self.assertEqual(registry.unregister("echo"), provider)
        self.assertFalse(registry.contains("echo"))

    def test_rejects_duplicate_provider_ids(self):
        registry = ProviderRegistry()
        registry.register(EchoProvider("echo"))

        with self.assertRaises(KeyError):
            registry.register(EchoProvider("echo"))


class ProviderFactoryTests(unittest.TestCase):
    def test_factory_creates_all_required_adapter_skeletons(self):
        factory = ProviderFactory()
        expected = ("claude", "deepseek", "gemini", "ollama", "openai", "openrouter", "qwen")

        self.assertEqual(factory.available_provider_ids(), expected)
        self.assertIsInstance(factory.create("gemini"), GeminiAdapter)
        self.assertIsInstance(factory.create("openai"), OpenAIAdapter)
        self.assertIsInstance(factory.create("claude"), ClaudeAdapter)
        self.assertIsInstance(factory.create("openrouter"), OpenRouterAdapter)
        self.assertIsInstance(factory.create("ollama"), OllamaAdapter)
        self.assertIsInstance(factory.create("deepseek"), DeepSeekAdapter)
        self.assertIsInstance(factory.create("qwen"), QwenAdapter)

    def test_unknown_provider_is_rejected(self):
        with self.assertRaises(KeyError):
            ProviderFactory().create("missing")


class ProviderSelectorTests(unittest.TestCase):
    def _registry(self) -> ProviderRegistry:
        registry = ProviderRegistry()
        registry.register(EchoProvider("paid", cost_rank=50, latency_rank=5, enterprise=True))
        registry.register(EchoProvider("free", free=True, cost_rank=5, latency_rank=30))
        registry.register(EchoProvider("local", free=True, offline=True, cost_rank=0, latency_rank=10))
        return registry

    def test_free_first_strategy_selects_free_provider(self):
        selector = ProviderSelector(self._registry())

        result = selector.select(ProviderSelectionPolicy.free())

        self.assertEqual(result.provider_id, "local")
        self.assertEqual(result.model, "local-model")
        self.assertEqual(result.fallback_chain, ("free", "paid"))

    def test_offline_and_privacy_policies_select_local_provider(self):
        selector = ProviderSelector(self._registry())

        self.assertEqual(selector.select(ProviderSelectionPolicy.offline()).provider_id, "local")
        self.assertEqual(selector.select(ProviderSelectionPolicy.privacy()).provider_id, "local")

    def test_latency_and_cost_preferences_rank_candidates(self):
        selector = ProviderSelector(self._registry())

        low_latency = selector.select(ProviderSelectionPolicy.paid(latency_preference=True))
        low_cost = selector.select(ProviderSelectionPolicy.paid(cost_preference=True))

        self.assertEqual(low_latency.provider_id, "paid")
        self.assertEqual(low_cost.provider_id, "local")

    def test_enterprise_policy_honors_allowlist(self):
        selector = ProviderSelector(self._registry())
        policy = ProviderSelectionPolicy.enterprise(
            enterprise_providers=("paid",),
            allowed_providers=("paid", "free"),
        )

        self.assertEqual(selector.select(policy).provider_id, "paid")
        self.assertEqual(policy.mode, ProviderPolicyMode.ENTERPRISE)


class ProviderManagerTests(unittest.TestCase):
    def test_manager_initializes_skeletons_and_reports_disabled_health(self):
        manager = ProviderManager()
        manager.initialize_providers(("gemini", "ollama"))

        self.assertEqual(manager.registry.provider_ids(), ("gemini", "ollama"))
        self.assertEqual(manager.health("gemini").status, ProviderHealthStatus.DISABLED)
        self.assertEqual(manager.available_provider_ids(), ())

    def test_manager_executes_contract_provider_and_wraps_skeleton_error(self):
        registry = ProviderRegistry()
        registry.register(EchoProvider("echo"))
        registry.register(GeminiAdapter())
        manager = ProviderManager(registry=registry)

        request = ProviderRequest(request_id="req-1", prompt="hello")
        ok = manager.execute("echo", request)
        unavailable = manager.execute("gemini", request, retries=2)

        self.assertTrue(ok.ok)
        self.assertEqual(ok.response.text, "hello")
        self.assertFalse(unavailable.ok)
        self.assertFalse(unavailable.error.retryable)
        self.assertEqual(unavailable.attempts, 1)


class ProviderCompatibilityTests(unittest.TestCase):
    def test_existing_ai_layer_imports_are_unchanged(self):
        from hgpt_ai_os.ai import GeminiProvider, ProviderFactory as LegacyProviderFactory

        self.assertEqual(GeminiProvider.provider, "Gemini")
        self.assertTrue(hasattr(LegacyProviderFactory, "create"))

    def test_provider_package_exports_contract_layer(self):
        from hgpt_ai_os.providers import ProviderRegistry as ExportedRegistry

        self.assertIs(ExportedRegistry, ProviderRegistry)


if __name__ == "__main__":
    unittest.main()
