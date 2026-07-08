from __future__ import annotations

from hgpt_ai_os.topic_engine.content_planner import ContentPlan
from hgpt_ai_os.topic_engine.reasoning_engine import ReasoningObject
from hgpt_ai_os.topic_engine.writers.channel_writer import inline


class VideoPromptWriter:
    def write(self, reasoning: ReasoningObject, plan: ContentPlan) -> str:
        subject = inline(reasoning.entities.get("Process") or reasoning.entities.get("Machine"), reasoning.topic)
        symptom = inline(reasoning.problem.symptoms[:2], "visible engineering symptom")
        verification = inline(reasoning.verification[:2], "inspection and sign-off")
        return (
            "Industrial cinematic prompt: 20-second realistic factory video, "
            f"steel fabrication environment, subject is {subject}. "
            f"Start with a wide establishing shot, cut to close-up evidence of {symptom}, "
            f"show an engineer checking {verification}, then show the team applying corrective controls. "
            "Use natural workshop lighting, handheld inspection movement, accurate PPE, no fantasy elements, "
            "no unreadable gauges, no unsafe behavior, final frame shows approved work and documented evidence."
        )
