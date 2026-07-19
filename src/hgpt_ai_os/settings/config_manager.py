from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from hgpt_ai_os.settings.provider_registry import PROVIDERS, provider_info
from hgpt_ai_os.settings.secure_store import SecureSecretStore

DEFAULT_CONFIG = {
    "provider": "openai",
    "openai_api_key": "",
    "gemini_api_key": "",
    "anthropic_api_key": "",
}
SUPPORTED_PROVIDERS = {"gemini", "openai", "anthropic", "ollama", "none", "free_desktop", "disabled"}
PROVIDER_KEY_FIELD = {
    "gemini": "gemini_api_key",
    "openai": "openai_api_key",
    "anthropic": "anthropic_api_key",
    "ollama": "ollama_api_key",
}
ENV_KEY_MAP = {
    "provider": "AI_PROVIDER",
    "gemini_api_key": "GEMINI_API_KEY",
    "openai_api_key": "OPENAI_API_KEY",
    "anthropic_api_key": "ANTHROPIC_API_KEY",
    "ollama_api_key": "OLLAMA_API_KEY",
}
DOTENV_KEY_MAP = {
    "AI_PROVIDER": "provider",
    "GEMINI_API_KEY": "gemini_api_key",
    "GOOGLE_API_KEY": "gemini_api_key",
    "OPENAI_API_KEY": "openai_api_key",
    "ANTHROPIC_API_KEY": "anthropic_api_key",
    "OLLAMA_API_KEY": "ollama_api_key",
}


@dataclass(frozen=True)
class ConfigValidation:
    ok: bool
    message: str
    status: str
    provider: str
    reason: str = ""


