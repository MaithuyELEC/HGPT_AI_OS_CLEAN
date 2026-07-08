from __future__ import annotations

import hashlib
import logging
import re
import time
from collections import deque
from dataclasses import dataclass
from typing import Any

from hgpt_ai_os.ai.config_resolver import is_free_desktop_mode
from hgpt_ai_os.ai.client import PROVIDER_UNAVAILABLE_MESSAGE
from hgpt_ai_os.ai.client import LucidAI
from hgpt_ai_os.ai.gemini_client import AIProviderError
from hgpt_ai_os.content.factory.builder_factory import BuilderFactory
from hgpt_ai_os.content.template_engine import TemplateEngine
from hgpt_ai_os.topic_engine import TopicIntelligenceEngine


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GenerationSpec:
    key: str
    content_type: str
    target_audience: str
    writing_goal: str
    format_notes: str
    reasoning_focus: str
    structure_options: tuple[str, ...]


_GENERATION_SPECS = {
    "facebook": GenerationSpec(
        key="facebook",
        content_type="Facebook engineering post",
        target_audience="steel fabrication and construction site engineers, QC teams, supervisors",
        writing_goal="educate readers with a practical field problem, risks, corrective action, and inspection checklist",
        format_notes="Write in Vietnamese. Use a strong hook, short sections, practical bullet points, and a clear CTA.",
        reasoning_focus="field consequence, root cause, decision points, inspection evidence, corrective workflow",
        structure_options=(
            "open with a site observation, then diagnose causes, then give controls and reviewer checks",
            "open with a risky decision, then contrast wrong vs right practice, then close with action steps",
            "open with a measured symptom, then explain why it matters, then provide a prevention sequence",
        ),
    ),
    "tiktok": GenerationSpec(
        key="tiktok",
        content_type="TikTok short video script",
        target_audience="site engineers, foremen, QC inspectors, and steel construction crews",
        writing_goal="turn the topic into a concise educational short-video script with visual beats and spoken lines",
        format_notes="Write in Vietnamese. Include hook, scene-by-scene shots, voiceover, captions, and CTA.",
        reasoning_focus="visual symptom, first three seconds, demonstration sequence, spoken explanation, field takeaway",
        structure_options=(
            "open with a camera-visible defect, then move through three quick shots and a final field rule",
            "open with a question to the crew, then show inspection, correction, and approval beats",
            "open with a before/after contrast, then explain the hidden risk and the practical fix",
        ),
    ),
    "image": GenerationSpec(
        key="image_prompt",
        content_type="Image generation prompt",
        target_audience="AI image model and industrial visual designer",
        writing_goal="describe a realistic engineering image that visualizes the topic accurately",
        format_notes="Write a production-ready prompt in English with subject, setting, technical details, camera, lighting, and exclusions.",
        reasoning_focus="visible subject, physical setting, measurable details, inspection context, visual exclusions",
        structure_options=(
            "compose from foreground subject to background context, then camera, lighting, and negative prompts",
            "compose from inspection action to material details, then environment, camera, and exclusions",
            "compose from problem evidence to corrective setup, then lens, mood, and prohibited artifacts",
        ),
    ),
    "video": GenerationSpec(
        key="video_prompt",
        content_type="Video generation prompt",
        target_audience="AI video model and industrial video producer",
        writing_goal="describe a cinematic technical sequence that explains the field issue and correction workflow",
        format_notes="Write a production-ready prompt in English with duration, shot sequence, motion, inspection actions, and safety mood.",
        reasoning_focus="sequence logic, motion, inspection handoff, correction workflow, final verification",
        structure_options=(
            "sequence from establishing shot to close-up evidence, correction action, and final sign-off",
            "sequence from unsafe assumption to measurement, team response, and approved condition",
            "sequence from material detail to human inspection, tool movement, and resolved outcome",
        ),
    ),
    "seo": GenerationSpec(
        key="seo",
        content_type="SEO article brief",
        target_audience="engineers, QA/QC teams, project managers, and technical buyers searching for steel construction guidance",
        writing_goal="create search-optimized educational content with keywords, title, meta description, outline, and FAQs",
        format_notes="Write in Vietnamese. Keep it distinct from social posts and focus on search intent and technical discoverability.",
        reasoning_focus="search intent, technical entities, practical questions, buyer/engineer concerns, answer hierarchy",
        structure_options=(
            "start from search intent, then title/meta, keyword clusters, outline, FAQs, and internal-link ideas",
            "start from reader problem, then keyword map, article promise, outline, FAQs, and conversion angle",
            "start from technical entity extraction, then SERP angle, headings, FAQs, and evidence needs",
        ),
    ),
    "checklist": GenerationSpec(
        key="checklist",
        content_type="Production approval checklist",
        target_audience="content reviewer, engineering reviewer, and QA/QC approver",
        writing_goal="verify technical accuracy, audience fit, channel fit, and production readiness",
        format_notes="Write in Vietnamese. Use checkbox bullets grouped by review area.",
        reasoning_focus="approval criteria, technical risk, channel readiness, evidence coverage, final release decision",
        structure_options=(
            "group checks by technical accuracy, channel fit, evidence, compliance, and final approval",
            "group checks by topic relevance, risk controls, visual assets, review workflow, and release readiness",
            "group checks by reviewer role: engineering, QA/QC, marketing, production, and approver",
        ),
    ),
}


