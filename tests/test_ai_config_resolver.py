from __future__ import annotations

import json
import os
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

    def test_config_manager_json_is_single_source_of_truth(self):
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
            config_path = docs / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "provider": "openai",
                        "openai_api_key": "json-openai-key",
                        "gemini_api_key": "",
                        "anthropic_api_key": "",
                    }
                ),
                encoding="utf-8",
            )
            os.chdir(cwd)

            with mock.patch.dict(
                os.environ,
                {
                    "USERPROFILE": str(root / "profile"),
                    "AI_PROVIDER": "gemini",
                    "GEMINI_API_KEY": "env-gemini-key",
                },
                clear=True,
            ):
                config = resolve_ai_config()

            self.assertEqual(config.provider, "openai")
            self.assertEqual(Path(config.source), config_path)
            self.assertEqual(config.api_key_for_provider(), "json-openai-key")

    def test_missing_config_creates_default_config_and_enters_free_desktop_mode(self):
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

            config_path = profile / "Documents" / "LUCID" / "config.json"
            self.assertTrue(validation.ok)
            self.assertEqual(validation.message, "Free Desktop Mode enabled.")
            self.assertEqual(validation.status, "Free Desktop")
            self.assertEqual(validation.reason, "Free Desktop Mode")
            self.assertEqual(validation.missing_key, "OPENAI_API_KEY")
            self.assertTrue(config_path.exists())
            self.assertEqual(
                json.loads(config_path.read_text(encoding="utf-8")),
                {
                    "provider": "openai",
                    "openai_api_key": "",
                    "gemini_api_key": "",
                    "anthropic_api_key": "",
                },
            )

    def test_is_free_desktop_mode_uses_config_manager_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "profile" / "Documents" / "LUCID"
            docs.mkdir(parents=True)
            (docs / "config.json").write_text(
                json.dumps(
                    {
                        "provider": "none",
                        "openai_api_key": "",
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
                self.assertTrue(is_free_desktop_mode())

    def test_provider_without_api_key_enters_free_desktop_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "profile" / "Documents" / "LUCID"
            docs.mkdir(parents=True)
            (docs / "config.json").write_text(
                json.dumps(
                    {
                        "provider": "openai",
                        "openai_api_key": "",
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
                validation = validate_ai_provider_config()

            self.assertTrue(validation.ok)
            self.assertEqual(validation.status, "Free Desktop")
            self.assertEqual(validation.reason, "Free Desktop Mode")
            self.assertEqual(validation.missing_key, "OPENAI_API_KEY")


if __name__ == "__main__":
    unittest.main()
