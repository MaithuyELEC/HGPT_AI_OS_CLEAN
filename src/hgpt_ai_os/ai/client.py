from __future__ import annotations

import json
import logging
import os
import socket
import ssl
import urllib.error
import urllib.request
from typing import Union

import certifi

from hgpt_ai_os.ai.config_resolver import (
    get_config_value,
    resolve_ai_config,
    validate_ai_provider_config,
)
from hgpt_ai_os.ai.gemini_client import (
    AIProviderError,
    AIResponse,
    GeminiClient,
)


logger = logging.getLogger(__name__)


DEFAULT_GEMINI_MODEL = "gemini-2.5-pro"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
DEFAULT_ANTHROPIC_MODEL = "claude-3-5-sonnet-latest"
DEFAULT_OLLAMA_MODEL = "llama3.1"
OPENAI_ENDPOINT = "https://api.openai.com/v1/chat/completions"
ANTHROPIC_ENDPOINT = "https://api.anthropic.com/v1/messages"
OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
PROVIDER_UNAVAILABLE_MESSAGE = (
    "AI provider is not available. Please check API key and provider "
    "configuration."
)
ALL_PROVIDERS_FAILED_MESSAGE = (
    "AI providers are unavailable. Please check Gemini, OpenAI, Ollama, "
    "network, SSL, and provider configuration, then try again."
)


