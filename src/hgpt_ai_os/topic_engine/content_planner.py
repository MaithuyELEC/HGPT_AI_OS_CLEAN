from __future__ import annotations

from dataclasses import dataclass

from hgpt_ai_os.diagnostics import instrument_runtime_tracing, module_loaded, trace_call

from .reasoning_engine import ReasoningObject


@dataclass(frozen=True)
class ContentPlan:
    channel: str
    sections: tuple[str, ...]
    angle: str


class ContentPlanner:
    _CHANNEL_DEFAULTS = {
        "facebook": ("Hook", "Context", "Practical body", "Lesson", "Reader question"),
        "tiktok": ("Opening", "Quick insight", "Action beat", "Memory point", "Ending"),
        "video": ("Opening", "Scene sequence", "Subject action", "Environment", "Camera movement", "Voice", "Sound", "Ending"),
        "image": ("Subject", "Environment", "Action", "Composition", "Lighting", "Exclusions"),
        "seo": ("Title", "Search intent", "Article sections", "FAQ", "Summary"),
        "checklist": ("Review scope", "Evidence", "Risk", "Channel fit", "Approval decision"),
        "hashtags": ("Topic tags", "Domain tags", "Channel tags"),
        "channel": ("Opening", "Body", "Action"),
    }

    _INTENT_SECTIONS = {
        "DIAGNOSE": ("Symptom", "Safety", "Probable causes", "Inspection sequence", "Repair decision", "Verification", "Prevention"),
        "TROUBLESHOOT": ("Symptom", "Immediate control", "Checks", "Actions", "Acceptance", "Recurrence prevention"),
        "IMPROVEMENT": ("Hook", "Current waste or pain", "Practical behaviors", "Measurable impact", "Implementation steps", "Sustainment", "Discussion question"),
        "SOP": ("Scope", "Inputs", "Step sequence", "Quality hold points", "Safety", "Records"),
        "CHECKLIST": ("Scope", "Safety", "Evidence", "Inspection points", "Acceptance", "Sign-off"),
        "TRAINING": ("Learning hook", "Core concept", "Example", "Practice steps", "Common mistake", "Reflection"),
        "MANAGEMENT": ("Decision context", "Current gap", "Operating rhythm", "Owner", "Metric", "Follow-up"),
        "INVESTMENT_ANALYSIS": ("Use case", "Technical scope", "Options", "CAPEX/OPEX", "Productivity", "Risks", "Recommendation"),
        "SAFETY_WARNING": ("Hazard", "Stop condition", "Safe control", "Escalation", "Verification"),
        "GENERAL_GUIDANCE": ("Need", "Context", "Simple steps", "Mistakes to avoid", "Next action"),
    }

    def plan(self, reasoning: ReasoningObject, channel: str) -> ContentPlan:
        trace_call("ContentPlanner.plan", self, selected_topic=reasoning.topic, writer_selected=channel)
        key = self.normalize_channel(channel)
        context = reasoning.topic_context
        sections = self._sections(context.topic_intent, key)
        primary = (
            reasoning.entities.get("Defect")
            or reasoning.entities.get("Process")
            or reasoning.entities.get("Machine")
            or context.secondary_domains[:1]
            or ((context.domain_family,) if context.domain_family else ())
            or reasoning.parsed.keywords[:2]
            or ("engineering topic",)
        )
        angle = (
            f"{context.topic_intent} plan for {', '.join(primary[:2])}; "
            f"audience: {context.audience}; style: {context.expected_output_style}"
        )
        return ContentPlan(key, sections, angle)

    def _sections(self, intent: str, channel: str) -> tuple[str, ...]:
        intent_sections = self._INTENT_SECTIONS.get(intent, self._INTENT_SECTIONS["GENERAL_GUIDANCE"])
        channel_sections = self._CHANNEL_DEFAULTS.get(channel, self._CHANNEL_DEFAULTS["channel"])
        if channel in {"video", "image", "hashtags"}:
            return channel_sections
        if channel == "checklist":
            return tuple(dict.fromkeys((*channel_sections, *intent_sections[:4])))
        return tuple(dict.fromkeys((*intent_sections, *channel_sections)))

    def normalize_channel(self, channel: str) -> str:
        value = (channel or "").strip().lower().replace("_prompt", "")
        if value in {"approval", "checklist"}:
            return "checklist"
        if value in {"image prompt", "image"}:
            return "image"
        if value in {"video prompt", "video"}:
            return "video"
        if value in self._CHANNEL_DEFAULTS:
            return value
        return "channel"


instrument_runtime_tracing(globals())
module_loaded(__name__, __file__, ContentPlanner)
