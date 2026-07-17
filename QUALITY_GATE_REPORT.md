# Quality Gate Report

## Gate Location

The engineering quality gate is implemented in `src/hgpt_ai_os/engineering_pipeline/quality_gate.py`.

## Record Rejection Rules

The gate rejects an EngineeringRecord when any required engineering substance is missing:

- no root causes
- no repair procedure
- no measurements
- no verification
- no lessons learned
- no engineering reasoning through failure mechanisms or decision logic

It also rejects generic or title-swapped records by scanning for generic phrases and checking that the engineering detail contains meaningful tokens beyond the topic title.

## Document Rejection Rules

After channel rendering, the gate checks that all generated documents are non-empty and that channel documents do not collapse into repeated generic text.

## Fabrication Controls

The AI reasoner prompt forbids invented standards and invented measurements. When source information is insufficient, the pipeline keeps unresolved data in `missing_information` and requires inspection/evidence items rather than allowing fabricated conclusions.

## Current Validation Result

Focused validation passed:

```text
PYTHONPATH=src PYTHONPYCACHEPREFIX=/tmp/lucid_pycache python3 -m unittest tests.test_engineering_pipeline_v2
Ran 2 tests in 15.038s
OK
```

Legacy topic-engine/playbook regression also passed after data-level compatibility anchors were preserved:

```text
PYTHONPATH=src PYTHONPYCACHEPREFIX=/tmp/lucid_pycache python3 -m unittest tests.test_topic_engine
Ran 29 tests in 16.422s
OK
```
