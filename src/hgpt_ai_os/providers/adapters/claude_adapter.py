"""Claude provider adapter skeleton."""

from hgpt_ai_os.contracts.provider_contract import ProviderCapability
from hgpt_ai_os.providers.base_provider import BaseProviderAdapter, ProviderAdapterProfile


class ClaudeAdapter(BaseProviderAdapter):
    profile = ProviderAdapterProfile(
        provider_id="claude",
        display_name="Claude",
        default_model="claude-3-5-sonnet-latest",
        models=("claude-3-5-sonnet-latest", "claude-3-5-haiku-latest"),
        capabilities=(ProviderCapability.TEXT_GENERATION, ProviderCapability.STRUCTURED_OUTPUT),
        cost_rank=45,
        latency_rank=25,
        enterprise=True,
    )
