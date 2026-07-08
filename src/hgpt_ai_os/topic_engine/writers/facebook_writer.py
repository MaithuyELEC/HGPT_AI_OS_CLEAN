from __future__ import annotations

from hgpt_ai_os.topic_engine.content_planner import ContentPlan
from hgpt_ai_os.topic_engine.reasoning_engine import ReasoningObject
from hgpt_ai_os.topic_engine.writers.channel_writer import bullets, facts, hashtags, inline


class FacebookWriter:
    def write(self, reasoning: ReasoningObject, plan: ContentPlan) -> str:
        p = reasoning.problem
        return "\n".join(
            [
                f"Hook: {reasoning.topic} không nên được xử lý bằng cảm tính; hãy nhìn vào dấu hiệu, nguyên nhân và bằng chứng nghiệm thu.",
                "",
                f"Vấn đề: {inline(p.symptoms, reasoning.topic)} đang tạo rủi ro cho chất lượng, tiến độ và chi phí nếu không được khoanh vùng sớm.",
                "",
                "Triệu chứng cần kiểm tra:",
                *bullets(p.symptoms),
                "",
                "Phân tích nguyên nhân:",
                *bullets(p.root_cause_candidates),
                "",
                "Hành động kiểm soát:",
                *bullets(reasoning.controls),
                "",
                "Bằng chứng trước khi cho qua công đoạn:",
                *bullets(reasoning.verification, 3),
                "",
                "Fact hỗ trợ:",
                *(facts(reasoning) or ["- Không có ghi chú phù hợp; dùng phân tích kỹ thuật từ chủ đề."]),
                "",
                f"Bài học: {reasoning.decision}",
                "",
                f"CTA: Lưu lại checklist kiểm tra cho ca sản xuất hôm nay. {hashtags(reasoning)}",
            ]
        )
