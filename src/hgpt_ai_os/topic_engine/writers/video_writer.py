from __future__ import annotations

from hgpt_ai_os.topic_engine.content_planner import ContentPlan
from hgpt_ai_os.topic_engine.reasoning_engine import ReasoningObject
from hgpt_ai_os.topic_engine.writers.channel_writer import inline, playbook_for_reasoning


class VideoPromptWriter:
    def write(self, reasoning: ReasoningObject, plan: ContentPlan) -> str:
        playbook = playbook_for_reasoning(reasoning)
        symptom = inline(playbook.typical_symptoms[:2], reasoning.topic)
        check = inline(playbook.inspection_steps[:2], "kiểm tra hiện trường")
        action = inline(playbook.corrective_actions[:2], "khắc phục theo tiêu chí")
        measurement = inline(playbook.measurements[:2], "thông số đo tại hiện trường")
        verification = inline(playbook.verification_steps[:2], "kiểm tra lại sau sửa")
        required_details = inline(
            tuple(dict.fromkeys((*playbook.checklist_items, *playbook.measurements, *playbook.standards, *playbook.safety_risks))),
            "điểm kiểm tra và an toàn chính",
        )
        subject = playbook.video_subject or f"{playbook.process}, {playbook.equipment}"
        return "\n".join(
            [
                f"Tiêu đề: {reasoning.topic}",
                "thời lượng 30-45 giây, khung hình 9:16, phong cách tài liệu công nghiệp thực tế",
                f"Cơ sở kỹ thuật: {playbook.technical_mechanism}",
                f"Mở đầu: cho thấy {subject} trong xưởng thật, không dùng cảnh minh họa chung.",
                f"Cảnh 1: quay dấu hiệu {symptom} và phản ứng của tổ sản xuất khi phát hiện bất thường.",
                f"Cảnh 2: kỹ sư kiểm tra {check}, ghi {measurement}, đối chiếu tiêu chí và lưu kết quả.",
                f"Cảnh 3: đội thực hiện {action}, sau đó {verification} để xác nhận điều kiện bàn giao.",
                "Góc máy: toàn cảnh xưởng, cận cảnh lỗi, cận tay thao tác, khung cuối thấy hồ sơ nghiệm thu; ống kính 35mm và macro cho chi tiết.",
                "Ánh sáng: ánh sáng xưởng tự nhiên, rõ bề mặt thép, không tối và không quá điện ảnh.",
                f"Lời thoại: Đừng xử lý {reasoning.topic} bằng cảm tính. Nhìn dấu hiệu, kiểm tra nguyên nhân, sửa đúng tiêu chí.",
                f"Phụ đề: {reasoning.topic} | {symptom} | {check} | {action}",
                "Âm thanh / SFX: tiếng xưởng nhẹ, tiếng dụng cụ thật, nhạc nền gọn không lấn lời.",
                "Kết thúc: hiển thị kết quả đã được kiểm tra lại, có người chịu trách nhiệm và hồ sơ xác nhận.",
                f"Chi tiết bắt buộc: {required_details}",
                "Kêu gọi hành động: Lưu quy trình này để dùng trong họp đầu ca.",
                "Chi tiết cần tránh: thao tác mất an toàn, thiết bị sai thực tế, chữ méo, thông số không đọc được, cảnh giả lập quá sạch.",
            ]
        )
