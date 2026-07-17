# OPENAI_DEFAULT_PROVIDER_REPORT

## Scope

Switched the production GUI default AI provider from Gemini to OpenAI while keeping multi-provider support.

No GUI layout, DOCX exporter, or production pipeline layout was modified.

## Files Changed

- `src/hgpt_ai_os/ai/config_resolver.py`
- `src/hgpt_ai_os/ai/client.py`
- `src/hgpt_ai_os/providers/provider_manager.py`
- `src/hgpt_ai_os/settings/config_manager.py`
- `tests/test_ai_config_resolver.py`
- `tests/test_provider_layer.py`

## Provider Selection Rule

- OpenAI is selected when `OPENAI_API_KEY` exists.
- Gemini is selected only when OpenAI is unavailable and a Gemini key exists.
- Existing multi-provider support remains through `AIManager`.
- Production `ProviderManager.generate_real_ai()` now uses the manager path for OpenAI/Gemini so fallback remains available.

## Verification

Command checks:

- `PYTHONPYCACHEPREFIX=/tmp/lucid_pycache PYTHONPATH=src python3 -m py_compile src/hgpt_ai_os/ai/config_resolver.py src/hgpt_ai_os/ai/client.py src/hgpt_ai_os/providers/provider_manager.py src/hgpt_ai_os/settings/config_manager.py`
- `PYTHONPYCACHEPREFIX=/tmp/lucid_pycache PYTHONPATH=src python3 -m unittest tests.test_ai_config_resolver tests.test_provider_layer`

Result:

- `Ran 20 tests`
- `OK`

GUI verification:

- Runtime: `QT_QPA_PLATFORM=offscreen`
- Entry path: `hgpt_ai_os.gui.main_window.MainWindow.generate()` -> `ProductionWorker` -> `ProductionService` -> `PlatformRuntime` -> production export
- Topic: `Vòng bi động cơ bị kêu`
- Provider: `OpenAI`
- Model: `gpt-4o-mini-2024-07-18`
- HTTP: `200`
- EngineeringRecord Source: `AI_PROVIDER`
- EngineeringRecord Created: `YES`
- Output folder: `/Users/macos/Documents/LUCID/outputs/marketing/Day1045`
- DOCX Count: `7`

Generated DOCX files:

- `approval_checklist.docx`
- `facebook.docx`
- `hashtags.docx`
- `image_prompt.docx`
- `seo.docx`
- `tiktok.docx`
- `video_prompt.docx`

## Status

PASS
