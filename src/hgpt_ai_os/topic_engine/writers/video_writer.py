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
                f"Tiêu đề: Mini documentary - {reasoning.topic}",
                "Thời lượng: 45-60 giây. Tỷ lệ: 9:16. Phong cách: tài liệu công nghiệp điện ảnh, thật hiện trường, không sân khấu hóa.",
                f"Cảnh 1 - Hook: camera push-in từ lối đi xưởng vào {subject}; worker movement: người vận hành giơ tay báo dừng và nhìn về điểm lỗi; machine movement: thiết bị giảm tốc hoặc đứng yên an toàn; ambient sound: tiếng xưởng thấp, một tiếng cảnh báo ngắn; voice: \"Đừng sửa khi chưa biết vì sao lỗi xuất hiện.\" emotion: căng nhưng kiểm soát.",
                f"Cảnh 2 - Failure: macro shot vào {symptom}; worker movement: kỹ thuật viên cúi thấp ngoài vùng nguy hiểm, chỉ vào dấu hiệu; machine movement: bộ phận liên quan dừng hoặc quay chậm có che chắn; ambient sound: tiếng kim loại nhẹ, hơi khí, giấy checklist; voice: \"Triệu chứng chỉ là phần nổi.\" emotion: lo ngại có kỷ luật.",
                f"Cảnh 3 - Diagnosis: camera tracking ngang theo kỹ sư khi kiểm tra {check} và ghi {measurement}; worker movement: một người đo, một người quan sát biên an toàn; machine movement: chỉ có test movement chậm khi đã cô lập; ambient sound: tiếng gauge beep, bút đánh dấu, nền nhạc công nghiệp rất nhẹ; voice: \"Tách giả thuyết khỏi bằng chứng.\" emotion: tập trung.",
                f"Cảnh 4 - Repair: close-up tay thao tác thực hiện {action}; worker movement: đội sửa đúng điểm đã xác nhận, không che điểm lỗi bằng người; machine movement: thiết bị vẫn trong trạng thái kiểm soát; ambient sound: wrench click, motor hum thấp, supervisor xác nhận ngắn; voice: \"Sửa đúng là sửa vào nguyên nhân, không phải vào chỗ dễ thấy nhất.\" emotion: quyết đoán.",
                f"Cảnh 5 - Result: pull-back ra khung rộng cho thấy {verification}, hồ sơ nghiệm thu và trạng thái thiết bị ổn định; worker movement: kỹ sư ký xác nhận, operator gật đầu, cả hai rời khỏi vùng nguy hiểm; machine movement: chạy thử chậm hoặc ready state an toàn; ambient sound: tiếng máy ổn định, checklist tick, không khí nhẹ lại; voice: \"Có bằng chứng rồi mới bàn giao.\" emotion: nhẹ nhõm và tin cậy.",
                "Góc máy: phối hợp toàn cảnh xưởng, handheld-stable documentary, cận cảnh lỗi, macro dụng cụ đo, khung cuối thấy người-thiết bị-hồ sơ cùng lúc.",
                "Ánh sáng: ánh sáng xưởng tự nhiên có task light vào điểm lỗi, rõ bề mặt thép, giữ chất điện ảnh nhưng không quá tối.",
                f"Phụ đề: {reasoning.topic} | {symptom} | {check} | {action}",
                "Âm thanh: tiếng xưởng thật, tiếng dụng cụ thật, nhạc nền gọn không lấn lời, giọng đọc bình tĩnh của kỹ sư trưởng.",
                "Kết thúc: hiển thị kết quả đã được kiểm tra lại, có người chịu trách nhiệm và hồ sơ xác nhận.",
                f"Chi tiết bắt buộc: {required_details}",
                "Kêu gọi hành động: Lưu quy trình này để dùng trong họp đầu ca.",
                "Chuyển cảnh: cắt thẳng theo nhịp tài liệu, có một J-cut âm thanh giữa failure và diagnosis, không dùng hiệu ứng gây rối.",
                "Chi tiết cần tránh: thao tác mất an toàn, thiết bị sai thực tế, chữ méo, cảnh giả lập quá sạch, hoạt hình, CGI rẻ tiền.",
            ]
        ))


instrument_runtime_tracing(globals())
module_loaded(__name__, __file__, VideoPromptWriter)
