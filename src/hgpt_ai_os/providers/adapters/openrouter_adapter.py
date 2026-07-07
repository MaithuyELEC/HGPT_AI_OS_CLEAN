"""OpenRouter provider adapter skeleton."""

from hgpt_ai_os.contracts.provider_contract import ProviderCapability
from hgpt_ai_os.providers.base_provider import BaseProviderAdapter, ProviderAdapterProfile


class OpenRouterAdapter(BaseProviderAdapter):
    profile = ProviderAdapterProfile(
        provider_id="openrouter",
        display_name="OpenRouter",
        default_model="auto",
        models=("auto",),
        capabilities=(ProviderCapability.TEXT_GENERATION, ProviderCapability.STRUCTURED_OUTPUT),
        cost_rank=30,
        latency_rank=30,
    )
