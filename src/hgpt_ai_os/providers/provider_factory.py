"""Provider factory that instantiates adapters only."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from hgpt_ai_os.contracts.provider_contract import Provider
from hgpt_ai_os.providers.adapters import (
    ClaudeAdapter,
    DeepSeekAdapter,
    GeminiAdapter,
    OllamaAdapter,
    OpenAIAdapter,
    OpenRouterAdapter,
    QwenAdapter,
)

ProviderBuilder = Callable[[dict[str, Any] | None], Provider]


class ProviderFactory:
    def __init__(self) -> None:
        self._builders: dict[str, ProviderBuilder] = {}
        self.register_builder("gemini", GeminiAdapter)
        self.register_builder("openai", OpenAIAdapter)
        self.register_builder("claude", ClaudeAdapter)
        self.register_builder("openrouter", OpenRouterAdapter)
        self.register_builder("ollama", OllamaAdapter)
        self.register_builder("deepseek", DeepSeekAdapter)
        self.register_builder("qwen", QwenAdapter)

    def register_builder(self, provider_id: str, builder: ProviderBuilder) -> None:
        normalized_id = provider_id.strip()
        if not normalized_id:
            raise ValueError("provider_id must not be empty")
        self._builders[normalized_id] = builder

    def create(self, provider_id: str, config: dict[str, Any] | None = None) -> Provider:
        if provider_id not in self._builders:
            raise KeyError(f"provider builder not registered: {provider_id}")
        return self._builders[provider_id](config)

    def available_provider_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._builders))

    def create_all(self, config_by_provider: dict[str, dict[str, Any]] | None = None) -> tuple[Provider, ...]:
        configs = config_by_provider or {}
        return tuple(
            self.create(provider_id, configs.get(provider_id))
            for provider_id in self.available_provider_ids()
        )
