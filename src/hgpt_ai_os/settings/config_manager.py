from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CONFIG = {
    "provider": "openai",
    "openai_api_key": "",
    "gemini_api_key": "",
    "anthropic_api_key": "",
}
SUPPORTED_PROVIDERS = {"gemini", "openai", "anthropic", "none"}
PROVIDER_KEY_FIELD = {
    "gemini": "gemini_api_key",
    "openai": "openai_api_key",
    "anthropic": "anthropic_api_key",
}
ENV_KEY_MAP = {
    "provider": "AI_PROVIDER",
    "gemini_api_key": "GEMINI_API_KEY",
    "openai_api_key": "OPENAI_API_KEY",
    "anthropic_api_key": "ANTHROPIC_API_KEY",
}
DOTENV_KEY_MAP = {
    "AI_PROVIDER": "provider",
    "GEMINI_API_KEY": "gemini_api_key",
    "GOOGLE_API_KEY": "gemini_api_key",
    "OPENAI_API_KEY": "openai_api_key",
    "ANTHROPIC_API_KEY": "anthropic_api_key",
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

    @staticmethod
    def default_config_path() -> Path:
        userprofile = os.getenv("USERPROFILE", "").strip()
        if userprofile:
            return Path(userprofile) / "Documents" / "LUCID" / "config.json"
        return Path.home() / "Documents" / "LUCID" / "config.json"

    def load(self) -> dict[str, str]:
        if not self.config_path.exists():
            self.save(DEFAULT_CONFIG.copy())
            return self.config.copy()

        try:
            data = json.loads(self.config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}

        self.config = self._normalize(data if isinstance(data, dict) else {})
        if self._migrate_to_openai_source():
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
        self.config_path.write_text(
            json.dumps(self.config, indent=4) + "\n",
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

    def validate(self) -> ConfigValidation:
        self.load()
        provider = self.provider()
        if provider == "none":
            return ConfigValidation(
                ok=True,
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
        if not self.api_key(provider):
            return ConfigValidation(
                ok=True,
                message="Free Desktop Mode enabled.",
                status="Free Desktop",
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

    def _normalize(self, data: dict) -> dict[str, str]:
        return {
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
        }

    def _migrate_to_openai_source(self) -> bool:
        before = self.config.copy()
        dotenv_values = self._read_repo_dotenv()

        if not self.config.get("openai_api_key", "").strip():
            self.config["openai_api_key"] = dotenv_values.get("openai_api_key", "")

        if self.config.get("openai_api_key", "").strip():
            self.config["provider"] = "openai"

        return self.config != before

    def _read_repo_dotenv(self) -> dict[str, str]:
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

        gemini_key = self.config.get("gemini_api_key", "").strip()
        if gemini_key:
            os.environ["GOOGLE_API_KEY"] = gemini_key
