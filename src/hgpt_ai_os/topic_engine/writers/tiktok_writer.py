from __future__ import annotations

from hgpt_ai_os.topic_engine.content_planner import ContentPlan
from hgpt_ai_os.topic_engine.reasoning_engine import ReasoningObject
from hgpt_ai_os.topic_engine.writers.channel_writer import hashtags, inline


class TikTokWriter:
    def write(self, reasoning: ReasoningObject, plan: ContentPlan) -> str:
        symptom = inline(reasoning.problem.symptoms[:1], reasoning.topic)
        control = inline(reasoning.controls[:1], "control the process before release")
        verify = inline(reasoning.verification[:1], "record inspection evidence")
        return "\n".join(
            [
                f"Hook 3s: Quay cận cảnh {symptom} và nói: \"Đừng cho qua khi chưa biết nguyên nhân.\"",
                "",
                "Scene sequence:",
                f"1. Wide shot: khu vực sản xuất với chủ đề {reasoning.topic}.",
                f"2. Close-up: chỉ ra dấu hiệu {symptom}.",
                f"3. Cutaway: kỹ sư kiểm tra {verify}.",
                f"4. Action shot: đội sản xuất thực hiện {control}.",
                "5. Final shot: hồ sơ kiểm tra được ký xác nhận trước khi chuyển công đoạn.",
                "",
                f"Voice: {reasoning.decision}",
                "",
                f"Caption: Kiểm tra nguyên nhân trước, sửa đúng điểm sau. {hashtags(reasoning)}",
                "",
                "CTA: Follow để nhận thêm tình huống kỹ thuật trong xưởng.",
            ]
        )
