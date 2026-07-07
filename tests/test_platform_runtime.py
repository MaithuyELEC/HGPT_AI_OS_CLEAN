from __future__ import annotations

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import ANY, Mock, patch

from hgpt_ai_os.platform import PlatformRuntime, RuntimeSettings
from hgpt_ai_os.platform.registry import PlatformServiceRegistry


class RecordingComponent:
    def __init__(self, events: list[str], name: str) -> None:
        self.events = events
        self.name = name

    def start(self) -> None:
        self.events.append(f"start:{self.name}")

    def stop(self) -> None:
        self.events.append(f"stop:{self.name}")


class FailingComponent(RecordingComponent):
    def start(self) -> None:
        super().start()
        raise RuntimeError("boom")


class PlatformRuntimeTests(unittest.TestCase):
    def test_runtime_exposes_context_and_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            runtime = PlatformRuntime(
                RuntimeSettings(
                    environment="test",
                    workspace=Path(tmp),
                    metadata={"compatibility": "lucid-auto"},
                )
            )

            self.assertEqual(runtime.context.app_name, "LUCID PLATFORM")
            self.assertEqual(runtime.context.environment, "test")
            self.assertEqual(runtime.context.workspace, Path(tmp))
            self.assertEqual(
                runtime.context.metadata,
                {"compatibility": "lucid-auto"},
            )
            self.assertFalse(runtime.status()["running"])
            self.assertIn(
                "legacy.production",
                runtime.status()["services"],
            )

    def test_runtime_lifecycle_starts_and_stops_in_order(self):
        events: list[str] = []
        runtime = PlatformRuntime()
        runtime.add_component(RecordingComponent(events, "a"))
        runtime.add_component(RecordingComponent(events, "b"))

        runtime.start()
        self.assertTrue(runtime.running)
        runtime.stop()

        self.assertFalse(runtime.running)
        self.assertEqual(events, ["start:a", "start:b", "stop:b", "stop:a"])

    def test_runtime_rolls_back_started_components_on_start_failure(self):
        events: list[str] = []
        runtime = PlatformRuntime()
        runtime.add_component(RecordingComponent(events, "ready"))
        runtime.add_component(FailingComponent(events, "fail"))

        with self.assertRaises(RuntimeError):
            runtime.start()

        self.assertFalse(runtime.running)
        self.assertEqual(events, ["start:ready", "start:fail", "stop:ready"])


class PlatformServiceRegistryTests(unittest.TestCase):
    def test_registry_registers_and_validates_services(self):
        registry = PlatformServiceRegistry()
        registry.register("answer", 42)

        self.assertTrue(registry.contains("answer"))
        self.assertEqual(registry.get("answer", int), 42)
        self.assertEqual(registry.keys(), ("answer",))

    def test_registry_rejects_empty_duplicate_and_wrong_type(self):
        registry = PlatformServiceRegistry()

        with self.assertRaises(ValueError):
            registry.register(" ", object())

        registry.register("service", object())
        with self.assertRaises(KeyError):
            registry.register("service", object())
        with self.assertRaises(TypeError):
            registry.get("service", str)


