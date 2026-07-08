from __future__ import annotations

from hgpt_ai_os.topic_engine.content_planner import ContentPlan
from hgpt_ai_os.topic_engine.reasoning_engine import ReasoningObject


class ChecklistWriter:
    def write(self, reasoning: ReasoningObject, plan: ContentPlan) -> str:
        lines = [
            f"Engineering inspection checklist: {reasoning.topic}",
            "",
            "Before work:",
        ]
        lines.extend(f"- [ ] Confirm {item}" for item in reasoning.problem.root_cause_candidates[:4])
        lines.extend(["", "During inspection:"])
        lines.extend(f"- [ ] Check {item}" for item in reasoning.verification[:4])
        lines.extend(["", "Control action:"])
        lines.extend(f"- [ ] Apply {item}" for item in reasoning.controls[:4])
        lines.extend(
            [
                "",
                "- [ ] Record photo, measurement, responsible person, and release decision.",
                "- [ ] Do not close the item until quality, safety, cost, and schedule impacts are reviewed.",
            ]
        )
        return "\n".join(lines)
