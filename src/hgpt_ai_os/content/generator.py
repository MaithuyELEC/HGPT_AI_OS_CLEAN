from __future__ import annotations

import hashlib
import logging
import re
import time
import unicodedata
from collections import deque
from dataclasses import dataclass
from typing import Any

from hgpt_ai_os.ai.config_resolver import validate_ai_provider_config
from hgpt_ai_os.ai.client import LucidAI
from hgpt_ai_os.ai.gemini_client import AIProviderError
from hgpt_ai_os.content.factory.builder_factory import BuilderFactory
from hgpt_ai_os.content.factory.general_domain import GeneralDomainRouter
from hgpt_ai_os.content.factory.topic_aware import TopicClassifier
from hgpt_ai_os.content.template_engine import TemplateEngine
from hgpt_ai_os.diagnostics import fallback, instrument_runtime_tracing, module_loaded, trace_call
from hgpt_ai_os.providers import ProviderManager
from hgpt_ai_os.topic_engine import (
    TopicContext,
    TopicIntelligenceEngine,
    compact_topic_context,
)


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
        content_type="Facebook educational post",
        target_audience="factory technicians, shift leaders, QA/QC, maintenance, and practical engineering readers on Facebook",
        writing_goal="transform engineering knowledge into a 900-1400 word senior-chief-engineer field story with hook, real shop scenario, root-cause analysis, practical workflow, lesson learned, and reader discussion",
        format_notes="Write in Vietnamese. Do not use report headings such as What is it, Why, Inspection, Measurement, Standards, Mô tả kỹ thuật ngắn, Nguyên nhân cần ưu tiên, or Trình tự kiểm tra thiết yếu. Use only these reader-facing sections: Hook, Real shop scenario, Root cause analysis, Practical solution, Lesson learned, Call To Action. Sound like a senior chief engineer speaking from factory experience, not an engineering report.",
        reasoning_focus="human shop-floor pain, danger, cause-and-effect engineering, technician workflow, prevention habit, discussion prompt",
        structure_options=(
            "open with pain or danger, enter a real factory scene, diagnose why it happened, then give a technician workflow and lesson",
            "open with a question from the shop floor, show a shift-level mistake, explain the root cause chain, then close with prevention",
            "open with a near-miss, follow the crew through evidence and repair, then ask readers how they would decide",
        ),
    ),
    "tiktok": GenerationSpec(
        key="tiktok",
        content_type="TikTok short video script",
        target_audience="the audience implied by the user's topic",
        writing_goal="turn the topic into a short viral TikTok script that moves through hook, curiosity, pain, useful information, twist, and action",
        format_notes="Write in Vietnamese. Use labels Mở đầu, Khơi tò mò, Nỗi đau, Thông tin, Cú twist, Kêu gọi hành động. Keep it around 150-250 words. Do not write a storyboard, shot plan, camera schedule, timestamps, or scene directions.",
        reasoning_focus="viral hook, curiosity gap, audience pain, one practical insight, twist, save/share action",
        structure_options=(
            "open with a camera-visible defect, then move through three quick shots and a final field rule",
            "open with a question to the crew, then show inspection, correction, and approval beats",
            "open with a before/after contrast, then explain the hidden risk and the practical fix",
        ),
    ),
    "image": GenerationSpec(
        key="image_prompt",
        content_type="Image generation prompt",
        target_audience="AI image model and visual designer",
        writing_goal="transform engineering knowledge into a clean visual-only prompt for Gemini image generation: subject, factory setting, visible action, motion, camera, lighting, composition, industrial realism, and visual exclusions",
        format_notes="Write a 350-700 word copy-paste-ready image prompt. Use DOCX-safe Vietnamese labels only: Chủ thể, Bối cảnh, Hành động chính, Chuyển động phụ, Góc máy, Ánh sáng, Vật liệu, Hiệu ứng công nghiệp, Bố cục, Phong cách hình ảnh, Chất lượng hình ảnh. Keep only visual information. Do not mention EngineeringRecord, missing data, unsupported numeric value, internal system messages, source records, hidden reasoning, report fields, or anything not useful for an image model.",
        reasoning_focus="visual subject identity, safe factory context, motion cues, camera/lens logic, lighting, material realism, composition, industrial visual exclusions",
        structure_options=(
            "compose from foreground subject to background context, then camera, lighting, and negative prompts",
            "compose from inspection action to material details, then environment, camera, and exclusions",
            "compose from problem evidence to corrective setup, then lens, mood, and prohibited artifacts",
        ),
    ),
    "video": GenerationSpec(
        key="video_prompt",
        content_type="Video generation prompt",
        target_audience="AI video model and video producer",
        writing_goal="transform engineering knowledge into a cinematic mini documentary video prompt with five scenes: strong hook, failure, diagnosis, repair, and result",
        format_notes="Write a production-ready mini documentary prompt, not a checklist and not one paragraph. Use DOCX-safe Vietnamese labels only: Tiêu đề, Thời lượng, Cảnh 1 - Hook, Cảnh 2 - Failure, Cảnh 3 - Diagnosis, Cảnh 4 - Repair, Cảnh 5 - Result, Kết thúc. Each scene must include camera movement, worker movement, machine movement, ambient sound, voice, and emotion. Do not mention EngineeringRecord, missing data, unsupported numeric value, internal system messages, source records, hidden reasoning, or report fields.",
        reasoning_focus="cinematic documentary arc, camera movement, worker movement, machine movement, ambient sound, narration, emotion, final proof",
        structure_options=(
            "sequence from establishing shot to close-up evidence, correction action, and final sign-off",
            "sequence from unsafe assumption to measurement, team response, and approved condition",
            "sequence from material detail to human inspection, tool movement, and resolved outcome",
        ),
    ),
    "seo": GenerationSpec(
        key="seo",
        content_type="SEO article",
        target_audience="readers searching for guidance on the user's topic",
        writing_goal="write a complete 1200-2000 word search article that transforms engineering knowledge into useful guidance with root cause, inspection, repair, acceptance, prevention, applicable standards, FAQ, and summary",
        format_notes="Write in Vietnamese. Use article structure: H1, Introduction, at least three H2 sections, FAQ, Summary. Include root cause, inspection, repair, acceptance, prevention, and applicable standards naturally. Use search keywords naturally. Do not output a knowledge database, engineering record, outline-only brief, or raw source notes.",
        reasoning_focus="search intent, root-cause explanation, inspection workflow, repair decisions, acceptance evidence, prevention, applicable standards, natural keywords",
        structure_options=(
            "start with search intent and shop-floor consequence, then explain causes, inspection, repair, acceptance, prevention, standards, FAQ, and summary",
            "start from reader problem, then move through diagnosis, repair workflow, pass/fail evidence, prevention system, standards, FAQ, and summary",
            "start from common symptoms, then build a complete how-to article with keywords embedded naturally in headings and answers",
        ),
    ),
    "checklist": GenerationSpec(
        key="checklist",
        content_type="Content approval checklist",
        target_audience="content reviewer, subject reviewer, and final approver",
        writing_goal="verify topic relevance, accuracy, clarity, practical value, audience fit, channel fit, visual fit, CTA, and readiness",
        format_notes="Write in Vietnamese. Use checkbox bullets grouped by review area.",
        reasoning_focus="approval criteria, technical risk, channel readiness, evidence coverage, final release decision",
        structure_options=(
            "group checks by topic relevance, accuracy, clarity, practical value, CTA, and final approval",
            "group checks by audience fit, visual assets, evidence, review workflow, and release readiness",
            "group checks by reviewer role: content, subject matter, marketing, visual, and approver",
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

_FORBIDDEN_OUTPUT_TERMS = (
    "Timeline",
    "Texture",
    "Engineering checklist",
    "Inspection item",
    "Acceptance criteria",
    "Responsible person",
    "Frequency",
    "Root Cause",
    "Problem",
    "Evidence",
    "Manager's job",
    "Quality release",
    "Schedule",
    "Hold the product",
    "The topic belongs to",
)

_BROKEN_VIETNAMESE_PATTERNS = (
    "Đ ng c",
    "đ ng c",
    "ki m tra",
    "b ng ch ng",
)

class PromptBuilder:
    def build(
        self,
        topic: str,
        context: str,
        spec: GenerationSpec,
        variation: str,
        sequence_number: int,
        topic_context: TopicContext | None = None,
        retry_note: str = "",
    ) -> str:
        reference = self._knowledge_pack(context)
        semantic_brief = (
            compact_topic_context(topic_context)
            if topic_context is not None
            else self._semantic_brief(topic)
        )
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
- Engineering Record is source material only. Transform it for the selected audience; never output it directly.
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

    def __init__(self, ai: LucidAI | None = None, provider_manager: ProviderManager | None = None):
        trace_call("Generator.__init__", self)
        self.template = TemplateEngine()
        validation = validate_ai_provider_config()
        self.free_desktop_mode = validation.config.free_desktop_mode or validation.status == "Free Desktop"
        self.ai = ai
        self.provider_manager = provider_manager or ProviderManager()
        if self.free_desktop_mode:
            logger.info("Mode: Offline Topic Intelligence")
        self.prompt_builder = PromptBuilder()
        self.topic_engine = TopicIntelligenceEngine()
        self._topic_context = None
        self.topic_classifier = TopicClassifier()
        self.general_router = GeneralDomainRouter()
        self._last_topic = ""
        self._last_context = ""
        self._generation_sequence = 0
        self._run_variation = self._new_variation("run")

    def prime_topic_context(self, topic_context: TopicContext) -> None:
        self._topic_context = topic_context

    def _get_topic_context(self, topic: str) -> TopicContext:
        if self._topic_context is not None and self._topic_context.original_topic == topic:
            return self._topic_context
        self._topic_context = self.topic_engine.analyze(topic)
        return self._topic_context

    def generate(self, platform: str, topic: str, context: str = ""):
        trace_call("Generator.generate", self, selected_topic=topic, writer_selected=platform)
        if topic:
            self._last_topic = topic
            self._last_context = context

        content_key = self._normalize_platform(platform)
        spec = _GENERATION_SPECS.get(content_key)

        if spec is None:
            spec = self._custom_spec(content_key or platform)

        self._generation_sequence += 1
        uses_general = self._uses_general_builder(topic) if topic else False
        topic_context = None if uses_general else self._get_topic_context(topic) if topic else None
        variation = self._new_variation(
            f"{self._run_variation}:{spec.key}:{topic}:{self._generation_sequence}"
        )
        prompt = self._build_prompt(topic, context, spec, variation, topic_context=topic_context)
        if self.free_desktop_mode:
            fallback("Free Desktop mode or AI provider unavailable; using built-in generator.")
            return self._generate_with_builtin(spec, topic, context, topic_context=topic_context)
        return self._generate_with_llm(prompt, spec, topic, context, variation, topic_context=topic_context)

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

        if topic and self._uses_general_builder(topic):
            return BuilderFactory.create("hashtags").build(topic, context)

        if topic:
            logger.info("Free Desktop Mode using built-in generator for hashtags")
            return self.topic_engine.generate(
                topic,
                "hashtags",
                context,
                topic_context=self._get_topic_context(topic),
            )

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
        topic_context: TopicContext | None = None,
        retry_note: str = "",
    ) -> str:
        return self.prompt_builder.build(
            topic=topic,
            context=context,
            spec=spec,
            variation=variation or self._run_variation,
            sequence_number=self._generation_sequence,
            topic_context=topic_context,
            retry_note=retry_note,
        )

    def _generate_with_llm(
        self,
        user_prompt: str,
        spec: GenerationSpec,
        topic: str,
        context: str,
        variation: str,
        topic_context: TopicContext | None = None,
    ) -> str:
        system_prompt = (
            "You are LUCID AUTO's AI content engine for Vietnamese topic-aware content. "
            "Generate practical, technically grounded final content. "
            "Every deliverable must use independent reasoning, an original opening, "
            "and a channel-specific structure."
        )
        for attempt in range(2):
            try:
                if self.ai is not None:
                    response = self.ai.generate(system_prompt, user_prompt)
                else:
                    response = self.provider_manager.generate_real_ai(system_prompt, user_prompt)
            except Exception:
                logger.exception(
                    "AI generation raised for %s.",
                    spec.key,
                )
                raise

            if isinstance(response, AIProviderError):
                if response.error_type in {"network_error", "connection_error", "timeout"}:
                    fallback(f"No Internet or provider timeout for {spec.key}; switching to offline topic intelligence.")
                    logger.info(
                        "Provider network failure for %s, switching to offline topic intelligence.",
                        spec.key,
                    )
                    return self._generate_with_builtin(spec, topic, context, topic_context=topic_context)
                fallback(f"AIProviderError for {spec.key}; switching to offline topic intelligence.")
                logger.info(
                    "AI provider failed for %s; local generator is blocked in AI mode.",
                    spec.key,
                )
                raise RuntimeError(response.message or response.error_type)

            content = getattr(response, "content", "") or ""
            metadata: dict[str, Any] = getattr(response, "metadata", {}) or {}

            if metadata.get("mock"):
                logger.info(
                    "Mock provider detected for %s; local generator is blocked in AI mode.",
                    spec.key,
                )
                raise RuntimeError("Mock provider response is not valid AI-mode content.")

            final_text = self._validate_response(content)
            if not final_text:
                logger.info(
                    "Invalid or empty AI response for %s; local generator is blocked in AI mode.",
                    spec.key,
                )
                raise RuntimeError("Invalid or empty AI response.")

            if self._is_duplicate_shape(final_text) and attempt == 0:
                retry_variation = self._new_variation(f"{variation}:retry")
                user_prompt = self._build_prompt(
                    topic,
                    context,
                    spec,
                    retry_variation,
                    topic_context=topic_context,
                    retry_note=(
                        "The previous draft reused an opening or body structure. "
                        "Rewrite with a different first paragraph, section order, "
                        "and progression of ideas."
                    ),
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
        topic_context: TopicContext | None = None,
    ) -> str:
        trace_call("Generator._generate_with_builtin", self, selected_topic=topic, writer_selected=spec.key)
        logger.info("Mode: Offline Topic Intelligence")
        logger.info("Using offline topic intelligence engine for %s", spec.key)
        if self._uses_general_builder(topic):
            builder_key = {
                "checklist": "approval",
                "image_prompt": "image",
                "video_prompt": "video",
            }.get(spec.key, spec.key)
            trace_call(
                "General Builder selected",
                self,
                selected_topic=topic,
                writer_selected=builder_key,
                writer_class=BuilderFactory.__name__,
                selected_builder=builder_key,
            )
            return BuilderFactory.create(builder_key).build(topic, context)
        trace_call(
            "Topic Engine selected",
            self.topic_engine,
            selected_topic=topic,
            writer_selected=spec.key,
            writer_class=self.topic_engine.__class__.__name__,
            selected_builder=self.topic_engine.__class__.__name__,
        )
        return self.topic_engine.generate(topic, spec.key, context, topic_context=topic_context)

    def _uses_general_builder(self, topic: str) -> bool:
        return self.general_router.can_handle(topic) or self.topic_classifier.uses_general_builder(topic)

    def _plain(self, text: str) -> str:
        decomposed = unicodedata.normalize("NFD", text.lower())
        value = "".join(
            char for char in decomposed if unicodedata.category(char) != "Mn"
        )
        value = value.replace("đ", "d")
        return re.sub(r"\s+", " ", value).strip()

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

    def _validate_response(self, content: Any) -> str:
        if not isinstance(content, str):
            return ""
        text = content.strip()
        if not text:
            return ""
        if text.startswith(
            "AI provider encountered an error while generating content."
        ):
            return ""
        if text.startswith("AI provider is unavailable"):
            return ""
        if text.startswith("AI provider is not available"):
            return ""
        lowered = text.lower()
        if any(term.lower() in lowered for term in _FORBIDDEN_OUTPUT_TERMS):
            return ""
        if any(pattern.lower() in lowered for pattern in _BROKEN_VIETNAMESE_PATTERNS):
            return ""
        return text

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


instrument_runtime_tracing(globals())
module_loaded(__name__, __file__, ContentGenerator)
