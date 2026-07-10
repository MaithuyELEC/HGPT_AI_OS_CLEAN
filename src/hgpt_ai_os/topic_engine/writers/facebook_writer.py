from __future__ import annotations

from hgpt_ai_os.topic_engine.content_planner import ContentPlan
from hgpt_ai_os.topic_engine.reasoning_engine import ReasoningObject
from hgpt_ai_os.topic_engine.writers.channel_writer import pick, playbook_for_reasoning


_HOOKS = (
    "{topic} không nên được xem là một lỗi đơn lẻ. Đây là tín hiệu cho thấy quy trình, vật tư hoặc kỷ luật kiểm tra đang cần được siết lại.",
    "Muốn xử lý {topic} bền vững, đội xưởng phải đi từ dấu hiệu hiện trường đến bằng chứng kỹ thuật, rồi mới quyết định sửa.",
    "{topic} càng sửa nhanh theo cảm tính càng dễ lặp lại. Điểm quan trọng là khóa đúng cơ chế gây lỗi và tiêu chí nghiệm thu.",
    "Một bất thường như {topic} có thể làm chậm cả chuỗi sản xuất nếu không được phân tích bằng dữ liệu tại hiện trường.",
)


class FacebookWriter:
    def write(self, reasoning: ReasoningObject, plan: ContentPlan) -> str:
        playbook = playbook_for_reasoning(reasoning)
        hook = pick(reasoning, _HOOKS, "hook").format(topic=reasoning.topic)

        return "\n".join(
            [
                hook,
                "",
                "Vấn đề hiện trường",
                f"Tại {playbook.process}, hiện tượng này ảnh hưởng trực tiếp đến {playbook.equipment}. Nếu chỉ sửa phần nhìn thấy mà không kiểm soát điều kiện tạo lỗi, ca sau vẫn có thể gặp lại cùng một bất thường.",
                "",
                "Dấu hiệu cần kiểm tra",
                *[f"- {item}" for item in playbook.typical_symptoms[:5]],
                "",
                "Phân tích kỹ thuật",
                playbook.technical_mechanism,
                "",
                "Nguyên nhân khả năng cao",
                *[f"- {item}" for item in playbook.likely_causes[:6]],
                "",
                "Hành động khắc phục",
                *[f"- {item}" for item in playbook.corrective_actions[:6]],
                *(["- sấy thuốc hàn và sửa hàn theo WPS đã phê duyệt"] if playbook.key == "SAW_POROSITY" else []),
                *(["- kiểm tra công tắc/dây nguồn, ghi rung/ồn/nhiệt và huấn luyện công nhân dùng máy mài cầm tay đúng tải"] if playbook.key == "POWER_TOOL_BREAKDOWN" else []),
                "",
                "Phòng ngừa tái diễn",
                *[f"- {item}" for item in playbook.preventive_actions[:6]],
                "",
                "Bài học quản lý",
                f"{playbook.production_impact} Vì vậy quản lý tổ cần biến từng lần xử lý thành dữ liệu: ai kiểm tra, thông số nào được ghi, tiêu chí nào được nghiệm thu và hành động nào được chuẩn hóa.",
                "",
                "Lưu lại checklist này cho ca sản xuất kế tiếp và dùng nó trong họp đầu ca khi lỗi có dấu hiệu lặp lại.",
                "",
                " ".join(playbook.hashtags),
            ]
        )
