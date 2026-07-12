# PATCH REPORT: Minimum Safe Patch for Crane Broken Routing

Date: 2026-07-12
Release: v1.0.0
Scope: root-cause patch only

## Files Modified

- `src/hgpt_ai_os/topic_engine/writers/channel_writer.py`
- `src/hgpt_ai_os/topic_engine/topic_intelligence_profiles.json`
- `tests/test_topic_engine.py`

## Functions Modified

### `channel_writer.py`

- Added `_fuzzy_confidence(playbook, haystack)`.
- Updated `match_playbook(topic, reasoning=None)`.

Change:
- When `reasoning.topic_context.playbook_key` is empty, fuzzy playbook selection is accepted only when confidence is at least `0.90`.
- Low-confidence partial token overlap now returns the existing generic engineering fallback playbook.

Why safe:
- Does not change writer architecture.
- Does not change channel writers, GUI, production, DOCX export, runtime, or AI provider code.
- Exact alias and complete match-group fuzzy matches still work.
- Partial overlap such as `cầu trục` no longer mutates `Broken` into `CRANE_NOISE`.

### `topic_intelligence_profiles.json`

- Added structured `CRANE_NOISE` selector for `Crane + Noise/Vibration`.
- Added minimal `CRANE_GENERAL_FAILURE` playbook for `Crane + Broken/Cracked` when no component is identified.

Change:
- `Cầu trục 7.5T bị đứt` now analyzes as:
  - Equipment: `Crane`
  - Failure: `Broken`
  - Component: none
  - Playbook: `CRANE_GENERAL_FAILURE`
  - Knowledge query: `Crane Broken Troubleshooting`

Why safe:
- Uses the existing JSON profile mechanism.
- Does not infer `Wire Rope`, `Motor`, or `Gearbox`.
- Keeps `WIRE_ROPE_FAILURE` for explicit wire-rope topics.
- Keeps noise/vibration topics on `CRANE_NOISE`.
- The new general crane failure playbook is neutral and requires evidence before naming a failed component.

### `tests/test_topic_engine.py`

- Added regression coverage for the release-blocking crane routing cases.
- Added writer fallback coverage for empty `TopicContext.playbook_key` plus low-confidence fuzzy overlap.

Why safe:
- Tests only the bug boundary described in `ROOT_CAUSE_REPORT.md`.
- Does not add new production behavior beyond preventing the confirmed misroute.

## Regression Results

Focused regression command:

```text
PYTHONPATH=src PYTHONPYCACHEPREFIX=/tmp/lucid_pycache python3 -m unittest \
  tests.test_topic_engine.TopicEngineTests.test_crane_failure_routing_does_not_mutate_unknown_failure_to_noise \
  tests.test_topic_engine.TopicEngineTests.test_empty_context_playbook_uses_generic_reasoning_for_low_confidence_fuzzy_match \
  tests.test_topic_engine.TopicEngineTests.test_final_topic_context_acceptance_cases \
  tests.test_topic_engine.TopicEngineTests.test_wire_rope_failure_output_uses_context_playbook_not_crane_noise
```

Result:

```text
Ran 4 tests in 1.337s
OK
```

Full regression command:

```text
PYTHONPATH=src PYTHONPYCACHEPREFIX=/tmp/lucid_pycache python3 -m unittest discover -s tests
```

Result:

```text
Ran 127 tests in 9.886s
OK
```

Manual analyzer readback:

```text
Cầu trục 7.5T bị đứt | playbook=CRANE_GENERAL_FAILURE | query=Crane Broken Troubleshooting | components=()
Cầu trục bị gãy | playbook=CRANE_GENERAL_FAILURE | query=Crane Broken Troubleshooting | components=()
Cầu trục bị nứt | playbook=CRANE_GENERAL_FAILURE | query=Crane Cracked Troubleshooting | components=()
Cầu trục rung | playbook=CRANE_NOISE | query=Crane Vibration Troubleshooting | components=()
Cầu trục kêu | playbook=CRANE_NOISE | query=Crane Noise Troubleshooting | components=()
Cáp cẩu trục bị đứt | playbook=WIRE_ROPE_FAILURE | query=Crane Wire Rope Broken Troubleshooting | components=('Wire Rope',)
```

## Scope Confirmation

- No architecture refactor.
- No Topic Engine rewrite.
- No GUI change.
- No Production pipeline change.
- No DOCX exporter change.
- No Runtime change.
- No AI Provider change.
