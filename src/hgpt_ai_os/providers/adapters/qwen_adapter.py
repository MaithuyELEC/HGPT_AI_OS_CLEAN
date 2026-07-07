"""Qwen provider adapter skeleton."""

from hgpt_ai_os.contracts.provider_contract import ProviderCapability
from hgpt_ai_os.providers.base_provider import BaseProviderAdapter, ProviderAdapterProfile


class QwenAdapter(BaseProviderAdapter):
    profile = ProviderAdapterProfile(
        provider_id="qwen",
        display_name="Qwen",
        default_model="qwen-plus",
        models=("qwen-plus", "qwen-turbo"),
        capabilities=(ProviderCapability.TEXT_GENERATION, ProviderCapability.STRUCTURED_OUTPUT),
        cost_rank=12,
        latency_rank=18,
        free=True,
    )
