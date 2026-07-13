from __future__ import annotations

from hgpt_ai_os.diagnostics import instrument_runtime_tracing, module_loaded, trace_call
from hgpt_ai_os.topic_engine.content_planner import ContentPlan
from hgpt_ai_os.topic_engine.reasoning_engine import ReasoningObject
from hgpt_ai_os.topic_engine.writers.channel_writer import inline, playbook_for_reasoning, sanitize_user_output


class VideoPromptWriter:
    def write(self, reasoning: ReasoningObject, plan: ContentPlan) -> str:
        trace_call("Video Prompt Writer", self, selected_topic=reasoning.topic, writer_selected=plan.channel, writer_class=self.__class__.__name__)
        playbook = playbook_for_reasoning(reasoning)
        trace_call("Selected playbook", self, selected_topic=reasoning.topic, selected_playbook=playbook.key, writer_selected=plan.channel, writer_class=self.__class__.__name__)
        symptom = inline(playbook.typical_symptoms[:2], reasoning.topic)
        check = inline(playbook.inspection_steps[:2], "kiểm tra hiện trường")
        action = inline(playbook.corrective_actions[:2], "khắc phục theo tiêu chí")
        measurement = inline(playbook.measurements[:2], "thông số đo tại hiện trường")
        verification = inline(playbook.verification_steps[:2], "kiểm tra lại sau sửa")
        required_details = inline(
            tuple(dict.fromkeys((*playbook.checklist_items[:5], *playbook.measurements[:3], *playbook.safety_risks[:2]))),
            "điểm kiểm tra và an toàn chính",
        )
        subject = playbook.video_subject or f"{playbook.process}, {playbook.equipment}"
        return sanitize_user_output("\n".join(
            [
                f"Tiêu đề: {reasoning.topic}",
                "Thời lượng: 45-60 giây. Tỷ lệ: 9:16. Phong cách: tài liệu công nghiệp thực tế, không sân khấu hóa.",
                f"Mở đầu: cho thấy {subject} trong xưởng thật, không dùng cảnh minh họa chung.",
                f"Mốc 0-5 giây: cận cảnh {symptom}, người vận hành dừng máy và báo bảo trì.",
                f"Mốc 5-18 giây: kỹ sư kiểm tra {check}, ghi {measurement}, quay rõ dụng cụ đo và điểm lỗi.",
                f"Mốc 18-38 giây: đội thực hiện {action}, giữ nhịp thao tác gọn, không giải thích dài.",
                f"Mốc 38-55 giây: {verification}, quay hồ sơ nghiệm thu và trạng thái thiết bị ổn định.",
                "Góc máy: toàn cảnh xưởng, cận cảnh lỗi, cận tay thao tác, khung cuối thấy hồ sơ nghiệm thu; dùng ống kính 35mm và macro cho chi tiết.",
                "Ánh sáng: ánh sáng xưởng tự nhiên, rõ bề mặt thép, không tối và không quá điện ảnh.",
                f"Lời thoại: Đừng xử lý {reasoning.topic} bằng cảm tính. Nhìn dấu hiệu, kiểm tra nguyên nhân, sửa đúng tiêu chí.",
                f"Phụ đề: {reasoning.topic} | {symptom} | {check} | {action}",
                "Âm thanh: tiếng xưởng nhẹ, tiếng dụng cụ thật, nhạc nền gọn không lấn lời.",
                "Kết thúc: hiển thị kết quả đã được kiểm tra lại, có người chịu trách nhiệm và hồ sơ xác nhận.",
                f"Chi tiết bắt buộc: {required_details}",
                "Kêu gọi hành động: Lưu quy trình này để dùng trong họp đầu ca.",
                "Chuyển cảnh: cắt thẳng theo từng mốc, không dùng hiệu ứng gây rối.",
                "Chi tiết cần tránh: thao tác mất an toàn, thiết bị sai thực tế, chữ méo, tiêu chuẩn giả, thông số bịa, cảnh giả lập quá sạch.",
            ]
        ))


instrument_runtime_tracing(globals())
module_loaded(__name__, __file__, VideoPromptWriter)
