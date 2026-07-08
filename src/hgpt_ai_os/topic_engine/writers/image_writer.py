from __future__ import annotations

from hgpt_ai_os.topic_engine.content_planner import ContentPlan
from hgpt_ai_os.topic_engine.reasoning_engine import ReasoningObject
from hgpt_ai_os.topic_engine.writers.channel_writer import inline


class ImagePromptWriter:
    def write(self, reasoning: ReasoningObject, plan: ContentPlan) -> str:
        subject = inline(reasoning.entities.get("Defect") or reasoning.entities.get("Process"), reasoning.topic)
        tools = inline(reasoning.verification[:2], "inspection tools")
        return (
            "Industrial poster prompt: realistic engineering poster inside a steel fabrication workshop, "
            f"main subject: {subject}, visible {tools}, clean composition with engineer and production worker "
            "reviewing evidence, labeled but not text-heavy, sharp focus, accurate PPE, practical lighting, "
            "high-detail metal surfaces, no abstract icons, no fake charts, no distorted hands, no unsafe posture."
        )
