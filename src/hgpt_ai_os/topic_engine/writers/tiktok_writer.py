from __future__ import annotations

from hgpt_ai_os.diagnostics import instrument_runtime_tracing, module_loaded, trace_call
from hgpt_ai_os.topic_engine.content_planner import ContentPlan
from hgpt_ai_os.topic_engine.reasoning_engine import ReasoningObject
from hgpt_ai_os.topic_engine.writers.channel_writer import inline, playbook_for_reasoning, sanitize_user_output


class TikTokWriter:
    def write(self, reasoning: ReasoningObject, plan: ContentPlan) -> str:
        trace_call("TikTok Writer", self, selected_topic=reasoning.topic, writer_selected=plan.channel, writer_class=self.__class__.__name__)
        playbook = playbook_for_reasoning(reasoning)
        trace_call("Selected playbook", self, selected_topic=reasoning.topic, selected_playbook=playbook.key, writer_selected=plan.channel, writer_class=self.__class__.__name__)
        symptom = inline(playbook.typical_symptoms[:1], reasoning.topic)
        cause = inline(playbook.likely_causes[:1], "nguyên nhân chưa được kiểm soát")
        action = inline(playbook.corrective_actions[:1], "sửa theo tiêu chí kỹ thuật")
        measurement = inline(playbook.measurements[:1], "ghi thông số đo tại hiện trường")
        verification = inline(playbook.verification_steps[:1], "kiểm tra lại trước khi bàn giao")
        return sanitize_user_output("\n".join(
            [
                f"Mở đầu: Gặp {reasoning.topic}, đừng sửa vội. Nhìn ngay {symptom}.",
                "",
                "Lời thoại:",
                f"Cảnh 1: dừng thiết bị, quay rõ dấu hiệu và khu vực nguy hiểm.",
                f"Cảnh 2: kiểm {inline(playbook.inspection_steps[:1], 'điểm nghi ngờ chính')} và {measurement}.",
                f"Cảnh 3: đối chiếu nguyên nhân ưu tiên: {cause}.",
                f"Cảnh 4: thực hiện {action}.",
                f"Cảnh 5: {verification}.",
                "",
                "Bài học kỹ thuật:",
                "Không kết luận bằng cảm giác; phải có triệu chứng, số đo và kiểm tra sau sửa cùng khớp.",
                "",
                "Kết thúc: ghi hồ sơ, ký xác nhận, chỉ bàn giao khi lỗi không lặp lại trong chạy thử.",
            ]
        ))


instrument_runtime_tracing(globals())
module_loaded(__name__, __file__, TikTokWriter)
