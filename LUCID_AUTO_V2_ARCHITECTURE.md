# LUCID AUTO V2 Architecture

## Mission

LUCID AUTO V2 replaces the prior playbook-first generation flow with a record-first AI Engineering Generation Pipeline while preserving the desktop product surface:

- macOS desktop application remains unchanged.
- Windows desktop application remains unchanged.
- GUI remains unchanged.
- User flow remains Enter Topic -> Generate -> 7 DOCX.
- DOCX export, PyInstaller, desktop packaging, channel filenames, and installer surfaces are not redesigned.

## Runtime Flow

```text
User Topic
  -> TopicAnalyzer / TopicIntelligenceEngine
  -> KnowledgeSearch / KnowledgeBundle
  -> EngineeringGenerationPipeline
  -> EngineeringRecord
  -> EngineeringQualityGate
  -> record-only channel writers
  -> existing DocxExporter
  -> 7 DOCX files
```

## Integration Boundary

The integration point is `src/hgpt_ai_os/production.py`. The legacy `ContentGenerator` call site is replaced by `EngineeringGenerationPipeline.generate_documents(...)` after the existing topic intelligence and knowledge retrieval steps have completed. The existing exporter still writes:

- `facebook.docx`
- `tiktok.docx`
- `image_prompt.docx`
- `video_prompt.docx`
- `seo.docx`
- `hashtags.docx`
- `approval_checklist.docx`

## Canonical Record

`src/hgpt_ai_os/engineering_pipeline/record.py` defines one canonical `EngineeringRecord`. It contains the requested engineering fields:

- Topic, Domain, Equipment, Subsystem, Component
- Failure Symptom, Operating Context, Working Principle
- Failure Mechanisms, Root Causes, Evidence Required
- Inspection Procedure, Measurements, Tools Required
- Decision Logic, Repair Procedure, Verification
- Acceptance Criteria, Lessons Learned, Common Mistakes
- Preventive Maintenance, Safety Controls, Kaizen
- Digital Factory Recommendations, Applicable Standards
- Missing Information, Confidence

## Knowledge Sources

The pipeline consumes the existing retrieval result and existing engineering knowledge library. It can incorporate:

- HGPT Knowledge through `KnowledgeSearch` / `KnowledgeBundle`
- Engineering playbooks through `EngineeringKnowledgeLibrary`
- Failure intelligence already attached to `TopicContext`
- Standards, SOP, checklist, and maintenance details carried by existing knowledge/playbook data

## Channel Rule

All seven channel writers render from `EngineeringRecord` only. They do not independently regenerate engineering conclusions.

