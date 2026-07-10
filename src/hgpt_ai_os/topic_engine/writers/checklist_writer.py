from __future__ import annotations

from hgpt_ai_os.topic_engine.content_planner import ContentPlan
from hgpt_ai_os.topic_engine.reasoning_engine import ReasoningObject
from hgpt_ai_os.topic_engine.writers.channel_writer import playbook_for_reasoning


class ChecklistWriter:
    def write(self, reasoning: ReasoningObject, plan: ContentPlan) -> str:
        playbook = playbook_for_reasoning(reasoning)
        lines = [
            f"Checklist kiểm tra: {reasoning.topic}",
            "",
            "Phạm vi",
            f"- [ ] Quy trình: {playbook.process}",
            f"- [ ] Thiết bị/khu vực: {playbook.equipment}",
            "",
            "Điểm kiểm tra chuyên ngành",
        ]
        lines.extend(f"- [ ] {item}" for item in playbook.checklist_items)
        lines.extend(["", "Kiểm tra xác nhận"])
        lines.extend(f"- [ ] {item}" for item in playbook.inspection_steps)
        lines.extend(["", "Hành động sau khi phát hiện lỗi"])
        lines.extend(f"- [ ] {item}" for item in playbook.corrective_actions)
        lines.extend(["", "Phòng ngừa lặp lại"])
        lines.extend(f"- [ ] {item}" for item in playbook.preventive_actions)
        lines.extend(
            [
                "",
                "Tiêu chí nghiệm thu",
                "- [ ] Tần suất: kiểm tra đầu ca, sau sửa và trước khi chuyển công đoạn.",
                "- [ ] Người chịu trách nhiệm: tổ trưởng sản xuất, QA/QC và người vận hành liên quan.",
                "- [ ] Hành động khi không đạt: cách ly điểm lỗi, báo người phụ trách, sửa theo quy trình và kiểm tra lại.",
                "",
                "Điều kiện bàn giao",
                "- [ ] Có ảnh hiện trường, thông số đo, người chịu trách nhiệm và ngày xác nhận.",
                "- [ ] Đã đóng rủi ro chất lượng, an toàn và ảnh hưởng tiến độ trước khi chuyển công đoạn.",
            ]
        )
        return "\n".join(lines)
