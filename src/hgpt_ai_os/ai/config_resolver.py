from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path


logger = logging.getLogger(__name__)


FREE_DESKTOP_MODE = "free_desktop"
DISABLED_PROVIDERS = {"none", "disabled", "disable", "off", FREE_DESKTOP_MODE}
SUPPORTED_PROVIDERS = {"openai", *DISABLED_PROVIDERS}
CONFIG_KEYS = (
    "AI_PROVIDER",
    "OPENAI_API_KEY",
    "GEMINI_API_KEY",
    "ANTHROPIC_API_KEY",
    "OLLAMA_API_KEY",
)
PROVIDER_KEY_MAP = {
    "openai": "OPENAI_API_KEY",
}
GUI_CONFIG_ERROR_MESSAGE = (
    "AI Provider is not configured. Please set AI_PROVIDER and API key in "
    "Settings or config file."
)
@dataclass(frozen=True)
class AIConfig:
    provider: str
    values: dict[str, str] = field(default_factory=dict)
    source: str = "none"
    search_paths: tuple[str, ...] = ()

    def api_key_for_provider(self) -> str:
        key_name = PROVIDER_KEY_MAP.get(self.provider)
        if not key_name:
            return ""
        return self.values.get(key_name, "").strip()

    @property
    def free_desktop_mode(self) -> bool:
        return self.provider in DISABLED_PROVIDERS


@dataclass(frozen=True)
class AIConfigValidation:
    ok: bool
    message: str
    status: str
    config: AIConfig
    reason: str = ""
    missing_key: str = ""


def resolve_ai_config() -> AIConfig:
    from hgpt_ai_os.settings.config_manager import ConfigManager

    manager = ConfigManager()
    config = manager.load()
    values = {
        "AI_PROVIDER": config.get("provider", "").strip(),
        "OPENAI_API_KEY": config.get("openai_api_key", "").strip(),
        "GEMINI_API_KEY": config.get("gemini_api_key", "").strip(),
        "ANTHROPIC_API_KEY": config.get("anthropic_api_key", "").strip(),
        "OLLAMA_API_KEY": config.get("ollama_api_key", "").strip(),
    }
    return _resolved(str(manager.config_path), values, (manager.config_path,))


def validate_ai_provider_config() -> AIConfigValidation:
    config = resolve_ai_config()
    provider = config.provider

    if provider not in SUPPORTED_PROVIDERS:
        logger.error("Unsupported AI_PROVIDER selected: %s", provider)
        return AIConfigValidation(
            ok=False,
            message=GUI_CONFIG_ERROR_MESSAGE,
            status="Configuration Error",
            config=config,
            reason=f"Unsupported AI_PROVIDER '{provider}'.",
        )

    if provider in DISABLED_PROVIDERS:
        logger.info("AI_PROVIDER is disabled; using Free Desktop Mode.")
        return AIConfigValidation(
            ok=True,
            message="Free Desktop Mode enabled.",
            status="Free Desktop",
            config=config,
            reason="Free Desktop Mode",
        )

    required_key = PROVIDER_KEY_MAP[provider]
    if not config.api_key_for_provider():
        logger.info(
            "Missing API key for provider %s (%s); using Free Desktop Mode.",
            provider,
            required_key,
        )
        return AIConfigValidation(
            ok=True,
            message="Free Desktop Mode enabled.",
            status="Free Desktop",
            config=config,
            reason="Free Desktop Mode",
            missing_key=required_key,
        )

    logger.info(
        "AI provider configuration valid: source=%s provider=%s key_present=True",
        config.source,
        provider,
    )
    return AIConfigValidation(
        ok=True,
        message="AI provider configured.",
        status="Ready",
        config=config,
    )


def get_config_value(name: str, default: str = "") -> str:
    value = resolve_ai_config().values.get(name, "")
    return value.strip() if value else default


def is_free_desktop_mode() -> bool:
    validation = validate_ai_provider_config()
    return validation.ok and validation.reason == "Free Desktop Mode"


def _resolved(
    source: str,
    values: dict[str, str],
    search_paths: tuple[Path, ...],
) -> AIConfig:
    normalized = {key: (values.get(key, "") or "").strip() for key in CONFIG_KEYS}
    provider = normalized.get("AI_PROVIDER", "").lower() or "none"
    if provider == FREE_DESKTOP_MODE.upper().lower():
        provider = FREE_DESKTOP_MODE
    config = AIConfig(
        provider=provider,
        values=normalized,
        source=source,
        search_paths=tuple(str(path) for path in search_paths),
    )
    _apply_to_environment(config)
    logger.info("AI config source used: %s", source)
    logger.info("AI provider selected: %s", provider)
    return config


def _apply_to_environment(config: AIConfig) -> None:
    for key, value in config.values.items():
        if value and not os.getenv(key):
            os.environ[key] = value
    gemini_key = config.values.get("GEMINI_API_KEY", "")
    if gemini_key and not os.getenv("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = gemini_key
