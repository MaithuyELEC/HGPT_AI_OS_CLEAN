from __future__ import annotations

import time
from dataclasses import dataclass

from hgpt_ai_os.ai.client import AnthropicProvider, OpenAIProvider
from hgpt_ai_os.ai.gemini_client import AIProviderError, GeminiClient


@dataclass(frozen=True)
class ConnectionTestResult:
    ok: bool
    status: str
    message: str
    latency_ms: int | None = None
    reason: str = ""


def test_provider(provider: str, api_key: str) -> ConnectionTestResult:
    provider_name = provider.strip().lower()
    if not api_key.strip():
        return ConnectionTestResult(
            ok=False,
            status="Disconnected",
            message="Invalid API Key",
            reason="API key is empty.",
        )

    started = time.perf_counter()
    try:
        if provider_name == "gemini":
            response = GeminiClient(
                api_key=api_key,
                timeout=20,
                retries=0,
            ).generate("", "Reply with OK.")
        elif provider_name == "openai":
            response = OpenAIProvider(
                api_key=api_key,
                timeout=20,
            ).generate("", "Reply with OK.")
        elif provider_name == "anthropic":
            response = AnthropicProvider(
                api_key=api_key,
                timeout=20,
            ).generate("", "Reply with OK.")
        else:
            return ConnectionTestResult(
                ok=False,
                status="Disconnected",
                message="Invalid API Key",
                reason=f"Unsupported provider: {provider_name}",
            )
    except Exception as exc:
        return ConnectionTestResult(
            ok=False,
            status="Disconnected",
            message="No Internet",
            reason=str(exc),
        )

    latency_ms = int((time.perf_counter() - started) * 1000)
    if isinstance(response, AIProviderError):
        message = _classify_error(response)
        return ConnectionTestResult(
            ok=False,
            status="Disconnected",
            message=message,
            latency_ms=latency_ms,
            reason=response.message,
        )

    return ConnectionTestResult(
        ok=True,
        status="Connected",
        message="Connection OK",
        latency_ms=latency_ms,
    )


def _classify_error(error: AIProviderError) -> str:
    status_code = error.metadata.get("status_code")
    body = str(error.metadata.get("body", "")).lower()
    reason = str(error.metadata.get("reason", "")).lower()
    text = f"{error.message} {body} {reason}".lower()

    if status_code in {401, 403} or "invalid api key" in text or "unauthorized" in text:
        return "Invalid API Key"
    if status_code == 429 or "quota" in text or "resource_exhausted" in text:
        return "Quota exceeded"
    if error.error_type in {"network_error", "timeout", "ssl_error", "transport_error"}:
        return "No Internet"
    if error.error_type == "configuration_error":
        return "Invalid API Key"
    return error.message or "Connection failed"
