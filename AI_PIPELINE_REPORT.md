# AI Pipeline Report

## Implemented Pipeline

The production generator now uses `EngineeringGenerationPipeline` from `src/hgpt_ai_os/engineering_pipeline/pipeline.py`.

Pipeline stages:

```text
Topic
  -> Engineering topic intelligence
  -> Engineering classification
  -> Knowledge retrieval
  -> AI engineering reasoner
  -> EngineeringRecord
  -> Quality gate
  -> Seven record-only channel renderers
```

## AI-First Behavior

When a configured AI provider is available, the pipeline calls `LucidAI` with a strict EngineeringRecord JSON prompt. The system prompt requires:

- no generic paragraphs
- no repeated content
- no invented standards
- no invented measurements
- insufficient information returned as missing information and required inspection items

If the AI provider is unavailable or Free Desktop Mode is active, the local engineering reasoner builds a valid EngineeringRecord from topic intelligence, retrieved context, engineering playbooks, failure intelligence, standards, and profile heuristics. This preserves desktop operation without changing the GUI.

## Retrieval Inputs

The pipeline receives:

- `topic`
- retrieved knowledge context
- ranked `KnowledgeResult` items
- structured `TopicContext`

It selects the best available engineering playbook by `TopicContext.playbook_key` first, then by alias and match-group evidence from the engineering knowledge library.

## Regression Compatibility

Existing verified playbooks continue to participate through `EngineeringKnowledgeLibrary`. Known playbook-backed topics such as SAW porosity, wire rope failure, compressor low pressure, VFD overcurrent, gearbox failure, and shot blast failures still resolve through the existing library instead of being discarded.

