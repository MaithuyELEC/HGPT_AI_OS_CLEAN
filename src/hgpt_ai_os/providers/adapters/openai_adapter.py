"""OpenAI provider adapter skeleton."""

from hgpt_ai_os.contracts.provider_contract import ProviderCapability
from hgpt_ai_os.providers.base_provider import BaseProviderAdapter, ProviderAdapterProfile


class OpenAIAdapter(BaseProviderAdapter):
    profile = ProviderAdapterProfile(
        provider_id="openai",
        display_name="OpenAI",
        default_model="gpt-4o-mini",
        models=("gpt-4o-mini", "gpt-4o"),
        capabilities=(
            ProviderCapability.TEXT_GENERATION,
            ProviderCapability.STRUCTURED_OUTPUT,
            ProviderCapability.TOOL_CALLING,
        ),
        cost_rank=40,
        latency_rank=15,
        enterprise=True,
    )
