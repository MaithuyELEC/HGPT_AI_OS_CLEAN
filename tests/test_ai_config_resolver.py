from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from hgpt_ai_os.ai.config_resolver import (
    is_free_desktop_mode,
    resolve_ai_config,
    validate_ai_provider_config,
)


class AIConfigResolverTests(unittest.TestCase):
    def setUp(self):
        self.previous_cwd = Path.cwd()

    def tearDown(self):
        os.chdir(self.previous_cwd)
        if hasattr(sys, "frozen"):
            delattr(sys, "frozen")
        if hasattr(sys, "_MEIPASS"):
            delattr(sys, "_MEIPASS")

    def test_environment_values_win_before_config_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cwd = root / "cwd"
            docs = root / "profile" / "Documents" / "LUCID"
            cwd.mkdir()
            docs.mkdir(parents=True)
            (cwd / ".env").write_text(
                "AI_PROVIDER=gemini\nGEMINI_API_KEY=file-key\n",
                encoding="utf-8",
            )
            (docs / "config.json").write_text(
                json.dumps(
                    {
                        "AI_PROVIDER": "anthropic",
                        "ANTHROPIC_API_KEY": "doc-key",
                    }
                ),
                encoding="utf-8",
            )
            os.chdir(cwd)

            with mock.patch.dict(
                os.environ,
                {
                    "AI_PROVIDER": "openai",
                    "OPENAI_API_KEY": "env-key",
                    "USERPROFILE": str(root / "profile"),
                },
                clear=True,
            ):
                config = resolve_ai_config()

            self.assertEqual(config.provider, "openai")
            self.assertEqual(config.source, "environment variables")
            self.assertEqual(config.api_key_for_provider(), "env-key")

    def test_cwd_dotenv_wins_before_documents_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cwd = root / "cwd"
            docs = root / "profile" / "Documents" / "LUCID"
            cwd.mkdir()
            docs.mkdir(parents=True)
            (cwd / ".env").write_text(
                "AI_PROVIDER=gemini\nGEMINI_API_KEY=file-key\n",
                encoding="utf-8",
            )
            (docs / "config.json").write_text(
                json.dumps(
                    {
                        "AI_PROVIDER": "openai",
                        "OPENAI_API_KEY": "doc-key",
                    }
                ),
                encoding="utf-8",
            )
            os.chdir(cwd)

            with mock.patch.dict(
                os.environ,
                {"USERPROFILE": str(root / "profile")},
                clear=True,
            ):
                config = resolve_ai_config()

            self.assertEqual(config.provider, "gemini")
            self.assertTrue(Path(config.source).samefile(cwd / ".env"))
            self.assertEqual(config.api_key_for_provider(), "file-key")

    def test_missing_config_creates_example_and_enters_free_desktop_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cwd = root / "cwd"
            profile = root / "profile"
            cwd.mkdir()
            os.chdir(cwd)

            with mock.patch.dict(
                os.environ,
                {"USERPROFILE": str(profile)},
                clear=True,
            ):
                validation = validate_ai_provider_config()

            example_path = profile / "Documents" / "LUCID" / "config.example.json"
            self.assertTrue(validation.ok)
            self.assertEqual(validation.message, "Free Desktop Mode enabled.")
            self.assertEqual(validation.status, "Free Desktop")
            self.assertEqual(validation.reason, "Free Desktop Mode")
            with mock.patch.dict(
                os.environ,
                {"USERPROFILE": str(profile)},
                clear=True,
            ):
                self.assertTrue(is_free_desktop_mode())
            self.assertTrue(example_path.exists())
            self.assertEqual(
                json.loads(example_path.read_text(encoding="utf-8")),
                {
                    "AI_PROVIDER": "gemini",
                    "GEMINI_API_KEY": "",
                    "OPENAI_API_KEY": "",
                    "ANTHROPIC_API_KEY": "",
                },
            )

    def test_provider_without_api_key_enters_free_desktop_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cwd = root / "cwd"
            profile = root / "profile"
            cwd.mkdir()
            os.chdir(cwd)

            with mock.patch.dict(
                os.environ,
                {
                    "USERPROFILE": str(profile),
                    "AI_PROVIDER": "openai",
                    "OPENAI_API_KEY": "",
                },
                clear=True,
            ):
                validation = validate_ai_provider_config()
                self.assertTrue(validation.ok)
                self.assertEqual(validation.status, "Free Desktop")
                self.assertEqual(validation.reason, "Free Desktop Mode")
                self.assertEqual(validation.missing_key, "OPENAI_API_KEY")


if __name__ == "__main__":
    unittest.main()
