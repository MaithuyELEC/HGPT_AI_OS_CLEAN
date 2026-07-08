from __future__ import annotations

from hgpt_ai_os.topic_engine.content_planner import ContentPlan
from hgpt_ai_os.topic_engine.reasoning_engine import ReasoningObject


def bullets(values: tuple[str, ...], limit: int = 4) -> list[str]:
    return [f"- {value}" for value in values[:limit]]


def inline(values: tuple[str, ...], fallback: str) -> str:
    return ", ".join(values) if values else fallback


def facts(reasoning: ReasoningObject) -> list[str]:
    return [f"- {fact.text}" for fact in reasoning.knowledge_facts[:3]]


def hashtags(reasoning: ReasoningObject) -> str:
    tags = ["#LucidAuto", "#HGPTSteel", "#Engineering"]
    for value in (
        *reasoning.entities.get("Process"),
        *reasoning.entities.get("Defect"),
        *reasoning.entities.get("Machine"),
    ):
        tag = "#" + "".join(part.capitalize() for part in value.replace("/", " ").split())
        if tag not in tags:
            tags.append(tag)
    return " ".join(tags[:8])


class ChannelWriter:
    def write(self, reasoning: ReasoningObject, plan: ContentPlan) -> str:
        return "\n".join(
            [
                f"Hook: {reasoning.topic}",
                "",
                f"Body: {reasoning.decision}",
                "",
                "Controls:",
                *bullets(reasoning.controls),
                "",
                "Verification:",
                *bullets(reasoning.verification, 3),
                "",
                f"CTA: Review the evidence before releasing the work. {hashtags(reasoning)}",
            ]
        )