class PlatformRuntimeProductionTests(unittest.TestCase):
    def test_runtime_execute_orchestrates_legacy_production(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            docx = output_dir / "result.docx"
            docx.write_text("placeholder")
            runtime = PlatformRuntime()
            adapter = runtime.registry.get("legacy.production")
            metadata = {"knowledge_count": None}

            def execute(*args, **kwargs):
                metadata["knowledge_count"] = 3
                return output_dir

            with (
                patch.object(adapter, "next_day", return_value=7) as next_day,
                patch.object(adapter, "execute", side_effect=execute) as execute,
            ):
                result = runtime.execute(
                    "AI QA",
                    open_output_folder=False,
                    knowledge_count_provider=lambda: metadata["knowledge_count"],
                    started_at=1.0,
                )

        next_day.assert_called_once_with()
        execute.assert_called_once_with(
            7,
            "AI QA",
            open_output_folder=False,
        )
        self.assertTrue(result.success)
        self.assertEqual(result.output_dir, output_dir)
        self.assertEqual(result.generated_files, [docx])
        self.assertEqual(result.knowledge_count, 3)
        self.assertIsNotNone(result.elapsed_seconds)

    def test_production_service_uses_platform_runtime_adapter(self):
        from hgpt_ai_os.gui.production_service import ProductionService

        runtime = Mock(spec=PlatformRuntime)
        output_dir = Path("Day 7")
        runtime.execute.return_value = output_dir

        result = ProductionService(runtime).run("AI QA")

        runtime.execute.assert_called_once_with(
            "AI QA",
            open_output_folder=False,
            knowledge_count_provider=ANY,
            started_at=ANY,
        )
        self.assertEqual(result, output_dir)

    def test_free_desktop_mode_runs_without_ai_tokens(self):
        from hgpt_ai_os import production
        from hgpt_ai_os.gui.production_service import ProductionService

        previous_cwd = Path.cwd()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cwd = root / "cwd"
            output_root = root / "outputs"
            profile = root / "profile"
            cwd.mkdir()
            os.chdir(cwd)

            free_env = {
                "USERPROFILE": str(profile),
                "AI_PROVIDER": "",
                "OPENAI_API_KEY": "",
                "GEMINI_API_KEY": "",
                "GOOGLE_API_KEY": "",
                "ANTHROPIC_API_KEY": "",
            }
            try:
                with (
                    patch.dict(os.environ, free_env, clear=True),
                    patch.object(production, "OUTPUT_ROOT", output_root),
                ):
                    result = ProductionService().run("test topic")

                self.assertTrue(result.success)
                self.assertTrue(result.output_dir.exists())
                self.assertEqual(
                    [path.name for path in result.generated_files],
                    [
                        "approval_checklist.docx",
                        "facebook.docx",
                        "hashtags.docx",
                        "image_prompt.docx",
                        "seo.docx",
                        "tiktok.docx",
                        "video_prompt.docx",
                    ],
                )
            finally:
                os.chdir(previous_cwd)

    def test_free_desktop_mode_makes_zero_provider_calls(self):
        from hgpt_ai_os import production
        from hgpt_ai_os.gui.production_service import ProductionService

        previous_cwd = Path.cwd()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cwd = root / "cwd"
            output_root = root / "outputs"
            profile = root / "profile"
            cwd.mkdir()
            os.chdir(cwd)

            free_env = {
                "USERPROFILE": str(profile),
                "AI_PROVIDER": "none",
                "OPENAI_API_KEY": "",
                "GEMINI_API_KEY": "",
                "GOOGLE_API_KEY": "",
                "ANTHROPIC_API_KEY": "",
            }
            stdout = io.StringIO()
            try:
                with (
                    patch.dict(os.environ, free_env, clear=True),
                    patch.object(production, "OUTPUT_ROOT", output_root),
                    patch(
                        "hgpt_ai_os.content.generator.LucidAI",
                        side_effect=AssertionError("LucidAI must not initialize"),
                    ) as lucid_ai,
                    patch(
                        "hgpt_ai_os.ai.client.GeminiProvider.__init__",
                        side_effect=AssertionError("Gemini must not initialize"),
                    ) as gemini_init,
                    patch(
                        "hgpt_ai_os.ai.client.OpenAIProvider.__init__",
                        side_effect=AssertionError("OpenAI must not initialize"),
                    ) as openai_init,
                    patch(
                        "hgpt_ai_os.ai.client.AnthropicProvider.__init__",
                        side_effect=AssertionError("Anthropic must not initialize"),
                    ) as anthropic_init,
                    patch(
                        "hgpt_ai_os.ai.client.OllamaProvider.__init__",
                        side_effect=AssertionError("Ollama must not initialize"),
                    ) as ollama_init,
                    patch(
                        "urllib.request.urlopen",
                        side_effect=AssertionError("remote provider call attempted"),
                    ) as urlopen,
                    redirect_stdout(stdout),
                ):
                    result = ProductionService().run("test topic")

                self.assertTrue(result.success)
                self.assertEqual(len(result.generated_files), 7)
                self.assertIn("Mode : Free Desktop", stdout.getvalue())
                self.assertIn("Generator : Built-in", stdout.getvalue())
                self.assertIn("AI Provider : Disabled", stdout.getvalue())
                self.assertNotIn("configuration_error", stdout.getvalue())
                self.assertNotIn("AI generation failed", stdout.getvalue())
                lucid_ai.assert_not_called()
                gemini_init.assert_not_called()
                openai_init.assert_not_called()
                anthropic_init.assert_not_called()
                ollama_init.assert_not_called()
                urlopen.assert_not_called()
            finally:
                os.chdir(previous_cwd)


if __name__ == "__main__":
    unittest.main()