def _env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def gemini_model() -> str:
    return (
        os.getenv("LUCID_GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip()
        or DEFAULT_GEMINI_MODEL
    )


def openai_model() -> str:
    return (
        os.getenv("LUCID_OPENAI_MODEL", DEFAULT_OPENAI_MODEL).strip()
        or DEFAULT_OPENAI_MODEL
    )


def anthropic_model() -> str:
    return (
        os.getenv("LUCID_ANTHROPIC_MODEL", DEFAULT_ANTHROPIC_MODEL).strip()
        or DEFAULT_ANTHROPIC_MODEL
    )


def ollama_model() -> str:
    return (
        os.getenv("LUCID_OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL).strip()
        or DEFAULT_OLLAMA_MODEL
    )


def gemini_api_key() -> str:
    return (
        get_config_value("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY", "").strip()
        or os.getenv("GEMINI_API_KEY", "").strip()
    )


def openai_api_key() -> str:
    return get_config_value("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY", "").strip()


def anthropic_api_key() -> str:
    return (
        get_config_value("ANTHROPIC_API_KEY")
        or os.getenv("ANTHROPIC_API_KEY", "").strip()
    )


def use_live_gemini() -> bool:
    return bool(gemini_api_key())


def provider_status() -> dict[str, str]:
    validation = validate_ai_provider_config()
    config = validation.config
    return {
        "ai_provider": "PASS" if validation.ok else "FAIL",
        "provider": config.provider,
        "mode": "Live" if validation.ok else validation.status,
        "source": config.source,
        "gemini": "Configured" if gemini_api_key() else "Unavailable",
        "openai": "Configured" if openai_api_key() else "Unavailable",
        "anthropic": "Configured" if anthropic_api_key() else "Unavailable",
        "ollama": "Disabled",
        "model": _selected_model(config.provider),
    }


def _selected_model(provider: str) -> str:
    if provider == "gemini":
        return gemini_model()
    if provider == "anthropic":
        return anthropic_model()
    return openai_model()


class GeminiProvider:
    """Provider boundary for Gemini with mock mode preserved by default."""

    provider = "Gemini"

    def __init__(self, client: GeminiClient | None = None) -> None:
        self.model = gemini_model()
        self.mode = "Live" if use_live_gemini() else "Mock"
        self.client = client or GeminiClient(
            api_key=gemini_api_key(),
            model=self.model,
        )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> Union[AIResponse, AIProviderError]:
        if self.mode != "Live":
            logger.error(
                "Gemini provider unavailable: api_key_present=%s",
                bool(gemini_api_key()),
            )
            return AIProviderError(
                provider=self.provider,
                model=self.model,
                message=PROVIDER_UNAVAILABLE_MESSAGE,
                error_type="configuration_error",
                retryable=False,
                metadata={
                    "mode": self.mode,
                    "api_key_present": bool(gemini_api_key()),
                },
            )

        logger.info("Generating content with Gemini model %s", self.model)
        response = self.client.generate(system_prompt, user_prompt)
        if isinstance(response, AIProviderError):
            logger.error(
                "Gemini provider failed: type=%s retryable=%s message=%s "
                "metadata=%s",
                response.error_type,
                response.retryable,
                response.message,
                response.metadata,
            )
        return response

    def ask(self, prompt: str) -> str:
        response = self.generate("", prompt)
        if isinstance(response, AIProviderError):
            logger.error("Gemini provider failed: %s", response.message)
            return ""
        return response.content

    def _mock_response(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> AIResponse:
        logger.info("Gemini provider running in mock mode")
        content = user_prompt.strip() or system_prompt.strip()
        if not content:
            content = "Mock Gemini response."
        return AIResponse(
            provider=self.provider,
            model=self.model,
            content=content,
            usage={
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
            finish_reason="mock",
            metadata={
                "mode": "Mock",
                "mock": True,
            },
        )


class OpenAIProvider:
    """OpenAI chat-completions provider used by AIManager failover."""

    provider = "OpenAI"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        endpoint: str = OPENAI_ENDPOINT,
        timeout: int = 60,
    ) -> None:
        self.api_key = (api_key or openai_api_key()).strip()
        self.model = model or openai_model()
        self.endpoint = endpoint
        self.timeout = timeout
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> Union[AIResponse, AIProviderError]:
        if not self.api_key:
            return self._error(
                PROVIDER_UNAVAILABLE_MESSAGE,
                error_type="configuration_error",
                retryable=False,
                metadata={"api_key_present": False},
            )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt or ""},
                {"role": "user", "content": user_prompt or ""},
            ],
        }
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.endpoint,
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout,
                context=self.ssl_context,
            ) as response:
                response_body = response.read().decode("utf-8")
            data = json.loads(response_body)
            return self._parse_response(data)
        except urllib.error.HTTPError as exc:
            return self._error(
                f"OpenAI HTTP error {exc.code}.",
                error_type="http_error",
                retryable=exc.code in {408, 409, 429, 500, 502, 503, 504},
                metadata={
                    "status_code": exc.code,
                    "body": self._read_error_body(exc),
                },
            )
        except urllib.error.URLError as exc:
            reason = exc.reason
            if isinstance(reason, ssl.SSLError):
                error_type = "ssl_error"
            elif isinstance(reason, TimeoutError | socket.timeout):
                error_type = "timeout"
            else:
                error_type = "network_error"
            return self._error(
                "OpenAI network error.",
                error_type=error_type,
                retryable=True,
                metadata={"reason": str(reason)},
            )
        except (TimeoutError, socket.timeout) as exc:
            return self._error(
                "OpenAI request timed out.",
                error_type="timeout",
                retryable=True,
                metadata={"reason": str(exc)},
            )
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            return self._error(
                "Failed to parse OpenAI response.",
                error_type="parse_error",
                retryable=False,
                metadata={"reason": str(exc)},
            )
        except Exception as exc:
            logger.exception("Unexpected OpenAI provider error")
            return self._error(
                "Unexpected OpenAI provider error.",
                error_type="unexpected_error",
                retryable=False,
                metadata={"reason": str(exc)},
            )

    def ask(self, prompt: str) -> str:
        response = self.generate("", prompt)
        if isinstance(response, AIProviderError):
            logger.error("OpenAI provider failed: %s", response.message)
            return ""
        return response.content

    def _parse_response(self, data: dict) -> AIResponse:
        choices = data.get("choices") or []
        choice = choices[0] if choices else {}
        message = choice.get("message") or {}
        usage = data.get("usage") or {}

        return AIResponse(
            provider=self.provider,
            model=data.get("model") or self.model,
            content=message.get("content", ""),
            usage={
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
                "raw": usage,
            },
            finish_reason=choice.get("finish_reason"),
            metadata={
                "mode": "Live",
                "response_id": data.get("id"),
            },
        )

    def _error(
        self,
        message: str,
        error_type: str,
        retryable: bool,
        metadata: dict | None = None,
    ) -> AIProviderError:
        return AIProviderError(
            provider=self.provider,
            model=self.model,
            message=message,
            error_type=error_type,
            retryable=retryable,
            metadata=metadata or {},
        )

    def _read_error_body(self, exc: urllib.error.HTTPError) -> str:
        try:
            return exc.read().decode("utf-8")
        except Exception:
            return ""


