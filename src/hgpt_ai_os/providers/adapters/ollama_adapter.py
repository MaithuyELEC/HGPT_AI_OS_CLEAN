"""Ollama provider adapter skeleton."""

from hgpt_ai_os.contracts.provider_contract import ProviderCapability
from hgpt_ai_os.providers.base_provider import BaseProviderAdapter, ProviderAdapterProfile


class OllamaAdapter(BaseProviderAdapter):
    profile = ProviderAdapterProfile(
        provider_id="ollama",
        display_name="Ollama",
        default_model="llama3.1",
        models=("llama3.1", "qwen2.5"),
        capabilities=(ProviderCapability.TEXT_GENERATION,),
        cost_rank=0,
        latency_rank=10,
        offline=True,
        free=True,
        privacy_preserving=True,
    )
