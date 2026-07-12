# Topic Intelligence Engine

Release Candidate v1.0 introduces a structured topic-intelligence layer before knowledge search and content generation.

## Flow

User topic

-> `TopicIntelligenceEngine.analyze()`

-> `TopicContext`

-> `KnowledgeSearch`

-> playbook selection

-> content generator

## TopicContext

`TopicContext` is the source of truth for downstream generation. It carries:

- `domain`
- `intent`
- `entities`
- `equipment`
- `components`
- `materials`
- `processes`
- `failures`
- `severity`
- `standards`
- `confidence`
- `knowledge_query`
- `playbook_key`

The generator can be primed with this context by calling `ContentGenerator.prime_topic_context(context)`. Production does this once per topic, then all output channels reuse the same context.

## Data-Driven Profiles

Profiles live in:

`src/hgpt_ai_os/topic_engine/topic_intelligence_profiles.json`

The profile file contains entity aliases, failure aliases, intent signals, standards, severity rules, and playbook selectors. New entities, failures, standards, and playbook routing rules should be added there first. Code changes are only needed when a new extractor capability is required, not when adding normal vocabulary.

## Knowledge Search

Knowledge search no longer depends on the raw topic string alone. `TopicContext.to_topic_analysis()` builds a structured retrieval query from:

equipment + component + material + process + failure + intent + standard

Example:

`Cáp cẩu trục bị đứt`

becomes:

`Crane Wire Rope Broken Troubleshooting`

## Playbook Selection

Playbook selection uses `TopicContext.playbook_key`. For the acceptance topic:

- equipment: `Crane`
- component: `Wire Rope`
- failure: `Broken`
- severity: `Critical`
- playbook: `WIRE_ROPE_FAILURE`

This selects the wire-rope failure playbook instead of the generic crane-noise or crane-maintenance path.