class AnthropicProvider:
    """Anthropic messages provider used when AI_PROVIDER=anthropic."""

    provider = "Anthropic"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        endpoint: str = ANTHROPIC_ENDPOINT,
        timeout: int = 60,
    ) -> None:
        self.api_key = (api_key or anthropic_api_key()).strip()
        self.model = model or anthropic_model()
        self.endpoint = endpoint
        self.timeout = timeout
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> Union[AIResponse, AIProviderError]:
        if not self.api_key:
            return self._error(
                PROVIDER_UNAVAILABLE_MESSAGE,
                error_type="configuration_error",
                retryable=False,
                metadata={"api_key_present": False},
            )

        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "system": system_prompt or "",
            "messages": [
                {"role": "user", "content": user_prompt or ""},
            ],
        }
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.endpoint,
            data=body,
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout,
                context=self.ssl_context,
            ) as response:
                response_body = response.read().decode("utf-8")
            data = json.loads(response_body)
            return self._parse_response(data)
        except urllib.error.HTTPError as exc:
            return self._error(
                f"Anthropic HTTP error {exc.code}.",
                error_type="http_error",
                retryable=exc.code in {408, 409, 429, 500, 502, 503, 504},
                metadata={
                    "status_code": exc.code,
                    "body": self._read_error_body(exc),
                },
            )
        except urllib.error.URLError as exc:
            reason = exc.reason
            if isinstance(reason, ssl.SSLError):
                error_type = "ssl_error"
            elif isinstance(reason, TimeoutError | socket.timeout):
                error_type = "timeout"
            else:
                error_type = "network_error"
            return self._error(
                "Anthropic network error.",
                error_type=error_type,
                retryable=True,
                metadata={"reason": str(reason)},
            )
        except (TimeoutError, socket.timeout) as exc:
            return self._error(
                "Anthropic request timed out.",
                error_type="timeout",
                retryable=True,
                metadata={"reason": str(exc)},
            )
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            return self._error(
                "Failed to parse Anthropic response.",
                error_type="parse_error",
                retryable=False,
                metadata={"reason": str(exc)},
            )
        except Exception as exc:
            logger.exception("Unexpected Anthropic provider error")
            return self._error(
                "Unexpected Anthropic provider error.",
                error_type="unexpected_error",
                retryable=False,
                metadata={"reason": str(exc)},
            )

    def ask(self, prompt: str) -> str:
        response = self.generate("", prompt)
        if isinstance(response, AIProviderError):
            logger.error("Anthropic provider failed: %s", response.message)
            return ""
        return response.content

    def _parse_response(self, data: dict) -> AIResponse:
        content_blocks = data.get("content") or []
        text_parts = [
            block.get("text", "")
            for block in content_blocks
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        usage = data.get("usage") or {}

        return AIResponse(
            provider=self.provider,
            model=data.get("model") or self.model,
            content="\n".join(part for part in text_parts if part),
            usage={
                "prompt_tokens": usage.get("input_tokens", 0),
                "completion_tokens": usage.get("output_tokens", 0),
                "total_tokens": (
                    usage.get("input_tokens", 0)
                    + usage.get("output_tokens", 0)
                ),
                "raw": usage,
            },
            finish_reason=data.get("stop_reason"),
            metadata={
                "mode": "Live",
                "response_id": data.get("id"),
            },
        )

    def _error(
        self,
        message: str,
        error_type: str,
        retryable: bool,
        metadata: dict | None = None,
    ) -> AIProviderError:
        return AIProviderError(
            provider=self.provider,
            model=self.model,
            message=message,
            error_type=error_type,
            retryable=retryable,
            metadata=metadata or {},
        )

    def _read_error_body(self, exc: urllib.error.HTTPError) -> str:
        try:
            return exc.read().decode("utf-8")
        except Exception:
            return ""


class OllamaProvider:
    """Local Ollama provider used as the final AIManager fallback."""

    provider = "Ollama"

    def __init__(
        self,
        model: str | None = None,
        endpoint: str | None = None,
        timeout: int = 120,
    ) -> None:
        self.model = model or ollama_model()
        self.endpoint = endpoint or os.getenv(
            "LUCID_OLLAMA_ENDPOINT",
            OLLAMA_ENDPOINT,
        )
        self.timeout = timeout

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> Union[AIResponse, AIProviderError]:
        prompt = user_prompt or ""
        if system_prompt:
            prompt = f"{system_prompt}\n\n{prompt}"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.endpoint,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout,
            ) as response:
                response_body = response.read().decode("utf-8")
            data = json.loads(response_body)
            return AIResponse(
                provider=self.provider,
                model=data.get("model") or self.model,
                content=data.get("response", ""),
                usage={
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": (
                        data.get("prompt_eval_count", 0)
                        + data.get("eval_count", 0)
                    ),
                    "raw": data,
                },
                finish_reason="stop" if data.get("done") else None,
                metadata={"mode": "Local"},
            )
        except urllib.error.HTTPError as exc:
            return self._error(
                f"Ollama HTTP error {exc.code}.",
                error_type="http_error",
                retryable=exc.code in {408, 429, 500, 502, 503, 504},
                metadata={
                    "status_code": exc.code,
                    "body": self._read_error_body(exc),
                },
            )
        except urllib.error.URLError as exc:
            reason = exc.reason
            if isinstance(reason, TimeoutError | socket.timeout):
                error_type = "timeout"
            else:
                error_type = "network_error"
            return self._error(
                "Ollama network error.",
                error_type=error_type,
                retryable=True,
                metadata={"reason": str(reason)},
            )
        except (TimeoutError, socket.timeout) as exc:
            return self._error(
                "Ollama request timed out.",
                error_type="timeout",
                retryable=True,
                metadata={"reason": str(exc)},
            )
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            return self._error(
                "Failed to parse Ollama response.",
                error_type="parse_error",
                retryable=False,
                metadata={"reason": str(exc)},
            )
        except Exception as exc:
            logger.exception("Unexpected Ollama provider error")
            return self._error(
                "Unexpected Ollama provider error.",
                error_type="unexpected_error",
                retryable=False,
                metadata={"reason": str(exc)},
            )

    def ask(self, prompt: str) -> str:
        response = self.generate("", prompt)
        if isinstance(response, AIProviderError):
            logger.error("Ollama provider failed: %s", response.message)
            return ""
        return response.content

    def _error(
        self,
        message: str,
        error_type: str,
        retryable: bool,
        metadata: dict | None = None,
    ) -> AIProviderError:
        return AIProviderError(
            provider=self.provider,
            model=self.model,
            message=message,
            error_type=error_type,
            retryable=retryable,
            metadata=metadata or {},
        )

    def _read_error_body(self, exc: urllib.error.HTTPError) -> str:
        try:
            return exc.read().decode("utf-8")
        except Exception:
            return ""


