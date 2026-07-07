"""DeepSeek provider adapter skeleton."""

from hgpt_ai_os.contracts.provider_contract import ProviderCapability
from hgpt_ai_os.providers.base_provider import BaseProviderAdapter, ProviderAdapterProfile


class DeepSeekAdapter(BaseProviderAdapter):
    profile = ProviderAdapterProfile(
        provider_id="deepseek",
        display_name="DeepSeek",
        default_model="deepseek-chat",
        models=("deepseek-chat", "deepseek-reasoner"),
        capabilities=(ProviderCapability.TEXT_GENERATION, ProviderCapability.STRUCTURED_OUTPUT),
        cost_rank=10,
        latency_rank=35,
        free=True,
    )
