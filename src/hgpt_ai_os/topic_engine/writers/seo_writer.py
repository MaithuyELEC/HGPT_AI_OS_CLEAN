from __future__ import annotations

from hgpt_ai_os.topic_engine.content_planner import ContentPlan
from hgpt_ai_os.topic_engine.reasoning_engine import ReasoningObject
from hgpt_ai_os.topic_engine.writers.channel_writer import pick, playbook_for_reasoning


_TITLE_ANGLES = (
    "{topic}: nguyên nhân gốc, kiểm tra kỹ thuật và giải pháp phòng ngừa",
    "Cách phân tích {topic} trong sản xuất cơ khí và kết cấu thép",
    "{topic}: hướng dẫn kỹ thuật từ triệu chứng đến hành động khắc phục",
)


class SeoWriter:
    def write(self, reasoning: ReasoningObject, plan: ContentPlan) -> str:
        playbook = playbook_for_reasoning(reasoning)
        title = pick(reasoning, _TITLE_ANGLES, "seo-title").format(topic=reasoning.topic)

        return "\n".join(
            [
                title,
                "",
                f"{reasoning.topic} là một vấn đề kỹ thuật thuộc nhóm {playbook.domain}. Để xử lý đúng, đội sản xuất cần hiểu cơ chế phát sinh, kiểm tra bằng chứng tại hiện trường và sửa theo tiêu chí đã được phê duyệt.",
                "",
                "Triệu chứng thường gặp",
                *[f"- {item}" for item in playbook.typical_symptoms],
                "",
                "Cơ chế kỹ thuật",
                playbook.technical_mechanism,
                "",
                "Nguyên nhân cần ưu tiên xác minh",
                *[f"- {item}" for item in playbook.likely_causes],
                "",
                "Cách kiểm tra tại xưởng",
                *[f"- {item}" for item in playbook.inspection_steps],
                "",
                "Biện pháp khắc phục",
                *[f"- {item}" for item in playbook.corrective_actions],
                "",
                "Kiểm soát phòng ngừa",
                *[f"- {item}" for item in playbook.preventive_actions],
                "",
                "Rủi ro nếu bỏ qua",
                *[f"- {item}" for item in (*playbook.quality_risks, *playbook.safety_risks)],
                "",
                "Câu hỏi thường gặp",
                f"1. Khi nào cần dừng để kiểm tra {reasoning.topic}? Khi xuất hiện {playbook.typical_symptoms[0]} hoặc khi tiêu chí nghiệm thu chưa rõ.",
                f"2. Ai chịu trách nhiệm xác nhận? Tổ trưởng, QA/QC và người vận hành liên quan phải cùng đóng bằng chứng kiểm tra.",
                f"3. Nên theo dõi chỉ số nào? Tần suất lỗi, thời gian sửa, kết quả kiểm tra lại và số lần tái diễn theo ca.",
                "",
                "Kế hoạch triển khai tại xưởng",
                "Bước 1: khoanh vùng hiện tượng và tách sản phẩm hoặc thiết bị có nguy cơ khỏi luồng bàn giao.",
                "Bước 2: kiểm tra triệu chứng bằng danh sách điểm kiểm tra chuyên ngành thay vì hỏi miệng hoặc đoán nguyên nhân.",
                "Bước 3: chọn hành động khắc phục theo tiêu chí kỹ thuật đã phê duyệt, ghi người chịu trách nhiệm và thời điểm xác nhận.",
                "Bước 4: cập nhật checklist phòng ngừa để ca sau nhìn thấy cùng dấu hiệu là biết dừng, kiểm tra và báo cáo đúng tuyến.",
                "Bước 5: đưa bài học vào họp đầu ca, kèm ảnh hiện trường, thông số đo và kết quả nghiệm thu sau sửa.",
                "",
                "Kết luận",
                f"Với {playbook.process}, kết quả bền vững không đến từ việc sửa nhanh mà đến từ kiểm soát điều kiện tạo lỗi, ghi bằng chứng kiểm tra và chuẩn hóa hành động phòng ngừa. {playbook.production_impact}",
            ]
        )
