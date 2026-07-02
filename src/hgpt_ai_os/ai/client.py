from __future__ import annotations

import logging
import os
from typing import Union

from hgpt_ai_os.ai.gemini_client import AIProviderError, AIResponse, GeminiClient


logger = logging.getLogger(__name__)


DEFAULT_GEMINI_MODEL = "gemini-2.5-pro"


def _env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def gemini_model() -> str:
    return os.getenv("LUCID_GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip() or DEFAULT_GEMINI_MODEL


def use_live_gemini() -> bool:
    return _env_flag("USE_REAL_GEMINI") and bool(os.getenv("GOOGLE_API_KEY", "").strip())


def provider_status() -> dict[str, str]:
    return {
        "ai_provider": "PASS",
        "provider": "Gemini",
        "mode": "Live" if use_live_gemini() else "Mock",
        "model": gemini_model(),
    }


class GeminiProvider:
    """Provider boundary for Gemini with mock mode preserved by default."""

    provider = "Gemini"

    def __init__(self, client: GeminiClient | None = None) -> None:
        self.model = gemini_model()
        self.mode = "Live" if use_live_gemini() else "Mock"
        self.client = client or GeminiClient(model=self.model)

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> Union[AIResponse, AIProviderError]:
        if self.mode != "Live":
            return self._mock_response(system_prompt, user_prompt)

        logger.info("Generating content with Gemini model %s", self.model)
        return self.client.generate(system_prompt, user_prompt)

    def ask(self, prompt: str) -> str:
        response = self.generate("", prompt)
        if isinstance(response, AIProviderError):
            logger.error("Gemini provider failed: %s", response.message)
            return ""
        return response.content

    def _mock_response(self, system_prompt: str, user_prompt: str) -> AIResponse:
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


class LucidAI:
    """Backward-compatible AI facade."""

    def __init__(self, provider: GeminiProvider | None = None) -> None:
        self.provider = provider or GeminiProvider()

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
    def create(provider: str = "gemini") -> GeminiProvider:
        if provider.lower() != "gemini":
            logger.warning("Unsupported provider requested: %s", provider)
        return GeminiProvider()
