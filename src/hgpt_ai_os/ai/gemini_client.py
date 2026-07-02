from __future__ import annotations

import json
import logging
import os
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Union


logger = logging.getLogger(__name__)


DEFAULT_GEMINI_MODEL = "gemini-2.5-pro"
GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)


def _env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _use_live_gemini() -> bool:
    return _env_flag("USE_REAL_GEMINI") and bool(os.getenv("GOOGLE_API_KEY", "").strip())


@dataclass(frozen=True)
class AIResponse:
    provider: str
    model: str
    content: str
    usage: dict[str, Any] = field(default_factory=dict)
    finish_reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AIProviderError:
    provider: str
    model: str
    message: str
    error_type: str = "provider_error"
    retryable: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


class GeminiClient:
    """HTTP-only Gemini transport."""

    provider = "Gemini"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        timeout: int = 30,
        retries: int = 2,
        endpoint_template: str = GEMINI_ENDPOINT,
    ) -> None:
        self.api_key = (api_key or os.getenv("GOOGLE_API_KEY", "")).strip()
        self.model = (
            model
            or os.getenv("LUCID_GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip()
            or DEFAULT_GEMINI_MODEL
        )
        self.timeout = timeout
        self.retries = retries
        self.endpoint_template = endpoint_template

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> Union[AIResponse, AIProviderError]:
        if not self.api_key:
            return self._error(
                "GOOGLE_API_KEY is required for live Gemini mode.",
                error_type="configuration_error",
                retryable=False,
                metadata={"mode": "Live"},
            )

        payload = self._build_payload(system_prompt, user_prompt)
        body = json.dumps(payload).encode("utf-8")
        url = self._endpoint()

        for attempt in range(self.retries + 1):
            try:
                request = urllib.request.Request(
                    url,
                    data=body,
                    headers={
                        "Content-Type": "application/json",
                        "x-goog-api-key": self.api_key,
                    },
                    method="POST",
                )
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    response_body = response.read().decode("utf-8")
                data = json.loads(response_body)
                return self._parse_response(data)
            except urllib.error.HTTPError as exc:
                error_body = self._read_error_body(exc)
                retryable = exc.code in {408, 429, 500, 502, 503, 504}
                logger.warning(
                    "Gemini HTTP error on attempt %s/%s: %s",
                    attempt + 1,
                    self.retries + 1,
                    exc.code,
                )
                if retryable and attempt < self.retries:
                    self._backoff(attempt)
                    continue
                return self._error(
                    f"Gemini HTTP error {exc.code}.",
                    error_type="http_error",
                    retryable=retryable,
                    metadata={
                        "status_code": exc.code,
                        "body": error_body,
                        "attempts": attempt + 1,
                    },
                )
            except urllib.error.URLError as exc:
                if isinstance(exc.reason, TimeoutError | socket.timeout):
                    logger.warning(
                        "Gemini timeout on attempt %s/%s",
                        attempt + 1,
                        self.retries + 1,
                    )
                    if attempt < self.retries:
                        self._backoff(attempt)
                        continue
                    return self._error(
                        "Gemini request timed out.",
                        error_type="timeout",
                        retryable=True,
                        metadata={
                            "timeout": self.timeout,
                            "attempts": attempt + 1,
                            "reason": str(exc.reason),
                        },
                    )
                logger.warning(
                    "Gemini transport error on attempt %s/%s: %s",
                    attempt + 1,
                    self.retries + 1,
                    exc.reason,
                )
                if attempt < self.retries:
                    self._backoff(attempt)
                    continue
                return self._error(
                    "Gemini transport error.",
                    error_type="transport_error",
                    retryable=True,
                    metadata={
                        "reason": str(exc.reason),
                        "attempts": attempt + 1,
                    },
                )
            except (TimeoutError, socket.timeout) as exc:
                logger.warning(
                    "Gemini timeout on attempt %s/%s",
                    attempt + 1,
                    self.retries + 1,
                )
                if attempt < self.retries:
                    self._backoff(attempt)
                    continue
                return self._error(
                    "Gemini request timed out.",
                    error_type="timeout",
                    retryable=True,
                    metadata={
                        "timeout": self.timeout,
                        "attempts": attempt + 1,
                        "reason": str(exc),
                    },
                )
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                logger.exception("Failed to parse Gemini response")
                return self._error(
                    "Failed to parse Gemini response.",
                    error_type="parse_error",
                    retryable=False,
                    metadata={"reason": str(exc), "attempts": attempt + 1},
                )
            except Exception as exc:
                logger.exception("Unexpected Gemini provider error")
                return self._error(
                    "Unexpected Gemini provider error.",
                    error_type="unexpected_error",
                    retryable=False,
                    metadata={"reason": str(exc), "attempts": attempt + 1},
                )

        return self._error(
            "Gemini request failed.",
            error_type="provider_error",
            retryable=True,
            metadata={"attempts": self.retries + 1},
        )

    def _build_payload(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt or ""}],
                }
            ]
        }
        if system_prompt:
            payload["systemInstruction"] = {
                "parts": [{"text": system_prompt}],
            }
        return payload

    def _endpoint(self) -> str:
        model = urllib.parse.quote(self.model, safe="")
        return self.endpoint_template.format(model=model)

    def _parse_response(self, data: dict[str, Any]) -> AIResponse:
        candidates = data.get("candidates") or []
        candidate = candidates[0] if candidates else {}
        content = candidate.get("content") or {}
        parts = content.get("parts") or []
        text_parts = [
            part.get("text", "")
            for part in parts
            if isinstance(part, dict) and part.get("text")
        ]
        usage = data.get("usageMetadata") or {}
        finish_reason = candidate.get("finishReason")

        return AIResponse(
            provider=self.provider,
            model=self.model,
            content="".join(text_parts),
            usage={
                "prompt_tokens": usage.get("promptTokenCount", 0),
                "completion_tokens": usage.get("candidatesTokenCount", 0),
                "total_tokens": usage.get("totalTokenCount", 0),
                "raw": usage,
            },
            finish_reason=finish_reason,
            metadata={
                "mode": "Live",
                "candidate_count": len(candidates),
                "response_id": data.get("responseId"),
                "raw_finish_reason": finish_reason,
            },
        )

    def _error(
        self,
        message: str,
        error_type: str,
        retryable: bool,
        metadata: dict[str, Any] | None = None,
    ) -> AIProviderError:
        return AIProviderError(
            provider=self.provider,
            model=self.model,
            message=message,
            error_type=error_type,
            retryable=retryable,
            metadata=metadata or {},
        )

    def _backoff(self, attempt: int) -> None:
        time.sleep(2 ** attempt)

    def _read_error_body(self, exc: urllib.error.HTTPError) -> str:
        try:
            return exc.read().decode("utf-8")
        except Exception:
            return ""


class GeminiAI:
    """Backward-compatible facade for older imports."""

    def __init__(self) -> None:
        self.client = GeminiClient()

    def ask(self, prompt: str) -> str:
        if not _use_live_gemini():
            logger.info("GeminiAI running in mock mode")
            return prompt.strip() or "Mock Gemini response."

        response = self.client.generate("", prompt)
        if isinstance(response, AIProviderError):
            logger.error("Gemini request failed: %s", response.message)
            return ""
        return response.content
