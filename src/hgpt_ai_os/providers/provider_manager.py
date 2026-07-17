"""Production provider manager for real AI generation."""

from __future__ import annotations

from typing import Union

from hgpt_ai_os.ai.client import ProviderFactory
from hgpt_ai_os.ai.config_resolver import validate_ai_provider_config
from hgpt_ai_os.ai.gemini_client import AIProviderError, AIResponse


class ProviderManager:
    """Single manager boundary used by the engineering pipeline."""

    def generate_real_ai(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> Union[AIResponse, AIProviderError]:
        validation = validate_ai_provider_config()
        configured = validation.config.provider
        if validation.config.free_desktop_mode or not validation.ok:
            return AIProviderError(
                provider=configured or "Disabled",
                model="",
                message=validation.reason or "AI_PROVIDER_DISABLED",
                error_type="configuration_error",
                retryable=False,
                metadata={
                    "status": validation.status,
                    "source": validation.config.source,
                },
            )

        provider = ProviderFactory.create(configured)
        endpoint = getattr(provider, "endpoint", "")
        if not endpoint and hasattr(provider, "client"):
            endpoint = getattr(provider.client, "endpoint_template", "")
        print(f"Selected Provider = {getattr(provider, 'provider', configured.title())}")
        print(f"Selected Model = {getattr(provider, 'model', '')}")
        print("API Key Source = ConfigManager")
        print("Config File = config.json")
        print(f"Config Path = {validation.config.source}")
        print(f"HTTP Endpoint = {endpoint}")

        response = provider.generate(system_prompt, user_prompt)
        status_code = getattr(response, "metadata", {}).get("status_code")
        if status_code:
            print(f"HTTP = {status_code}")
        return response