class ConfigManager:
    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = config_path or self.default_config_path()
        self.config: dict[str, str] = DEFAULT_CONFIG.copy()
        self.secrets = SecureSecretStore(self.config_path.parent)
        self._loaded_legacy_secret = False

    @staticmethod
    def default_config_path() -> Path:
        userprofile = os.getenv("USERPROFILE", "").strip()
        if userprofile:
            return Path(userprofile) / "Documents" / "LUCID" / "config.json"
        return Path.home() / "Documents" / "LUCID" / "config.json"

    def load(self) -> dict[str, str]:
        self._loaded_legacy_secret = False
        if not self.config_path.exists():
            self.save(DEFAULT_CONFIG.copy())
            return self.config.copy()

        try:
            data = json.loads(self.config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}

        self.config = self._normalize(data if isinstance(data, dict) else {})
        if self._migrate_to_openai_source() or self._loaded_legacy_secret:
            self._write_config()
        self._apply_environment()
        return self.config.copy()

    def save(self, config: dict[str, str] | None = None) -> dict[str, str]:
        self.config = self._normalize(config or self.config)
        self._migrate_to_openai_source()
        self._write_config()
        self._apply_environment()
        return self.config.copy()

    def _write_config(self) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        public_config = self._public_config(self.config)
        self.config_path.write_text(
            json.dumps(public_config, indent=4) + "\n",
            encoding="utf-8",
        )

    def exists(self) -> bool:
        return self.config_path.exists()

    def provider(self) -> str:
        return self.config.get("provider", "openai").strip().lower() or "openai"

    def api_key(self, provider: str | None = None) -> str:
        provider_name = (provider or self.provider()).strip().lower()
        key_field = PROVIDER_KEY_FIELD.get(provider_name, "")
        if not key_field:
            return ""
        return self.config.get(key_field, "").strip()

    def is_configured(self) -> bool:
        provider = self.provider()
        if provider in {"none", "disabled", "free_desktop"}:
            return False
        if provider_info(provider).local:
            return True
        return bool(self.api_key(provider))

    def masked_api_key(self, provider: str | None = None) -> str:
        key = self.api_key(provider)
        if not key:
            return "Not configured"
        if len(key) <= 8:
            return "••••"
        return f"{key[:4]}••••{key[-4:]}"

    def remove_api_key(self, provider: str | None = None) -> None:
        provider_name = (provider or self.provider()).strip().lower()
        self.secrets.delete(provider_name)
        field = PROVIDER_KEY_FIELD.get(provider_name)
        if field:
            self.config[field] = ""
        self._write_config()
        self._apply_environment()

    def mark_successful_test(self, provider: str, model: str) -> str:
        provider_name = (provider or self.provider()).strip().lower()
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.config[f"{provider_name}_last_successful_test"] = f"{stamp} - {model}"
        self._write_config()
        return self.config[f"{provider_name}_last_successful_test"]

    def validate(self) -> ConfigValidation:
        self.load()
        provider = self.provider()
        if provider in {"none", "disabled", "free_desktop"}:
            return ConfigValidation(
                ok=False,
                message="Free Desktop Mode enabled.",
                status="Free Desktop",
                provider="none",
                reason="AI Provider disabled.",
            )
        if provider not in SUPPORTED_PROVIDERS:
            return ConfigValidation(
                ok=False,
                message="AI is not configured.",
                status="Configuration Error",
                provider=provider,
                reason=f"Unsupported provider: {provider}",
            )
        if provider_info(provider).local:
            return ConfigValidation(
                ok=False,
                message=f"{provider_info(provider).label} is coming soon.",
                status="Coming Soon",
                provider=provider,
                reason="Provider is not enabled in this release.",
            )
        if provider_info(provider).coming_soon:
            return ConfigValidation(
                ok=False,
                message=f"{provider_info(provider).label} is coming soon.",
                status="Coming Soon",
                provider=provider,
                reason="Provider is not enabled in this release.",
            )
        if not self.api_key(provider):
            return ConfigValidation(
                ok=False,
                message="AI Provider is not configured.",
                status="Not Configured",
                provider="none",
                reason=f"Missing API key for {provider.title()}.",
            )
        return ConfigValidation(
            ok=True,
            message="AI provider configured.",
            status="Connected",
            provider=provider,
        )

    def test_connection(self) -> ConnectionTestResult:
        from hgpt_ai_os.settings.provider_test import ConnectionTestResult, test_provider

        self.load()
        return test_provider(self.provider(), self.api_key())

    def test_connection_for(self, provider: str, api_key: str) -> ConnectionTestResult:
        from hgpt_ai_os.settings.provider_test import ConnectionTestResult, test_provider

        return test_provider(provider, api_key)

    def _normalize(self, data: dict) -> dict[str, str]:
        normalized = {
            "provider": str(
                data.get("provider") or data.get("AI_PROVIDER") or "openai"
            )
            .strip()
            .lower()
            or "openai",
            "gemini_api_key": str(
                data.get("gemini_api_key")
                or data.get("GEMINI_API_KEY")
                or data.get("GOOGLE_API_KEY")
                or ""
            ).strip(),
            "openai_api_key": str(
                data.get("openai_api_key") or data.get("OPENAI_API_KEY") or ""
            ).strip(),
            "anthropic_api_key": str(
                data.get("anthropic_api_key") or data.get("ANTHROPIC_API_KEY") or ""
            ).strip(),
            "ollama_api_key": str(
                data.get("ollama_api_key") or data.get("OLLAMA_API_KEY") or ""
            ).strip(),
        }
        for provider in PROVIDER_KEY_FIELD:
            key = f"{provider}_last_successful_test"
            if key in data:
                normalized[key] = str(data.get(key, "")).strip()
        if normalized["provider"] not in SUPPORTED_PROVIDERS:
            return normalized
        for provider, field in PROVIDER_KEY_FIELD.items():
            legacy_key = normalized.get(field, "").strip()
            if legacy_key:
                self.secrets.set(provider, legacy_key)
                self._loaded_legacy_secret = True
            stored = self.secrets.get(provider)
            if stored:
                normalized[field] = stored
        return normalized

    def _public_config(self, config: dict[str, str]) -> dict[str, str]:
        public_config = DEFAULT_CONFIG.copy()
        public_config["provider"] = config.get("provider", "openai")
        for field in DEFAULT_CONFIG:
            if field != "provider":
                public_config[field] = ""
        for provider in PROVIDER_KEY_FIELD:
            key = f"{provider}_last_successful_test"
            if config.get(key):
                public_config[key] = config[key]
        return public_config

    def _migrate_to_openai_source(self) -> bool:
        before = self.config.copy()
        dotenv_values = self._read_repo_dotenv()

        if not self.config.get("openai_api_key", "").strip():
            self.config["openai_api_key"] = dotenv_values.get("openai_api_key", "")
            if self.config["openai_api_key"].strip():
                self.secrets.set("openai", self.config["openai_api_key"])

        if self.config.get("openai_api_key", "").strip():
            self.config["provider"] = "openai"

        return self.config != before

    def _read_repo_dotenv(self) -> dict[str, str]:
        if os.getenv("LUCID_IMPORT_REPO_DOTENV", "").strip().lower() not in {"1", "true", "yes"}:
            return {}
        env_path = Path(__file__).resolve().parents[3] / ".env"
        if not env_path.exists():
            return {}

        values: dict[str, str] = {}
        try:
            lines = env_path.read_text(encoding="utf-8").splitlines()
        except OSError:
            return values

        for raw_line in lines:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            field = DOTENV_KEY_MAP.get(key.strip())
            if not field:
                continue
            if field == "provider":
                continue
            values.setdefault(field, value.strip().strip('"').strip("'"))
        return values

    def _apply_environment(self) -> None:
        provider = self.provider()
        os.environ["AI_PROVIDER"] = provider

        for config_key, env_key in ENV_KEY_MAP.items():
            if config_key == "provider":
                continue
            value = self.config.get(config_key, "").strip()
            if value:
                os.environ[env_key] = value
            else:
                os.environ.pop(env_key, None)

        gemini_key = self.config.get("gemini_api_key", "").strip()
        if gemini_key:
            os.environ["GOOGLE_API_KEY"] = gemini_key
