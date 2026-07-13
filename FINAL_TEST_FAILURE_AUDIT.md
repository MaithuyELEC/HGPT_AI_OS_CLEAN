# Final Test Failure Audit

Repository: `/Users/macos/Desktop/HGPT_AI_OS_CLEAN`

Verification command:

```bash
python3 -m unittest discover -s tests
```

Observed result:

```text
Ran 134 tests
FAILED (failures=9)
Errors 0
```

No production code was modified for this audit.

## Failure 1

- Test name: `test_conveyor_belt_misalignment_routes_before_shotblast_and_uses_conveyor_knowledge`
- File: `tests/test_topic_engine.py`
- Line: 483
- Expected: generated SEO output contains English snapshot term `belt tracking`
- Actual: generated SEO output is Vietnamese-first conveyor content containing `độ lệch băng tải`, `căn chỉnh tang`, `căn chỉnh con lăn`, `bộ căng băng`, `mối nối băng tải`, `ổ lăn`, `độ đảo trục`, and `gạt làm sạch`
- Category: A. Snapshot/content expectation only
- Root cause: the test still asserts the older English terminology snapshot for conveyor tracking concepts. The actual output routes correctly to `CONVEYOR_BELT_MISALIGNMENT` and contains the equivalent localized engineering concepts without leaking shotblast-wheel concepts.

## Failure 2

- Test name: `test_conveyor_knowledge_contains_required_tracking_concepts`
- File: `tests/test_topic_engine.py`
- Line: 526
- Expected: serialized conveyor playbook contains English snapshot term `head pulley`
- Actual: serialized playbook contains localized conveyor terminology such as `tang chủ động`, `tang bị động`, `con lăn đỡ tải`, `con lăn hồi`, `bộ căng băng`, `mối nối băng tải`, `lực căng băng`, `căn chỉnh con lăn`, `căn chỉnh tang`, `ổ lăn`, `độ đảo trục`, and `gạt làm sạch`
- Category: A. Snapshot/content expectation only
- Root cause: the data contract has shifted to Vietnamese-first playbook content. The assertion still expects English storage terms even though the current localized playbook preserves the intended conveyor engineering concepts.

## Failure 3

- Test name: `test_engineering_writer_v3_generates_release_topics_from_structured_knowledge` subtest `topic='Cầu trục đứt cáp'`
- File: `tests/test_topic_engine.py`
- Line: 559
- Expected: generated SEO output contains English measurement phrase `broken wire count`
- Actual: generated SEO output is Vietnamese-first crane wire-rope RCA content containing `ISO 4309`, `cáp tải`, `puly`, `tang cuốn`, and Vietnamese inspection/measurement language
- Category: A. Snapshot/content expectation only
- Root cause: the test still checks an old English measurement phrase after localization. The output remains engineering-specific and includes the required crane/wire-rope context, but the phrase is no longer rendered in English.

## Failure 4

- Test name: `test_engineering_writer_v3_generates_release_topics_from_structured_knowledge` subtest `topic='SAW undercut'`
- File: `tests/test_topic_engine.py`
- Line: 559
- Expected: generated SEO output contains English measurement phrase `undercut depth`
- Actual: generated SEO output is Vietnamese-first SAW undercut RCA content containing `ISO 5817`, `SAW`, `khuyết cạnh`, `cháy cạnh`, `stickout`, and Vietnamese inspection/measurement language
- Category: A. Snapshot/content expectation only
- Root cause: the assertion has not been localized. The output is still the correct engineering topic and mechanism, but the old English measurement phrase is replaced by Vietnamese technical wording.

## Failure 5

- Test name: `test_engineering_writer_v3_generates_release_topics_from_structured_knowledge` subtest `topic='Shotblast conveyor lỗi'`
- File: `tests/test_topic_engine.py`
- Line: 559
- Expected: generated SEO output contains English measurement phrase `surface profile`
- Actual: generated SEO output is Vietnamese-first shotblast conveyor content containing `ISO 8501-1`, `biên dạng`, `bánh văng bi`, `bộ phân ly`, `rung`, and surface-preparation context
- Category: A. Snapshot/content expectation only
- Root cause: the test expects a legacy English phrase while the output now renders the surface-preparation measurement in Vietnamese. The engineering output is topical and not a wrong-domain result.

