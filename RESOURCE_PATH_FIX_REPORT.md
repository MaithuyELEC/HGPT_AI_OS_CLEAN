# RESOURCE_PATH_FIX_REPORT

## Root Cause

Unit-test imports failed because `EngineeringKnowledgeLibrary` asked for:

`resource_path("hgpt_ai_os/topic_engine/engineering_knowledge_playbooks.json")`

In source mode, `resource_root()` returned the repository root:

`/Users/macos/Desktop/HGPT_AI_OS_CLEAN`

That made the JSON path resolve incorrectly to:

`/Users/macos/Desktop/HGPT_AI_OS_CLEAN/hgpt_ai_os/topic_engine/engineering_knowledge_playbooks.json`

The actual source-layout resource is:

`/Users/macos/Desktop/HGPT_AI_OS_CLEAN/src/hgpt_ai_os/topic_engine/engineering_knowledge_playbooks.json`

## Files Changed

- `src/hgpt_ai_os/core/resource_path.py`
- `RESOURCE_PATH_FIX_REPORT.md`

No engineering knowledge JSON, playbooks, generated content, routing, GUI, runtime generation logic, or packaging source was modified by this fix.

## Fix

`resource_path()` now keeps the existing frozen/resource-root behavior, first checks the original root-relative path, and in non-frozen source mode falls back to `repo/src/<relative>` when that file exists.

This preserves repo-root resources such as `templates/` and `knowledge/`, while allowing package resources under `src/hgpt_ai_os/...` to resolve correctly in unit tests and source runs.

## Verification

### Source Resource Resolution

Command:

`PYTHONPATH=src PYTHONPYCACHEPREFIX=/private/tmp/lucid_pycache python3 - <<'PY' ...`

Result:

- `hgpt_ai_os/topic_engine/engineering_knowledge_playbooks.json` resolves to `src/hgpt_ai_os/topic_engine/engineering_knowledge_playbooks.json`
- `templates/facebook/default.md` resolves to `templates/facebook/default.md`
- `knowledge/cases/QAQC_001.md` resolves to `knowledge/cases/QAQC_001.md`
- `EngineeringKnowledgeLibrary().all()` loads successfully with 7 playbooks

### Focused Import/Resource Tests

The previous import/resource-path blocker is resolved. The focused test set no longer raises `FileNotFoundError` for:

`/Users/macos/Desktop/HGPT_AI_OS_CLEAN/hgpt_ai_os/topic_engine/engineering_knowledge_playbooks.json`

### Runtime DOCX Generation

Command:

`production.build_outputs(999, "AWS D1.1", open_output_folder=False)`

Result:

Runtime generated exactly 7 DOCX files:

- `approval_checklist.docx`
- `facebook.docx`
- `hashtags.docx`
- `image_prompt.docx`
- `seo.docx`
- `tiktok.docx`
- `video_prompt.docx`

### Frozen JSON Resource Smoke

Frozen-mode smoke checks loaded all topic-engine JSON resources from the current built artifacts:

- `dist/LUCID/_internal/hgpt_ai_os/topic_engine/engineering_knowledge_playbooks.json`
- `dist/LUCID/_internal/hgpt_ai_os/topic_engine/failure_intelligence_library.json`
- `dist/LUCID/_internal/hgpt_ai_os/topic_engine/topic_intelligence_profiles.json`
- `dist/LUCID.app/Contents/Resources/hgpt_ai_os/topic_engine/engineering_knowledge_playbooks.json`
- `dist/LUCID.app/Contents/Resources/hgpt_ai_os/topic_engine/failure_intelligence_library.json`
- `dist/LUCID.app/Contents/Resources/hgpt_ai_os/topic_engine/topic_intelligence_profiles.json`

Note: older `release/Mac/...` app artifacts are stale and do not contain `engineering_knowledge_playbooks.json`; the current `dist` frozen artifacts do contain and load all three JSON resources.

## Final Unittest Summary

Command:

`PYTHONPATH=src PYTHONPYCACHEPREFIX=/private/tmp/lucid_pycache python3 -m unittest discover -s tests`

Final result after the path fix:

- Ran: 134
- Failures: 9
- Errors: 0
- Skipped: 0

The remaining failures are not import/resource-path failures. They are out-of-scope content/knowledge assertion failures in `tests/test_topic_engine.py`, grouped under:

- `test_conveyor_belt_misalignment_routes_before_shotblast_and_uses_conveyor_knowledge`
- `test_conveyor_knowledge_contains_required_tracking_concepts`
- `test_release_blocker_engineering_documents_are_chief_engineer_quality` subtests

Those failures correspond to content expectations such as missing English terms (`belt tracking`, `head pulley`, `blast wheel`, `header`) while the working tree already contains dirty topic-engine/content files. They were not changed because this task explicitly forbids modifying engineering knowledge, playbooks, generated content, routing, GUI, or runtime behavior beyond path resolution.

## Freeze Readiness

The resource-path blocker is fixed and frozen/source resource loading is verified. The repository is not fully green yet because the existing dirty content changes still leave 9 content assertion failures outside the allowed scope of this final resource-path fix.
