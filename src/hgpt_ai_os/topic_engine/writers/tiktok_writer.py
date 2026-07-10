from __future__ import annotations

from hgpt_ai_os.topic_engine.content_planner import ContentPlan
from hgpt_ai_os.topic_engine.reasoning_engine import ReasoningObject
from hgpt_ai_os.topic_engine.writers.channel_writer import hashtags, inline, playbook_for_reasoning


class TikTokWriter:
    def write(self, reasoning: ReasoningObject, plan: ContentPlan) -> str:
        playbook = playbook_for_reasoning(reasoning)
        symptom = inline(playbook.typical_symptoms[:1], reasoning.topic)
        cause = inline(playbook.likely_causes[:1], "nguyên nhân chưa được kiểm soát")
        action = inline(playbook.corrective_actions[:1], "sửa theo tiêu chí kỹ thuật")
        prevention = inline(playbook.preventive_actions[:1], "chuẩn hóa bước kiểm tra")
        return "\n".join(
            [
                "Mở đầu",
                f"Nếu gặp {reasoning.topic}, đừng vội sửa cho xong. Dấu hiệu đầu tiên cần nhìn là {symptom}.",
                "",
                "Khơi tò mò",
                f"Một lỗi nhỏ có thể kéo theo dừng chuyền vì {playbook.production_impact.lower()}",
                "",
                "Nỗi đau",
                f"Đội xưởng thường mất thời gian khi chỉ xử lý bề mặt mà bỏ qua {cause}.",
                "",
                "Thông tin",
                f"Cách làm đúng: kiểm tra {inline(playbook.inspection_steps[:2], 'điểm kỹ thuật chính')}, rồi {action}.",
                "",
                "Cú twist",
                f"Điểm quyết định không nằm ở sửa nhanh, mà ở việc {prevention} để ca sau không lặp lại.",
                "",
                "Kêu gọi hành động",
                f"Lưu lại để họp đầu ca và kiểm tra trước khi bàn giao. {hashtags(reasoning)}",
            ]
        )
