from __future__ import annotations

import os
import unittest
from unittest import mock

from hgpt_ai_os.ai.gemini_client import AIProviderError, AIResponse
from hgpt_ai_os.content.generator import ContentGenerator


OLD_PROVIDER_FAILURE_MESSAGES = (
    "AI provider encountered an error while generating content. "
    "Please check network, SSL, and provider configuration, then try again.",
    "AI provider is unavailable. Please check API key and provider configuration.",
    "AI provider is not available. Please check API key and provider configuration.",
)


class _FailingAI:
    def __init__(self, response=None, exc: Exception | None = None):
        self.response = response
        self.exc = exc
        self.calls = 0

    def generate(self, system_prompt: str, user_prompt: str):
        self.calls += 1
        if self.exc is not None:
            raise self.exc
        return self.response


class ContentGeneratorAIRoutingTests(unittest.TestCase):
    def _offline_env(self, provider: str = "none") -> dict[str, str]:
        return {
            "AI_PROVIDER": provider,
            "OPENAI_API_KEY": "",
            "GEMINI_API_KEY": "",
            "GOOGLE_API_KEY": "",
            "ANTHROPIC_API_KEY": "",
        }

    def _online_env(self) -> dict[str, str]:
        return {
            "AI_PROVIDER": "openai",
            "OPENAI_API_KEY": "test-key",
            "GEMINI_API_KEY": "",
            "GOOGLE_API_KEY": "",
            "ANTHROPIC_API_KEY": "",
        }

    def _patch_topic_engine(self):
        return mock.patch(
            "hgpt_ai_os.content.generator.TopicIntelligenceEngine.generate",
            return_value="Offline Topic Intelligence content",
        )

    def test_free_desktop_mode_does_not_call_ai(self):
        ai = _FailingAI(exc=AssertionError("AI must not be called"))
        with (
            mock.patch.dict(os.environ, self._offline_env("free_desktop"), clear=True),
            mock.patch(
                "hgpt_ai_os.content.generator.LucidAI",
                side_effect=AssertionError("LucidAI must not initialize"),
            ) as lucid_ai,
            self._patch_topic_engine() as topic_generate,
        ):
            output = ContentGenerator(ai=ai).generate("facebook", "5S trong xưởng")

        self.assertEqual(output, "Offline Topic Intelligence content")
        self.assertEqual(ai.calls, 0)
        lucid_ai.assert_not_called()
        topic_generate.assert_called_once()

    def test_disabled_provider_does_not_call_ai(self):
        ai = _FailingAI(exc=AssertionError("AI must not be called"))
        with (
            mock.patch.dict(os.environ, self._offline_env("disabled"), clear=True),
            mock.patch(
                "hgpt_ai_os.content.generator.LucidAI",
                side_effect=AssertionError("LucidAI must not initialize"),
            ) as lucid_ai,
            self._patch_topic_engine() as topic_generate,
        ):
            output = ContentGenerator(ai=ai).generate("facebook", "5S trong xưởng")

        self.assertEqual(output, "Offline Topic Intelligence content")
        self.assertEqual(ai.calls, 0)
        lucid_ai.assert_not_called()
        topic_generate.assert_called_once()

    def test_enabled_provider_uses_injected_ai_without_topic_intelligence(self):
        ai = _FailingAI(
            response=AIResponse(
                provider="OpenAI",
                model="test",
                content="AI content approved for production.",
            )
        )
        with (
            mock.patch.dict(os.environ, self._online_env(), clear=True),
            self._patch_topic_engine() as topic_generate,
        ):
            output = ContentGenerator(ai=ai).generate("facebook", "5S trong xưởng")

        self.assertEqual(output, "AI content approved for production.")
        self.assertEqual(ai.calls, 1)
        topic_generate.assert_not_called()

    def test_ai_exception_falls_back_to_topic_intelligence(self):
        ai = _FailingAI(exc=TimeoutError("timeout"))
        with (
            mock.patch.dict(os.environ, self._online_env(), clear=True),
            self._patch_topic_engine() as topic_generate,
        ):
            output = ContentGenerator(ai=ai).generate("seo", "5S trong xưởng")

        self.assertEqual(output, "Offline Topic Intelligence content")
        self.assertEqual(ai.calls, 1)
        topic_generate.assert_called_once()

    def test_ai_provider_error_falls_back_to_topic_intelligence(self):
        ai = _FailingAI(
            response=AIProviderError(
                provider="OpenAI",
                model="test",
                message="OpenAI error: API key quota",
            )
        )
        with (
            mock.patch.dict(os.environ, self._online_env(), clear=True),
            self._patch_topic_engine() as topic_generate,
        ):
            output = ContentGenerator(ai=ai).generate("seo", "5S trong xưởng")

        self.assertEqual(output, "Offline Topic Intelligence content")
        self.assertEqual(ai.calls, 1)
        topic_generate.assert_called_once()

    def test_empty_ai_response_falls_back_to_topic_intelligence(self):
        ai = _FailingAI(
            response=AIResponse(
                provider="OpenAI",
                model="test",
                content="   ",
            )
        )
        with (
            mock.patch.dict(os.environ, self._online_env(), clear=True),
            self._patch_topic_engine() as topic_generate,
        ):
            output = ContentGenerator(ai=ai).generate("seo", "5S trong xưởng")

        self.assertEqual(output, "Offline Topic Intelligence content")
        self.assertEqual(ai.calls, 1)
        topic_generate.assert_called_once()

    def test_engineering_terms_are_valid_ai_content(self):
        ai = _FailingAI(
            response=AIResponse(
                provider="OpenAI",
                model="test",
                content=(
                    "The API key rotation plan should include SSL certificate "
                    "checks, quota monitoring, Gemini routing, and OpenAI "
                    "fallback verification."
                ),
            )
        )
        with (
            mock.patch.dict(os.environ, self._online_env(), clear=True),
            self._patch_topic_engine() as topic_generate,
        ):
            output = ContentGenerator(ai=ai).generate("facebook", "5S trong xưởng")

        self.assertIn("API key", output)
        self.assertIn("SSL", output)
        self.assertIn("quota", output)
        self.assertIn("Gemini", output)
        self.assertIn("OpenAI", output)
        self.assertEqual(ai.calls, 1)
        topic_generate.assert_not_called()

    def test_old_provider_failure_messages_fall_back(self):
        for message in OLD_PROVIDER_FAILURE_MESSAGES:
            with self.subTest(message=message):
                ai = _FailingAI(
                    response=AIResponse(
                        provider="OpenAI",
                        model="test",
                        content=message,
                    )
                )
                with (
                    mock.patch.dict(os.environ, self._online_env(), clear=True),
                    self._patch_topic_engine() as topic_generate,
                ):
                    output = ContentGenerator(ai=ai).generate(
                        "facebook",
                        "5S trong xưởng",
                    )

                self.assertEqual(output, "Offline Topic Intelligence content")
                self.assertEqual(ai.calls, 1)
                topic_generate.assert_called_once()


if __name__ == "__main__":
    unittest.main()