## Failure 6

- Test name: `test_engineering_writer_v3_generates_release_topics_from_structured_knowledge` subtest `topic='Máy nén khí áp thấp'`
- File: `tests/test_topic_engine.py`
- Line: 559
- Expected: generated SEO output contains English measurement phrase `pressure decay`
- Actual: generated SEO output is Vietnamese-first compressed-air RCA content containing `ISO 8573`, `áp suất`, `đường ống góp`, `lọc tách dầu`, `load-unload`, and Vietnamese pressure-loss/check language
- Category: A. Snapshot/content expectation only
- Root cause: the assertion is still anchored to pre-localization English wording. The generated content keeps the correct low-pressure compressor diagnosis path and equivalent localized measurement language.

## Failure 7

- Test name: `test_engineering_writer_v3_generates_release_topics_from_structured_knowledge` subtest `topic='Lỗi bong tróc sơn'`
- File: `tests/test_topic_engine.py`
- Line: 560
- Expected: generated SEO output contains English mechanism phrase `adhesion`
- Actual: generated SEO output is Vietnamese-first coating failure RCA content containing `ISO 8503`, `dew point`, `độ bám dính`, `biên dạng phun bi`, `DFT`, and coating repair/verification context
- Category: A. Snapshot/content expectation only
- Root cause: the expected English phrase was localized to Vietnamese engineering terminology. The actual content still covers the intended coating adhesion mechanism through `độ bám dính`.

## Failure 8

- Test name: `test_release_blocker_engineering_documents_are_chief_engineer_quality` subtest `topic='Phun bi tự động gãy cánh đẩy'`
- File: `tests/test_topic_engine.py`
- Line: 423
- Expected: generated Facebook output contains English equipment phrase `blast wheel`
- Actual: generated Facebook output is Vietnamese-first shotblast failure content containing `bánh văng bi`, `cánh đẩy`, `lồng định hướng`, `tấm lót`, `hạt bi`, `rung`, `motor`, and verification steps
- Category: A. Snapshot/content expectation only
- Root cause: the test still expects the English equipment term after Vietnamese-first localization. The actual output is not generic and uses the correct localized shotblast equipment vocabulary.

## Failure 9

- Test name: `test_release_blocker_engineering_documents_are_chief_engineer_quality` subtest `topic='Máy nén khí áp thấp'`
- File: `tests/test_topic_engine.py`
- Line: 423
- Expected: generated Facebook output contains English equipment phrase `header`
- Actual: generated Facebook output is Vietnamese-first compressed-air content containing `đường ống góp`, `áp outlet`, `leak`, `pressure decay` equivalent wording through pressure-loss checks, `lọc tách dầu`, and `load-unload`
- Category: A. Snapshot/content expectation only
- Root cause: the assertion still requires the English term `header`, while the localized output renders the same compressed-air distribution concept as `đường ống góp`. The content remains correct for the compressor low-pressure topic.

## Summary

Category A:

- 9 failures
- All failures are snapshot/content expectation differences caused by older English-term assertions after Vietnamese-first localization.
- Affected expectations: `belt tracking`, `head pulley`, `broken wire count`, `undercut depth`, `surface profile`, `pressure decay`, `adhesion`, `blast wheel`, and `header`.

Category B:

- 0 failures
- No failure shows wrong engineering output. The actual outputs remain topic-specific and contain the localized engineering equivalents.

Category C:

- 0 failures
- No failure indicates a behavioral regression in routing, generation, or domain selection.

Category D:

- 0 failures
- No failure indicates a logic bug. The failures are assertion-language mismatches, not broken execution logic.

READY FOR CODE FREEZE = YES
