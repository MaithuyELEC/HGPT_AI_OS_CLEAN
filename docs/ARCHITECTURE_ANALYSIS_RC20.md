# RC20-C True AI Content Engine

Project: `HGPT_AI_OS_CLEAN`

## Modified Files

- `src/hgpt_ai_os/content/generator.py`
- `src/hgpt_ai_os/knowledge/bundle.py`
- `src/hgpt_ai_os/knowledge/repository.py`
- `docs/ARCHITECTURE_ANALYSIS_RC20.md`

## Architecture Summary

`ContentGenerator` is now an AI orchestration boundary only.

Responsibilities:

1. Receive topic.
2. Receive optional retrieved knowledge context.
3. Build one prompt per output type.
4. Invoke the configured AI provider.
5. Validate the provider response.
6. Return structured content or a generic AI-unavailable fallback.

The generator no longer performs topic analysis, engineering rule matching, or offline engineering-content generation. Engineering knowledge is allowed to enter generation only through:

- AI provider reasoning.
- Retrieved knowledge context passed into the prompt.

Knowledge retrieval remains separate from generation. `KnowledgeBundle` trims retrieved packages into reference notes and never generates final content. `FileKnowledgeRepository` improves retrieval precision by filtering low-value search terms before selecting candidate knowledge packages.

## Prompt Independence

The following outputs are generated independently through separate prompt specs:

- Facebook
- TikTok
- Image prompt
- Video prompt
- SEO
- Checklist

Each prompt carries the topic, the output key, the content type, the audience, the writing goal, optional retrieved context, and format instructions.

## Fallback Behavior

If the AI provider returns an error, mock response, or empty response, the generator returns only a production-safe status block:

```text
Status:
AI unavailable

Topic:
<topic>

Retrieved Context:
<context>

Reason:
No AI provider available.
```

This fallback intentionally contains no engineering recommendation, diagnosis, checklist, repair method, topic-specific substitute, or QA/QC claim.

## Migration Notes

- Public generator methods are preserved: `generate`, `generate_facebook`, `generate_tiktok`, `generate_image_prompt`, `generate_video_prompt`, `generate_seo`, `generate_hashtags`, and `generate_checklist`.
- GUI, packaging, exporter, and production service boundaries are unchanged.
- Existing static hashtag rendering is preserved for backward compatibility because hashtags are not one of the RC20-C required AI output types.
- Checklist generation remains backward-compatible. When called after topic-based generation, it uses the last topic and context; when called without any topic, it preserves the previous static-template behavior.
- Unknown `generate(platform, topic, context)` platforms still return content through the AI provider using a generic prompt spec instead of legacy template builders.

## Validation Checklist

- [ ] `generator.py` contains no topic-specific engineering rules.
- [ ] `generator.py` contains no hard-coded topic branches such as `if "bulong"`, `if "fit-up"`, `if "paint"`, or similar.
- [ ] `generator.py` contains no offline engineering article, SEO, image, video, or checklist templates.
- [ ] Facebook, TikTok, image prompt, video prompt, SEO, and checklist each build a distinct prompt.
- [ ] AI-unavailable behavior returns only the generic status block.
- [ ] Retrieved knowledge is included as context only and is not converted into generated content by the repository or bundle.
- [ ] GUI remains unchanged.
- [ ] Packaging remains unchanged.
- [ ] Exporter remains unchanged.

## Acceptance Topics

Use these inputs to confirm that engineering content comes only from AI reasoning or retrieved knowledge context:

- `Sai bulong neo tại hiện trường so với bản mã đế trụ`
- `Nứt mối hàn SAW`
- `Robot hàn AI`
- `ISO 3834`
- `Biến dạng dầm`
