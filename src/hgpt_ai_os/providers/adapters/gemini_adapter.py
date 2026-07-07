"""Gemini provider adapter skeleton."""

from hgpt_ai_os.contracts.provider_contract import ProviderCapability
from hgpt_ai_os.providers.base_provider import BaseProviderAdapter, ProviderAdapterProfile


class GeminiAdapter(BaseProviderAdapter):
    profile = ProviderAdapterProfile(
        provider_id="gemini",
        display_name="Gemini",
        default_model="gemini-2.5-pro",
        models=("gemini-2.5-pro", "gemini-2.5-flash"),
        capabilities=(ProviderCapability.TEXT_GENERATION, ProviderCapability.STRUCTURED_OUTPUT),
        cost_rank=20,
        latency_rank=20,
        free=True,
    )
