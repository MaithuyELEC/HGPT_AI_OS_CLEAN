from __future__ import annotations

from dataclasses import dataclass

from .reasoning_engine import ReasoningObject


@dataclass(frozen=True)
class ContentPlan:
    channel: str
    sections: tuple[str, ...]
    angle: str


class ContentPlanner:
    _SECTIONS = {
        "facebook": ("Hook", "Problem", "Symptoms", "Analysis", "Root Cause", "Solution", "Lesson", "CTA", "Hashtags"),
        "tiktok": ("Hook", "Scene", "Voice", "Caption", "CTA"),
        "video": ("Industrial cinematic prompt",),
        "image": ("Industrial poster prompt",),
        "seo": ("Title", "Search Intent", "Professional Article Outline", "FAQ", "CTA"),
        "checklist": ("Engineering inspection checklist",),
        "hashtags": ("Hashtags",),
        "channel": ("Hook", "Body", "Action"),
    }

    def plan(self, reasoning: ReasoningObject, channel: str) -> ContentPlan:
        key = self.normalize_channel(channel)
        primary = (
            reasoning.entities.get("Defect")
            or reasoning.entities.get("Process")
            or reasoning.entities.get("Machine")
            or reasoning.parsed.keywords[:2]
            or ("engineering topic",)
        )
        angle = f"{reasoning.intent.intent} angle for {', '.join(primary[:2])}"
        return ContentPlan(key, self._SECTIONS.get(key, self._SECTIONS["channel"]), angle)

    def normalize_channel(self, channel: str) -> str:
        value = (channel or "").strip().lower().replace("_prompt", "")
        if value in {"approval", "checklist"}:
            return "checklist"
        if value in {"image prompt", "image"}:
            return "image"
        if value in {"video prompt", "video"}:
            return "video"
        if value in self._SECTIONS:
            return value
        return "channel"
