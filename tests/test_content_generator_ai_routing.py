from __future__ import annotations

import json
import os
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
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
    @contextmanager
    def _config(self, provider: str, *, openai_key: str = ""):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "profile" / "Documents" / "LUCID"
            docs.mkdir(parents=True)
            (docs / "config.json").write_text(
                json.dumps(
                    {
                        "provider": provider,
                        "openai_api_key": openai_key,
                        "gemini_api_key": "",
                        "anthropic_api_key": "",
                    }
                ),
                encoding="utf-8",
            )
            with mock.patch.dict(
                os.environ,
                {"USERPROFILE": str(root / "profile")},
                clear=True,
            ):
                yield

    def _patch_topic_engine(self):
        return mock.patch(
            "hgpt_ai_os.content.generator.TopicIntelligenceEngine.generate",
            return_value="Offline Topic Intelligence content",
        )

    def test_free_desktop_mode_does_not_call_ai(self):
        ai = _FailingAI(exc=AssertionError("AI must not be called"))
        with (
            self._config("free_desktop"),
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
            self._config("disabled"),
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
            self._config("openai", openai_key="test-key"),
            self._patch_topic_engine() as topic_generate,
        ):
            output = ContentGenerator(ai=ai).generate("facebook", "5S trong xưởng")

        self.assertEqual(output, "AI content approved for production.")
        self.assertEqual(ai.calls, 1)
        topic_generate.assert_not_called()

    def test_ai_exception_does_not_call_topic_intelligence_in_ai_mode(self):
        ai = _FailingAI(exc=TimeoutError("timeout"))
        with (
            self._config("openai", openai_key="test-key"),
            self._patch_topic_engine() as topic_generate,
        ):
            with self.assertRaises(TimeoutError):
                ContentGenerator(ai=ai).generate("seo", "5S trong xưởng")

        self.assertEqual(ai.calls, 1)
        topic_generate.assert_not_called()

    def test_ai_provider_error_does_not_call_topic_intelligence_in_ai_mode(self):
        ai = _FailingAI(
            response=AIProviderError(
                provider="OpenAI",
                model="test",
                message="OpenAI error: API key quota",
            )
        )
        with (
            self._config("openai", openai_key="test-key"),
            self._patch_topic_engine() as topic_generate,
        ):
            with self.assertRaises(RuntimeError):
                ContentGenerator(ai=ai).generate("seo", "5S trong xưởng")

        self.assertEqual(ai.calls, 1)
        topic_generate.assert_not_called()

    def test_empty_ai_response_does_not_call_topic_intelligence_in_ai_mode(self):
        ai = _FailingAI(
            response=AIResponse(
                provider="OpenAI",
                model="test",
                content="   ",
            )
        )
        with (
            self._config("openai", openai_key="test-key"),
            self._patch_topic_engine() as topic_generate,
        ):
            with self.assertRaises(RuntimeError):
                ContentGenerator(ai=ai).generate("seo", "5S trong xưởng")

        self.assertEqual(ai.calls, 1)
        topic_generate.assert_not_called()

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
            self._config("openai", openai_key="test-key"),
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

    def test_old_provider_failure_messages_are_not_local_fallback_in_ai_mode(self):
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
                    self._config("openai", openai_key="test-key"),
                    self._patch_topic_engine() as topic_generate,
                ):
                    with self.assertRaises(RuntimeError):
                        ContentGenerator(ai=ai).generate(
                            "facebook",
                            "5S trong xưởng",
                        )

                self.assertEqual(ai.calls, 1)
                topic_generate.assert_not_called()


if __name__ == "__main__":
    unittest.main()
