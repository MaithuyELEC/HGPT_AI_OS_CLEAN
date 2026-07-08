from __future__ import annotations

from hgpt_ai_os.topic_engine.content_planner import ContentPlan
from hgpt_ai_os.topic_engine.reasoning_engine import ReasoningObject
from hgpt_ai_os.topic_engine.writers.channel_writer import bullets, inline, pick, subject


_TITLE_ANGLES = (
    "{topic}: nguyên nhân gốc, kiểm tra kỹ thuật và giải pháp phòng ngừa",
    "Cách phân tích {topic} trong sản xuất cơ khí và kết cấu thép",
    "{topic}: hướng dẫn kỹ thuật từ triệu chứng đến hành động khắc phục",
)


class SeoWriter:
    def write(self, reasoning: ReasoningObject, plan: ContentPlan) -> str:
        p = reasoning.problem
        keyword = inline(reasoning.parsed.keywords[:4], reasoning.topic)
        title = pick(reasoning, _TITLE_ANGLES, "seo-title").format(topic=reasoning.topic)
        topic_subject = subject(reasoning)

        return "\n".join(
            [
                f"SEO Title: {title}",
                f"Meta Description: Phân tích kỹ thuật về {reasoning.topic}: triệu chứng, cơ chế lỗi, nguyên nhân gốc, kiểm tra xác nhận, giải pháp và bảo trì phòng ngừa.",
                f"Search Intent: Người đọc muốn hiểu {keyword}, xác định nguyên nhân thật và có checklist hành động tại xưởng.",
                "",
                "Introduction",
                f"{reasoning.topic} cần được xem như một bài toán kiểm soát sản xuất, không chỉ là một lỗi riêng lẻ. Với {topic_subject}, chất lượng đầu ra phụ thuộc vào việc đọc đúng triệu chứng, truy nguyên cơ chế phát sinh và ghi lại bằng chứng nghiệm thu trước khi bàn giao.",
                "",
                "Technical Analysis",
                f"Triệu chứng chính: {inline(p.symptoms, reasoning.topic)}.",
                "Cơ chế có khả năng xảy ra:",
                *bullets(reasoning.possible_mechanisms, 5),
                f"Bằng chứng cần ưu tiên: {inline(reasoning.evidence[:4], 'ảnh hiện trường, số đo, nhật ký thông số và xác nhận QA/QC')}.",
                "",
                "Root Cause",
                f"Immediate Cause: {p.immediate_cause}.",
                f"Hidden Cause: {p.hidden_cause}.",
                f"Root Cause: {p.root_cause}.",
                f"Quality Risk: {p.quality_risk}",
                f"Safety Risk: {p.safety_risk}",
                f"Maintenance Risk: {p.maintenance_risk}",
                "",
                "Engineering Solution",
                *bullets(reasoning.corrective_actions, 6),
                f"Cost Impact: {p.cost_impact}",
                f"Schedule Impact: {p.schedule_impact}",
                "",
                "Preventive Maintenance",
                *bullets(reasoning.preventive_actions, 6),
                f"Recommended Inspection: {inline(p.recommended_inspection[:5], 'visual check, measurement record, parameter log')}.",
                "",
                "Conclusion",
                f"Muốn xử lý {reasoning.topic} bền vững, đội sản xuất cần đi theo chuỗi: Problem -> Possible mechanisms -> Evidence -> Most probable cause -> Recommended verification -> Corrective action -> Preventive action. Khi bằng chứng được chuẩn hóa, lỗi giảm lặp lại và quyết định nghiệm thu rõ ràng hơn.",
            ]
        )
