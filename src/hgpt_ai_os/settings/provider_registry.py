from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderInfo:
    key: str
    label: str
    model_env: str
    default_model: str
    key_url: str
    coming_soon: bool = False
    local: bool = False
    key_prefixes: tuple[str, ...] = ()
    instructions: tuple[str, ...] = ()


PROVIDERS: dict[str, ProviderInfo] = {
    "openai": ProviderInfo(
        key="openai",
        label="OpenAI",
        model_env="LUCID_OPENAI_MODEL",
        default_model="gpt-4o-mini",
        key_url="https://platform.openai.com/api-keys",
        key_prefixes=("sk-",),
        instructions=(
            "Dang nhap tai khoan OpenAI.",
            "Vao muc API Keys.",
            "Tao Secret Key moi.",
            "Copy API Key.",
            "Quay lai Lucid.",
            "Dan API Key.",
            "Nhan Test Connection.",
        ),
    ),
    "gemini": ProviderInfo(
        key="gemini",
        label="Google Gemini",
        model_env="LUCID_GEMINI_MODEL",
        default_model="gemini-2.5-pro",
        key_url="https://aistudio.google.com/app/apikey",
        coming_soon=True,
        instructions=(
            "Mo Google AI Studio.",
            "Tao API key cho project phu hop.",
            "Copy API key.",
            "Quay lai Lucid va dan vao o API Key.",
            "Nhan Test Connection.",
        ),
    ),
    "anthropic": ProviderInfo(
        key="anthropic",
        label="Claude",
        model_env="LUCID_ANTHROPIC_MODEL",
        default_model="claude-3-5-sonnet-latest",
        key_url="https://console.anthropic.com/settings/keys",
        coming_soon=True,
        key_prefixes=("sk-ant-",),
        instructions=(
            "Dang nhap Anthropic Console.",
            "Mo muc API Keys.",
            "Tao key moi.",
            "Copy API key.",
            "Quay lai Lucid va dan vao o API Key.",
            "Nhan Test Connection.",
        ),
    ),
    "ollama": ProviderInfo(
        key="ollama",
        label="Ollama",
        model_env="LUCID_OLLAMA_MODEL",
        default_model="llama3.1",
        key_url="https://ollama.com/download",
        coming_soon=True,
        local=True,
        instructions=(
            "Tai va cai dat Ollama.",
            "Cai model can dung tren may cuc bo.",
            "Khoi dong dich vu Ollama.",
            "Quay lai Lucid va nhan Test Connection.",
        ),
    ),
}


def provider_info(provider: str) -> ProviderInfo:
    return PROVIDERS.get(provider.strip().lower(), PROVIDERS["openai"])


def provider_label(provider: str) -> str:
    return provider_info(provider).label