_TOPIC_STOPWORDS = {
    "a",
    "an",
    "and",
    "at",
    "by",
    "for",
    "from",
    "in",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
    "ai",
    "và",
    "của",
    "cho",
    "khi",
    "tại",
    "trong",
    "ngoài",
    "so",
    "với",
    "về",
    "là",
    "các",
    "một",
    "những",
}


_OPENING_MOVES = (
    "start from visible evidence on site",
    "start from the decision a supervisor must make",
    "start from a measurement that changes the risk level",
    "start from the hidden cost of accepting the condition",
    "start from a crew-level misconception",
)

_BODY_PROGRESSIONS = (
    "symptom -> cause -> risk -> control -> verification",
    "observation -> wrong assumption -> technical check -> correction -> approval",
    "field condition -> engineering implication -> decision criteria -> action sequence",
    "failure signal -> root-cause questions -> inspection evidence -> prevention rule",
    "reader intent -> practical answer -> evidence needs -> next action",
)

_EVIDENCE_RHYTHMS = (
    "use measured facts before recommendations",
    "separate visual clues from acceptance criteria",
    "pair each risk with one verification action",
    "move from general implication to specific field check",
    "make the final step a release or hold decision",
)


class PromptBuilder:
    def build(
        self,
        topic: str,
        context: str,
        spec: GenerationSpec,
        variation: str,
        sequence_number: int,
        retry_note: str = "",
    ) -> str:
        reference = self._knowledge_pack(context)
        semantic_brief = self._semantic_brief(topic)
        structure = self._structure(spec, variation, sequence_number)
        retry_block = f"\nRevision Constraint:\n{retry_note}\n" if retry_note else ""

        return f"""Topic:
{topic}

Output Key:
{spec.key}

Content Type:
{spec.content_type}

Target Audience:
{spec.target_audience}

Semantic Brief:
{semantic_brief}

Reasoning Focus:
{spec.reasoning_focus}

Writing Goal:
{spec.writing_goal}

Knowledge Injection:
{reference}

Narrative Shape:
{structure}

Diversity Control:
- Variation token: {variation}
- Generation sequence: {sequence_number}
- Create a new hook, new paragraph order, and new section logic for this output.
- Do not reuse the opening angle, first paragraph, heading order, or bullet rhythm from another output.
- Treat Facebook, TikTok, Image, Video, SEO, and Checklist as separate deliverables with separate reasoning paths.
{retry_block}
Instructions:
- Generate original final content only.
- Reason from the topic semantics before writing; do not fill a preset template.
- Use only the topic, AI reasoning, and retrieved knowledge context.
- Do not invent citations or claim retrieved knowledge exists when it is empty.
- Do not copy retrieved context verbatim unless a short quoted phrase is necessary.
- Keep this output independent from the other output types.
- {spec.format_notes}
"""

    def _knowledge_pack(self, context: str) -> str:
        reference = context.strip()
        if not reference:
            return "No relevant knowledge was retrieved. Use topic semantics and general engineering reasoning only."

        return (
            "Use these retrieved notes as evidence, not as copy-ready prose. "
            "Extract only the details that are relevant to this exact topic.\n\n"
            f"{reference}"
        )

    def _semantic_brief(self, topic: str) -> str:
        terms = self._topic_terms(topic)
        if not terms:
            return "No strong topic terms detected; infer the practical problem, audience, risk, and action from the full topic."

        return "\n".join(
            [
                f"- Core terms: {', '.join(terms[:8])}",
                "- Infer the practical object, failure mode, process stage, risk, and required decision from those terms.",
                "- Prefer topic-specific angles over generic manufacturing advice.",
            ]
        )

    def _topic_terms(self, topic: str) -> list[str]:
        words = re.findall(r"[\wÀ-ỹ]+", (topic or "").lower())
        terms = []
        for word in words:
            if len(word) < 3 or word in _TOPIC_STOPWORDS:
                continue
            if word not in terms:
                terms.append(word)
        return terms

    def _structure(
        self,
        spec: GenerationSpec,
        variation: str,
        sequence_number: int,
    ) -> str:
        options = spec.structure_options
        if not options:
            return "Choose the structure that best fits the topic and output type."

        seed = int(variation[:8], 16)
        ordinal = max(sequence_number - 1, 0)
        primary = options[(seed + sequence_number) % len(options)]
        opening = _OPENING_MOVES[ordinal % len(_OPENING_MOVES)]
        progression = _BODY_PROGRESSIONS[
            (ordinal // len(_OPENING_MOVES)) % len(_BODY_PROGRESSIONS)
        ]
        evidence = _EVIDENCE_RHYTHMS[
            (ordinal // (len(_OPENING_MOVES) * len(_BODY_PROGRESSIONS)))
            % len(_EVIDENCE_RHYTHMS)
        ]

        return "\n".join(
            [
                f"- Primary shape: {primary}",
                f"- Opening move: {opening}",
                f"- Body progression: {progression}",
                f"- Evidence rhythm: {evidence}",
            ]
        )


class ContentGenerator:
    _recent_openings: deque[str] = deque(maxlen=80)
    _recent_structures: deque[str] = deque(maxlen=80)

    def __init__(self, ai: LucidAI | None = None):
        self.template = TemplateEngine()
        self.free_desktop_mode = ai is None and is_free_desktop_mode()
        self.ai = ai if ai is not None else None
        if self.ai is None and not self.free_desktop_mode:
            self.ai = LucidAI()
        self.prompt_builder = PromptBuilder()
        self.topic_engine = TopicIntelligenceEngine()
        self._last_topic = ""
        self._last_context = ""
        self._generation_sequence = 0
        self._run_variation = self._new_variation("run")

    def generate(self, platform: str, topic: str, context: str = ""):
        if topic:
            self._last_topic = topic
            self._last_context = context

        content_key = self._normalize_platform(platform)
        spec = _GENERATION_SPECS.get(content_key)

        if spec is None:
            spec = self._custom_spec(content_key or platform)

        self._generation_sequence += 1
        variation = self._new_variation(
            f"{self._run_variation}:{spec.key}:{topic}:{self._generation_sequence}"
        )
        prompt = self._build_prompt(topic, context, spec, variation)
        if self.free_desktop_mode:
            return self._generate_with_builtin(spec, topic, context)
        return self._generate_with_llm(prompt, spec, topic, context, variation)

    def generate_facebook(self, topic, context=""):
        return self.generate("facebook", topic, context)

    def generate_tiktok(self, topic, context=""):
        return self.generate("tiktok", topic, context)

    def generate_image_prompt(self, topic, context=""):
        return self.generate("image", topic, context)

    def generate_video_prompt(self, topic, context=""):
        return self.generate("video", topic, context)

    def generate_hashtags(self, topic="", context=""):
        topic = topic or self._last_topic
        context = context or self._last_context

        if topic:
            logger.info("Free Desktop Mode using built-in generator for hashtags")
            return BuilderFactory.create("hashtags").build(topic, context)

        return self.template.render(
            "templates/content/hashtags.md",
            {},
        )

    def generate_checklist(self, topic="", context=""):
        topic = topic or self._last_topic
        context = context or self._last_context

        if not topic:
            return self.template.render(
                "templates/content/checklist.md",
                {},
            )

        return self.generate("checklist", topic, context)

    def generate_seo(self, topic, context=""):
        return self.generate("seo", topic, context)

    def _normalize_platform(self, platform: str) -> str:
        value = (platform or "").strip().lower().replace("_prompt", "")
        if value == "image prompt":
            return "image"
        if value == "video prompt":
            return "video"
        return value

    def _build_prompt(
        self,
        topic: str,
        context: str,
        spec: GenerationSpec,
        variation: str | None = None,
        retry_note: str = "",
    ) -> str:
        return self.prompt_builder.build(
            topic=topic,
            context=context,
            spec=spec,
            variation=variation or self._run_variation,
            sequence_number=self._generation_sequence,
            retry_note=retry_note,
        )

    def _generate_with_llm(
        self,
        user_prompt: str,
        spec: GenerationSpec,
        topic: str,
        context: str,
        variation: str,
    ) -> str:
        system_prompt = (
            "You are LUCID AUTO's AI content engine for steel fabrication, "
            "construction QA/QC, site engineering, and industrial marketing. "
            "Generate practical, technically grounded final content. "
            "Every deliverable must use independent reasoning, an original opening, "
            "and a channel-specific structure."
        )
        for attempt in range(2):
            response = self.ai.generate(system_prompt, user_prompt)

            if isinstance(response, AIProviderError):
                logger.info(
        "AI unavailable for %s, switching to built-in generator.",
        spec.key,
    )
                return self._generate_with_builtin(spec, topic, context)

            content = getattr(response, "content", "") or ""
            metadata: dict[str, Any] = getattr(response, "metadata", {}) or {}

            if metadata.get("mock"):
                logger.info(
                    "Mock provider detected for %s, switching to built-in generator.",
                     spec.key,
    )
                return self._generate_with_builtin(spec, topic, context)

            final_text = self._validate_response(content)
            if not final_text:
               logger.info(
                   "Empty AI response for %s, switching to built-in generator.",
        spec.key,
    )
               return self._generate_with_builtin(spec, topic, context)

            if self._is_duplicate_shape(final_text) and attempt == 0:
                retry_variation = self._new_variation(f"{variation}:retry")
                user_prompt = self._build_prompt(
                    topic,
                    context,
                    spec,
                    retry_variation,
                    "The previous draft reused an opening or body structure. "
                    "Rewrite with a different first paragraph, section order, "
                    "and progression of ideas.",
                )
                continue

            self._remember_shape(final_text)
            return final_text

        self._remember_shape(final_text)
        return final_text

    def _generate_with_builtin(
        self,
        spec: GenerationSpec,
        topic: str,
        context: str,
    ) -> str:
        logger.info("Using offline topic intelligence engine for %s", spec.key)
        return self.topic_engine.generate(topic, spec.key, context)

    def _builtin_fallback(
        self,
        spec: GenerationSpec,
        topic: str,
        context: str,
    ) -> str:
        reference = context.strip() or "No local knowledge context was retrieved."
        return "\n".join(
            [
                spec.content_type,
                "",
                f"Topic: {topic}",
                "",
                spec.writing_goal,
                "",
                "Local knowledge:",
                reference,
            ]
        )

    def _validate_response(self, content: str) -> str:
        return content.strip()

    def _is_duplicate_shape(self, content: str) -> bool:
        opening = self._opening_fingerprint(content)
        structure = self._structure_fingerprint(content)
        return opening in self._recent_openings or structure in self._recent_structures

    def _remember_shape(self, content: str) -> None:
        opening = self._opening_fingerprint(content)
        structure = self._structure_fingerprint(content)
        if opening:
            self._recent_openings.append(opening)
        if structure:
            self._recent_structures.append(structure)

    def _opening_fingerprint(self, content: str) -> str:
        paragraphs = [
            line.strip()
            for line in re.split(r"\n\s*\n", content.strip())
            if line.strip()
        ]
        opening = paragraphs[0] if paragraphs else content.strip()
        return self._fingerprint(opening[:320])

    def _structure_fingerprint(self, content: str) -> str:
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        markers = []
        for line in lines[:24]:
            if re.match(r"^(#{1,6}\s+|[-*]\s+|\d+[\).]\s+|\[[ xX]\]\s+)", line):
                markers.append("list:" + self._line_signature(line))
            elif line.endswith(":") or len(line) <= 48:
                markers.append("heading:" + self._line_signature(line))
            else:
                markers.append("paragraph:" + self._paragraph_shape(line))
        return self._fingerprint("|".join(markers))

    def _line_signature(self, line: str) -> str:
        normalized = re.sub(r"\s+", " ", line.lower()).strip()
        normalized = re.sub(r"\d+", "0", normalized)
        words = re.findall(r"[\wÀ-ỹ]+", normalized)
        return "-".join(words[:6])

    def _paragraph_shape(self, line: str) -> str:
        words = re.findall(r"[\wÀ-ỹ]+", line.lower())
        bucket = min(len(words) // 12, 8)
        signature = "-".join(words[:5])
        return f"{bucket}:{signature}"

    def _fingerprint(self, value: str) -> str:
        normalized = re.sub(r"\s+", " ", value.strip().lower())
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def _new_variation(self, value: str) -> str:
        seed = f"{value}:{time.time_ns()}"
        return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]

    def _failure_message(self, error: AIProviderError) -> str:
        logger.error(
            "AI generation failed: provider=%s model=%s type=%s retryable=%s message=%s metadata=%s",
            error.provider,
            error.model,
            error.error_type,
            error.retryable,
            error.message,
            error.metadata,
        )
        if error.error_type == "configuration_error":
            return PROVIDER_UNAVAILABLE_MESSAGE

        return (
            "AI provider encountered an error while generating content. "
            "Please check network, SSL, and provider configuration, then try again."
        )

    def _custom_spec(self, platform: str) -> GenerationSpec:
        content_type = f"{platform} content".strip()
        return GenerationSpec(
            key=platform,
            content_type=content_type,
            target_audience="the requested audience",
            writing_goal="generate the requested content from the topic and retrieved context",
            format_notes="Match the requested output type.",
            reasoning_focus="topic semantics, audience needs, channel fit, retrieved evidence, original structure",
            structure_options=(
                "choose a structure that fits the requested output type and differs from prior outputs",
            ),
        )
