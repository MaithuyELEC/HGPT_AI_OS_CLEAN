from __future__ import annotations

from hgpt_ai_os.topic_engine.content_planner import ContentPlan
from hgpt_ai_os.topic_engine.reasoning_engine import ReasoningObject
from hgpt_ai_os.topic_engine.writers.channel_writer import bullets, inline


class SeoWriter:
    def write(self, reasoning: ReasoningObject, plan: ContentPlan) -> str:
        keyword = inline(reasoning.parsed.keywords[:3], reasoning.topic)
        return "\n".join(
            [
                f"SEO Title: {reasoning.topic}: nguyên nhân, kiểm tra và hướng xử lý trong sản xuất",
                f"Meta Description: Hướng dẫn kỹ thuật về {reasoning.topic}, tập trung vào triệu chứng, nguyên nhân gốc, kiểm soát và bằng chứng nghiệm thu.",
                f"Search Intent: Người đọc muốn hiểu {keyword} và biết cách xử lý trên hiện trường.",
                "",
                "Professional article outline:",
                "1. Bối cảnh sản xuất và vì sao chủ đề này ảnh hưởng đến chất lượng.",
                "2. Dấu hiệu nhận biết tại xưởng hoặc công trường.",
                "3. Nguyên nhân gốc cần loại trừ trước khi sửa.",
                "4. Tác động đến chất lượng, an toàn, chi phí và tiến độ.",
                "5. Quy trình kiểm tra và kiểm soát đề xuất.",
                "6. Tiêu chí nghiệm thu trước khi chuyển công đoạn.",
                "",
                "Key technical points:",
                *bullets(reasoning.problem.root_cause_candidates),
                "",
                "FAQ:",
                f"- Khi nào cần dừng công đoạn? Khi {inline(reasoning.problem.symptoms[:1], 'dấu hiệu bất thường')} chưa có nguyên nhân rõ.",
                f"- Bằng chứng tối thiểu là gì? {inline(reasoning.verification[:3], 'ảnh, số đo và xác nhận QA/QC')}.",
            ]
        )
