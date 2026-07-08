from __future__ import annotations

from hgpt_ai_os.topic_engine.content_planner import ContentPlan
from hgpt_ai_os.topic_engine.reasoning_engine import ReasoningObject
from hgpt_ai_os.topic_engine.writers.channel_writer import bullets, hashtags, inline, pick, subject


_HOOKS = (
    "{topic} không phải chuyện xử lý cho xong; đó là tín hiệu cho biết quy trình đang mất kiểm soát ở một điểm rất cụ thể.",
    "Khi gặp {topic}, câu hỏi quan trọng không phải là sửa nhanh thế nào, mà là bằng chứng nào chứng minh được nguyên nhân thật.",
    "Một lỗi nhỏ quanh {topic} có thể kéo theo rework, dừng công đoạn và tranh luận nghiệm thu nếu đội xưởng bỏ qua dấu hiệu ban đầu.",
    "{topic}: nhìn giống sự cố hiện trường, nhưng bản chất thường nằm ở tham số, điều kiện làm việc và kỷ luật kiểm tra.",
)

_TRANSITIONS = (
    "Điểm cần nhìn kỹ:",
    "Cách đọc hiện tượng này:",
    "Chuỗi suy luận nên đi như sau:",
    "Đừng tách lỗi ra khỏi bối cảnh vận hành:",
)


class FacebookWriter:
    def write(self, reasoning: ReasoningObject, plan: ContentPlan) -> str:
        p = reasoning.problem
        topic_subject = subject(reasoning)
        hook = pick(reasoning, _HOOKS, "hook").format(topic=reasoning.topic)
        transition = pick(reasoning, _TRANSITIONS, "transition")

        return "\n".join(
            [
                f"Hook: {hook}",
                "",
                f"Pain Point: {topic_subject} làm đội sản xuất mất nhịp vì triệu chứng thấy được chỉ là phần nổi. Nếu không khoanh vùng, tổ sẽ sửa theo cảm tính, QA/QC thiếu bằng chứng, còn ca sau vẫn gặp lại cùng một lỗi.",
                "",
                "Symptoms:",
                *bullets(p.symptoms, 5),
                "",
                f"Engineering Analysis: {transition}",
                f"- Problem: {inline(p.symptoms[:2], reasoning.topic)}",
                *bullets(reasoning.possible_mechanisms, 4),
                f"- Evidence: {inline(reasoning.evidence[:3], 'ảnh hiện trường, số đo và nhật ký kiểm tra')}",
                f"- Most probable cause: {reasoning.most_probable_cause}",
                f"- Recommended verification: {inline(reasoning.verification[:3], 'kiểm tra trực quan và đo kiểm')}",
                "",
                f"Root Cause: {p.root_cause}. Hidden layer: {p.hidden_cause}. Immediate trigger: {p.immediate_cause}.",
                "",
                "Corrective Action:",
                *bullets(reasoning.corrective_actions, 5),
                "",
                "Preventive Action:",
                *bullets(reasoning.preventive_actions, 5),
                "",
                f"Lesson Learned: {p.production_loss} {p.quality_risk}",
                "",
                f"CTA: Lưu lại quy trình suy luận này cho lần kiểm tra kế tiếp: thấy dấu hiệu, khóa nguyên nhân, đo bằng chứng, rồi mới cho qua công đoạn. {hashtags(reasoning)}",
            ]
        )
