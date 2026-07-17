# AI Provider Truth Report

Audit date: 2026-07-14 21:25 Asia/Ho_Chi_Minh

Repository: `/Users/macos/Desktop/HGPT_AI_OS_CLEAN`

Question: Is the production GUI actually calling a real AI provider?

Answer: YES, in the GUI-equivalent production path after `ConfigManager.validate()`, production selects Gemini and attempts real HTTP POST calls to Google Gemini. The calls fail with HTTP 429 `RESOURCE_EXHAUSTED`, so no AI `EngineeringRecord` is accepted. Production then falls back to local engineering records.

## Execution Path Verified

GUI Generate path:

`MainWindow.generate`
-> `ProductionWorker`
-> `ProductionService.run`
-> `PlatformRuntime.execute`
-> `LegacyProductionAdapter.execute`
-> `production.build_outputs`
-> `EngineeringGenerationPipeline.generate_documents`
-> `EngineeringGenerationPipeline.build_record`
-> `EngineeringGenerationPipeline._ai_record`
-> `LucidAI.generate`
-> `GeminiProvider.generate`
-> `GeminiClient.generate`
-> HTTP POST to Gemini
-> `AIProviderError`
-> local `EngineeringRecord`
-> `render_all`
-> `DocxExporter.save`

Source evidence:

- GUI validates config before worker: `src/hgpt_ai_os/gui/main_window.py:738-782`
- Worker calls production service: `src/hgpt_ai_os/gui/worker.py:60-68`
- Production service calls platform runtime: `src/hgpt_ai_os/gui/production_service.py:16-24`
- Platform runtime calls legacy production adapter: `src/hgpt_ai_os/platform/runtime.py:106-122`
- Adapter calls `production.build_outputs`: `src/hgpt_ai_os/platform/legacy_production_adapter.py:17-30`
- Production initializes pipeline and prints provider mode: `src/hgpt_ai_os/production.py:74-94`
- Pipeline calls AI only when not Free Desktop Mode: `src/hgpt_ai_os/engineering_pipeline/pipeline.py:49-56`, `src/hgpt_ai_os/engineering_pipeline/pipeline.py:96-102`
- AI provider error fallback line: `src/hgpt_ai_os/engineering_pipeline/pipeline.py:103-105`
- Local record fallback starts: `src/hgpt_ai_os/engineering_pipeline/pipeline.py:118-163`
- Renderer called after record: `src/hgpt_ai_os/engineering_pipeline/pipeline.py:69`

## Runtime Provider State

ConfigManager validation:

```json
{
  "ok": true,
  "status": "Connected",
  "provider": "gemini",
  "reason": ""
}
```

AI resolver validation after GUI config load:

```json
{
  "source": "environment variables",
  "provider": "gemini",
  "free_desktop_mode": false,
  "ok": true,
  "status": "Ready",
  "reason": "",
  "missing_key": "",
  "values_present": {
    "AI_PROVIDER": true,
    "OPENAI_API_KEY": true,
    "GEMINI_API_KEY": true,
    "ANTHROPIC_API_KEY": false
  }
}
```

Provider status:

```json
{
  "ai_provider": "PASS",
  "provider": "gemini",
  "mode": "Live",
  "source": "environment variables",
  "gemini": "Configured",
  "openai": "Configured",
  "anthropic": "Unavailable",
  "ollama": "Disabled",
  "model": "gemini-2.5-pro"
}
```

## Topic Audit

### TOPIC: Vòng bi động cơ bị kêu

PROVIDER: Gemini

PROVIDER ENABLED/DISABLED: Enabled. `free_desktop_mode=false`; `ConfigManager` status `Connected`.

MODEL: `gemini-2.5-pro`

AI CALLED: YES

API CALL ATTEMPTED: YES, 3 attempts.

HTTP/API RESULT: HTTP 429 `Too Many Requests`; provider returned `AIProviderError`, `error_type=http_error`, `retryable=true`.

RESPONSE LENGTH: 0 accepted AI content characters. No `AIResponse` content was returned; only provider error metadata was returned.

RESPONSE JSON:

```json
{
  "error": {
    "code": 429,
    "message": "You exceeded your current quota, please check your plan and billing details... Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests... Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_input_token_count... Please retry in 28.354372834s.",
    "status": "RESOURCE_EXHAUSTED",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.Help"
      },
      {
        "@type": "type.googleapis.com/google.rpc.QuotaFailure",
        "violations": [
          {
            "quotaMetric": "generativelanguage.googleapis.com/generate_content_free_tier_requests",
            "quotaId": "GenerateRequestsPerDayPerProjectPerModel-FreeTier",
            "quotaDimensions": {
              "location": "global",
              "model": "gemini-2.5-pro"
            }
          },
          {
            "quotaMetric": "generativelanguage.googleapis.com/generate_content_free_tier_requests",
            "quotaId": "GenerateRequestsPerMinutePerProjectPerModel-FreeTier",
            "quotaDimensions": {
              "location": "global",
              "model": "gemini-2.5-pro"
            }
          },
          {
            "quotaMetric": "generativelanguage.googleapis.com/generate_content_free_tier_input_token_count",
            "quotaId": "GenerateContentInputTokensPerModelPerMinute-FreeTier",
            "quotaDimensions": {
              "location": "global",
              "model": "gemini-2.5-pro"
            }
          },
          {
            "quotaMetric": "generativelanguage.googleapis.com/generate_content_free_tier_input_token_count",
            "quotaId": "GenerateContentInputTokensPerModelPerDay-FreeTier",
            "quotaDimensions": {
              "location": "global",
              "model": "gemini-2.5-pro"
            }
          }
        ]
      },
      {
        "@type": "type.googleapis.com/google.rpc.RetryInfo",
        "retryDelay": "28s"
      }
    ]
  }
}
```

