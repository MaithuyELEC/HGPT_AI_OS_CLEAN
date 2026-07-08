# Free Generator Quality Fix

## Scope

Free Desktop Mode now uses a topic-aware built-in generator for the seven exported content files:

- `facebook.docx`
- `tiktok.docx`
- `video_prompt.docx`
- `image_prompt.docx`
- `seo.docx`
- `hashtags.docx`
- `approval_checklist.docx`

No provider API key is required, and the generator does not create remote AI calls.

## Topic Classification

The built-in generator classifies the entered topic into one of these domains:

- 5S / kaizen / lean
- welding / SAW / MIG / fit-up
- painting / blasting / coating
- maintenance / motor / compressor / machine fault
- QAQC / inspection / NCR / checklist
- general manufacturing

Each domain provides topic-specific workshop objects, risks, causes, signs, actions, and hashtags. Output content is then composed from the topic and the detected domain rather than from a fixed placeholder template.

## Quality Rules

- Final body text must stay relevant to the requested topic.
- Retrieved context is not copied into the final content as raw reference notes.
- Unrelated defect examples are not inserted into unrelated topics.
- Required brand hashtags are preserved, with topic-specific hashtags appended.
