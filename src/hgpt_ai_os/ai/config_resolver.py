from __future__ import annotations

import json
import logging
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path


logger = logging.getLogger(__name__)


FREE_DESKTOP_MODE = "free_desktop"
DISABLED_PROVIDERS = {"none", "disabled", "disable", "off", FREE_DESKTOP_MODE}
SUPPORTED_PROVIDERS = {"openai", "gemini", "anthropic", *DISABLED_PROVIDERS}
CONFIG_KEYS = (
    "AI_PROVIDER",
    "OPENAI_API_KEY",
    "GEMINI_API_KEY",
    "ANTHROPIC_API_KEY",
)
PROVIDER_KEY_MAP = {
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
}
GUI_CONFIG_ERROR_MESSAGE = (
    "AI Provider is not configured. Please set AI_PROVIDER and API key in "
    "Settings or config file."
)
CONFIG_EXAMPLE = {
    "AI_PROVIDER": "gemini",
    "GEMINI_API_KEY": "",
    "OPENAI_API_KEY": "",
    "ANTHROPIC_API_KEY": "",
}


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
    _create_example_config_if_missing()

    env_values = _read_environment()
    if _has_config(env_values):
        return _resolved("environment variables", env_values, ())

    search_paths = tuple(_config_search_paths())
    for path in search_paths:
        logger.info("Checking AI config path: %s", path)
        if not path.exists():
            continue

        values = _read_config_file(path)
        if _has_config(values):
            return _resolved(str(path), values, search_paths)

    logger.info(
        "No AI provider config found. Checked: %s",
        ", ".join(str(path) for path in search_paths),
    )
    return AIConfig(
        provider="none",
        values={},
        source="none",
        search_paths=tuple(str(path) for path in search_paths),
    )


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


def _read_environment() -> dict[str, str]:
    values = {key: os.getenv(key, "").strip() for key in CONFIG_KEYS}
    google_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if google_key and not values["GEMINI_API_KEY"]:
        values["GEMINI_API_KEY"] = google_key
    return values


def _read_config_file(path: Path) -> dict[str, str]:
    if path.name == ".env":
        return _read_dotenv(path)

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Could not read AI config file %s: %s", path, exc)
        return {}

    if not isinstance(data, dict):
        logger.warning("AI config file ignored because it is not a JSON object: %s", path)
        return {}

    return {key: str(data.get(key, "") or "").strip() for key in CONFIG_KEYS}


def _read_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        logger.warning("Could not read AI .env file %s: %s", path, exc)
        return values

    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key not in CONFIG_KEYS and key != "GOOGLE_API_KEY":
            continue
        cleaned = value.strip().strip('"').strip("'")
        if key == "GOOGLE_API_KEY":
            key = "GEMINI_API_KEY"
        values[key] = cleaned

    return values


def _has_config(values: dict[str, str]) -> bool:
    return any((values.get(key, "") or "").strip() for key in CONFIG_KEYS)


def _apply_to_environment(config: AIConfig) -> None:
    for key, value in config.values.items():
        if value and not os.getenv(key):
            os.environ[key] = value
    gemini_key = config.values.get("GEMINI_API_KEY", "")
    if gemini_key and not os.getenv("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = gemini_key


def _config_search_paths() -> list[Path]:
    paths = [Path.cwd() / ".env"]

    if getattr(sys, "frozen", False):
        paths.append(Path(sys.executable).resolve().parent / ".env")
        if hasattr(sys, "_MEIPASS"):
            paths.append(Path(sys._MEIPASS) / ".env")

    appdata = os.getenv("APPDATA", "").strip()
    if appdata:
        paths.append(Path(appdata) / "LUCID" / "config.json")

    paths.append(_documents_config_dir() / "config.json")

    unique_paths: list[Path] = []
    seen = set()
    for path in paths:
        marker = str(path)
        if marker not in seen:
            seen.add(marker)
            unique_paths.append(path)
    return unique_paths


def _documents_config_dir() -> Path:
    userprofile = os.getenv("USERPROFILE", "").strip()
    if userprofile:
        return Path(userprofile) / "Documents" / "LUCID"
    return Path.home() / "Documents" / "LUCID"


def _create_example_config_if_missing() -> None:
    config_dir = _documents_config_dir()
    config_path = config_dir / "config.json"
    example_path = config_dir / "config.example.json"

    if config_path.exists() or example_path.exists():
        return

    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        example_path.write_text(
            json.dumps(CONFIG_EXAMPLE, indent=2) + "\n",
            encoding="utf-8",
        )
        logger.info("Created AI config example: %s", example_path)
    except OSError as exc:
        logger.warning("Could not create AI config example %s: %s", example_path, exc)