class AIManager:
    """Selects AI providers and owns failover policy."""

    provider = "AIManager"

    def __init__(self, providers: list | None = None) -> None:
        self.providers = providers or [
            GeminiProvider(),
            OpenAIProvider(),
            OllamaProvider(),
        ]

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> Union[AIResponse, AIProviderError]:
        errors: list[AIProviderError] = []

        for provider in self.providers:
            response = provider.generate(system_prompt, user_prompt)
            if not isinstance(response, AIProviderError):
                if errors:
                    response.metadata["failover_from"] = [
                        error.provider for error in errors
                    ]
                return response

            errors.append(response)
            logger.warning(
                "%s failed: type=%s retryable=%s metadata=%s",
                response.provider,
                response.error_type,
                response.retryable,
                response.metadata,
            )

            if (
                response.provider == "Gemini"
                and not self._should_retry_after_gemini(response)
            ):
                break

        return AIProviderError(
            provider=self.provider,
            model=" > ".join(provider.model for provider in self.providers),
            message=ALL_PROVIDERS_FAILED_MESSAGE,
            error_type="all_providers_failed",
            retryable=True,
            metadata={
                "providers": [
                    {
                        "provider": error.provider,
                        "model": error.model,
                        "error_type": error.error_type,
                        "message": error.message,
                        "metadata": error.metadata,
                    }
                    for error in errors
                ]
            },
        )

    def ask(self, prompt: str) -> str:
        response = self.generate("", prompt)
        if isinstance(response, AIProviderError):
            logger.error("AI manager failed: %s", response.message)
            return ""
        return response.content

    def _should_retry_after_gemini(self, error: AIProviderError) -> bool:
        status_code = error.metadata.get("status_code")
        if status_code in {401, 403, 429}:
            return True
        return error.error_type in {
            "configuration_error",
            "timeout",
            "ssl_error",
            "transport_error",
            "network_error",
            "http_error",
        }


class LucidAI:
    """Backward-compatible AI facade."""

    def __init__(self, provider=None) -> None:
        configured_provider = resolve_ai_config().provider
        self.provider = provider or ProviderFactory.create(configured_provider)

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> Union[AIResponse, AIProviderError]:
        return self.provider.generate(system_prompt, user_prompt)

    def ask(self, prompt: str) -> str:
        return self.provider.ask(prompt)


class ProviderFactory:
    """Backward-compatible provider factory."""

    @staticmethod
    def create(provider: str = "openai"):
        provider_name = provider.lower()
        if provider_name in {"openai"}:
            return OpenAIProvider()
        if provider_name == "gemini":
            return GeminiProvider()
        if provider_name == "anthropic":
            return AnthropicProvider()
        if provider_name == "ollama":
            return OllamaProvider()
        if provider_name in {"manager", "ai", "lucid"}:
            return AIManager()
        logger.warning("Unsupported provider requested: %s", provider)
        return OpenAIProvider()
