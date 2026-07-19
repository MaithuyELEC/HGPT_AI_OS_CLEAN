from __future__ import annotations

import json
import socket
import ssl
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

import certifi

from hgpt_ai_os.ai.client import AnthropicProvider, OpenAIProvider
from hgpt_ai_os.ai.gemini_client import AIProviderError, GeminiClient
from hgpt_ai_os.settings.provider_registry import provider_info


@dataclass(frozen=True)
class ConnectionTestResult:
    ok: bool
    status: str
    message: str
    latency_ms: int | None = None
    reason: str = ""
    provider: str = ""
    model: str = ""


def test_provider(provider: str, api_key: str) -> ConnectionTestResult:
    provider_name = provider.strip().lower()
    info = provider_info(provider_name)
    clean_key = api_key.strip()
    if info.coming_soon:
        return ConnectionTestResult(
            ok=False,
            status="Connection Failed",
            message=f"{info.label} is coming soon",
            reason="This provider is routed but not enabled in Phase 1.",
            provider=info.label,
            model=info.default_model,
        )
    if not info.local and not clean_key:
        return ConnectionTestResult(
            ok=False,
            status="Connection Failed",
            message="Invalid API Key",
            reason="API key is empty.",
            provider=info.label,
            model=info.default_model,
        )
    if info.key_prefixes and not clean_key.startswith(info.key_prefixes):
        return ConnectionTestResult(
            ok=False,
            status="Connection Failed",
            message="Invalid API Key",
            reason=f"{info.label} API key format is not recognized.",
            provider=info.label,
            model=info.default_model,
        )

    started = time.perf_counter()
    try:
        if provider_name == "openai":
            return _test_openai(clean_key, started)
        elif provider_name == "gemini":
            response = GeminiClient(
                api_key=clean_key,
                timeout=20,
                retries=0,
            ).generate("", "Reply with OK.")
        elif provider_name == "anthropic":
            response = AnthropicProvider(
                api_key=clean_key,
                timeout=20,
            ).generate("", "Reply with OK.")
        else:
            return ConnectionTestResult(
                ok=False,
                status="Connection Failed",
                message="Invalid API Key",
                reason=f"Unsupported provider: {provider_name}",
                provider=info.label,
                model=info.default_model,
            )
    except Exception as exc:
        return ConnectionTestResult(
            ok=False,
            status="Connection Failed",
            message=_network_message(exc),
            reason="Network unavailable" if _is_network_error(exc) else "Connection failed",
            provider=info.label,
            model=info.default_model,
        )

    latency_ms = int((time.perf_counter() - started) * 1000)
    if isinstance(response, AIProviderError):
        message = _classify_error(response)
        return ConnectionTestResult(
            ok=False,
            status="Connection Failed",
            message=message,
            latency_ms=latency_ms,
            reason=response.message,
            provider=info.label,
            model=getattr(response, "model", info.default_model),
        )

    return ConnectionTestResult(
        ok=True,
        status="Ready",
        message="Connected",
        latency_ms=latency_ms,
        provider=info.label,
        model=getattr(response, "model", info.default_model),
    )


def _test_openai(api_key: str, started: float) -> ConnectionTestResult:
    model = OpenAIProvider(api_key=api_key, timeout=20).model
    request = urllib.request.Request(
        f"https://api.openai.com/v1/models/{model}",
        headers={"Authorization": f"Bearer {api_key}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(
            request,
            timeout=20,
            context=ssl.create_default_context(cafile=certifi.where()),
        ) as response:
            status_code = response.getcode()
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        return ConnectionTestResult(
            ok=False,
            status="Connection Failed",
            message=_classify_http_error(exc),
            latency_ms=int((time.perf_counter() - started) * 1000),
            reason=_read_error_body(exc) or f"HTTP {exc.code}",
            provider="OpenAI",
            model=model,
        )
    except (urllib.error.URLError, TimeoutError, socket.timeout, ssl.SSLError) as exc:
        return ConnectionTestResult(
            ok=False,
            status="Connection Failed",
            message=_network_message(exc),
            latency_ms=int((time.perf_counter() - started) * 1000),
            reason="Network unavailable",
            provider="OpenAI",
            model=model,
        )

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        data = {}
    detected_model = data.get("id") or model
    return ConnectionTestResult(
        ok=status_code == 200,
        status="Ready" if status_code == 200 else "Connection Failed",
        message="Connected" if status_code == 200 else "Connection failed",
        latency_ms=int((time.perf_counter() - started) * 1000),
        provider="OpenAI",
        model=detected_model,
    )


def _classify_error(error: AIProviderError) -> str:
    status_code = error.metadata.get("status_code")
    body = str(error.metadata.get("body", "")).lower()
    reason = str(error.metadata.get("reason", "")).lower()
    text = f"{error.message} {body} {reason}".lower()

    if status_code == 401 or "invalid api key" in text or "unauthorized" in text:
        return "Invalid API Key"
    if status_code == 403:
        return "No permission"
    if status_code == 429 or "quota" in text or "resource_exhausted" in text:
        return "Rate limited"
    if error.error_type in {"network_error", "timeout", "ssl_error", "transport_error"}:
        return "Network unavailable"
    if error.error_type == "configuration_error":
        return "Invalid API Key"
    return error.message or "Connection failed"


def _classify_http_error(exc: urllib.error.HTTPError) -> str:
    body = _read_error_body(exc).lower()
    if exc.code == 401 or "invalid api key" in body:
        return "Invalid API Key"
    if exc.code == 403:
        return "No permission"
    if exc.code == 404:
        return "No permission"
    if exc.code == 429:
        return "Rate limited"
    if exc.code in {408, 500, 502, 503, 504}:
        return "Network unavailable"
    return "Authentication failed"


def _read_error_body(exc: urllib.error.HTTPError) -> str:
    try:
        return exc.read().decode("utf-8")
    except Exception:
        return ""


def _is_network_error(exc: Exception) -> bool:
    return isinstance(exc, (urllib.error.URLError, TimeoutError, socket.timeout, ssl.SSLError))


def _network_message(exc: Exception) -> str:
    return "Network unavailable" if _is_network_error(exc) else "Connection failed"