ENGINEERING RECORD SOURCE: `EXACT_PLAYBOOK`

Selected knowledge/playbook key: `CONVEYOR_BELT_MISALIGNMENT`

Knowledge search result IDs: none

Final record `source_keys`:

```json
["CONVEYOR_BELT_MISALIGNMENT"]
```

FALLBACK: YES

Fallback reason and exact line: `src/hgpt_ai_os/engineering_pipeline/pipeline.py:103-105 AIProviderError -> return None`

ROOT CAUSE OF WRONG CONTENT: The real AI provider was called, but Gemini returned HTTP 429 `RESOURCE_EXHAUSTED`. Because `_ai_record()` returns `None` on `AIProviderError`, production used the local record. The local playbook selector chose `CONVEYOR_BELT_MISALIGNMENT` for a motor bearing noise topic, so conveyor-belt content entered the final `EngineeringRecord`.

### TOPIC: Động cơ 3 pha bị nóng

PROVIDER: Gemini

PROVIDER ENABLED/DISABLED: Enabled. `free_desktop_mode=false`; `ConfigManager` status `Connected`.

MODEL: `gemini-2.5-pro`

AI CALLED: YES

API CALL ATTEMPTED: YES, 3 attempts.

HTTP/API RESULT: HTTP 429 `Too Many Requests`; provider returned `AIProviderError`, `error_type=http_error`, `retryable=true`.

RESPONSE LENGTH: 0 accepted AI content characters. No `AIResponse` content was returned; only provider error metadata was returned.

RESPONSE JSON:

```json
{
  "error": {
    "code": 429,
    "message": "You exceeded your current quota... Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests... Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_input_token_count... Please retry in 24.115950948s.",
    "status": "RESOURCE_EXHAUSTED",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.Help"
      },
      {
        "@type": "type.googleapis.com/google.rpc.QuotaFailure"
      },
      {
        "@type": "type.googleapis.com/google.rpc.RetryInfo",
        "retryDelay": "24s"
      }
    ]
  }
}
```

ENGINEERING RECORD SOURCE: `LOCAL_FALLBACK`

Selected knowledge/playbook key: none

Knowledge search result IDs: none

Final record `source_keys`:

```json
["LOCAL_ENGINEERING_REASONER"]
```

FALLBACK: YES

Fallback reason and exact line: `src/hgpt_ai_os/engineering_pipeline/pipeline.py:103-105 AIProviderError -> return None`

ROOT CAUSE OF WRONG CONTENT: The real AI provider was called, but Gemini returned HTTP 429 `RESOURCE_EXHAUSTED`. Because `_ai_record()` returns `None` on `AIProviderError`, production used the local engineering reasoner. No playbook or knowledge item was selected, so the record stayed generic.

### TOPIC: Bơm thủy lực bị mất áp

PROVIDER: Gemini

PROVIDER ENABLED/DISABLED: Enabled. `free_desktop_mode=false`; `ConfigManager` status `Connected`.

MODEL: `gemini-2.5-pro`

AI CALLED: YES

API CALL ATTEMPTED: YES, 3 attempts.

HTTP/API RESULT: HTTP 429 `Too Many Requests`; provider returned `AIProviderError`, `error_type=http_error`, `retryable=true`.

RESPONSE LENGTH: 0 accepted AI content characters. No `AIResponse` content was returned; only provider error metadata was returned.

RESPONSE JSON:

```json
{
  "error": {
    "code": 429,
    "message": "You exceeded your current quota... Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_input_token_count... Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests... Please retry in 19.920632743s.",
    "status": "RESOURCE_EXHAUSTED",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.Help"
      },
      {
        "@type": "type.googleapis.com/google.rpc.QuotaFailure"
      },
      {
        "@type": "type.googleapis.com/google.rpc.RetryInfo",
        "retryDelay": "19s"
      }
    ]
  }
}
```

ENGINEERING RECORD SOURCE: `LOCAL_FALLBACK`

Selected knowledge/playbook key: none

Knowledge search result IDs: none

Final record `source_keys`:

```json
["LOCAL_ENGINEERING_REASONER"]
```

FALLBACK: YES

Fallback reason and exact line: `src/hgpt_ai_os/engineering_pipeline/pipeline.py:103-105 AIProviderError -> return None`

ROOT CAUSE OF WRONG CONTENT: The real AI provider was called, but Gemini returned HTTP 429 `RESOURCE_EXHAUSTED`. Because `_ai_record()` returns `None` on `AIProviderError`, production used the local engineering reasoner. No playbook or knowledge item was selected, so the final record used generic local fallback structure.

## Final Finding

Production GUI is actually calling a real AI provider when the GUI config path is exercised.

The current production outputs are still wrong because every audited Gemini request failed with HTTP 429 `RESOURCE_EXHAUSTED`; therefore no AI-generated `EngineeringRecord` reached the renderer. The rendered DOCX content came from local fallback records:

- `Vòng bi động cơ bị kêu`: local exact playbook fallback selected `CONVEYOR_BELT_MISALIGNMENT`.
- `Động cơ 3 pha bị nóng`: local fallback with no selected playbook.
- `Bơm thủy lực bị mất áp`: local fallback with no selected playbook.

