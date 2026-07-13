from __future__ import annotations

from hgpt_ai_os.diagnostics import instrument_runtime_tracing, module_loaded, trace_call
from hgpt_ai_os.topic_engine.content_planner import ContentPlan
from hgpt_ai_os.topic_engine.reasoning_engine import ReasoningObject
from hgpt_ai_os.topic_engine.writers.channel_writer import playbook_for_reasoning, sanitize_user_output


class ChecklistWriter:
    def write(self, reasoning: ReasoningObject, plan: ContentPlan) -> str:
        trace_call("Checklist Writer", self, selected_topic=reasoning.topic, writer_selected=plan.channel, writer_class=self.__class__.__name__)
        playbook = playbook_for_reasoning(reasoning)
        trace_call("Selected playbook", self, selected_topic=reasoning.topic, selected_playbook=playbook.key, writer_selected=plan.channel, writer_class=self.__class__.__name__)
        measurements = playbook.measurements or ("ghi số đo trước/sau sửa theo tài liệu OEM hoặc ITP",)
        mechanical_checks = self._take(playbook.inspection_steps, 5)
        mechanical_text = " ".join(mechanical_checks).lower()
        extra_checks = tuple(
            item
            for item in self._take(playbook.checklist_items, 10)
            if item.lower() not in mechanical_text
        )[:5]
        lines = [
            f"Danh mục kiểm tra hiện trường: {reasoning.topic}",
            "",
            "1. An toàn và cô lập năng lượng",
            "- [ ] Dừng thiết bị/công đoạn và treo cảnh báo khu vực liên quan.",
            "- [ ] Thực hiện LOTO, xả áp/xả tải/xác nhận hết năng lượng tồn dư nếu áp dụng.",
            "- [ ] Xác nhận PPE, lối thoát và người giám sát trước khi mở che chắn hoặc tiếp cận điểm lỗi.",
            "",
            "2. Ghi nhận hiện trạng",
            "- [ ] Chụp ảnh toàn cảnh, cận cảnh lỗi, nhãn thiết bị và vị trí phát hiện.",
            "- [ ] Ghi thời điểm, người phát hiện, chế độ vận hành, tải, âm thanh/mùi/nhiệt/rung bất thường.",
            f"- [ ] Ghi triệu chứng chính: {self._first(playbook.typical_symptoms, reasoning.topic)}.",
            "",
            "3. Kiểm tra cơ khí",
            *[f"- [ ] {item}." for item in mechanical_checks],
            *[f"- [ ] Kiểm tra {item}." for item in extra_checks],
            "",
            "4. Kiểm tra điện/điều khiển",
            "- [ ] Kiểm tra nguồn cấp, dòng tải, tín hiệu cảm biến/công tắc và lịch sử cảnh báo nếu có.",
            "- [ ] Kiểm tra cáp, đầu nối, tủ điều khiển, trạng thái interlock và tham số vận hành liên quan.",
            "",
            "5. Đo kiểm",
            *[f"- [ ] {item}." for item in self._take(measurements, 6)],
            "",
            "6. Khắc phục",
            *[f"- [ ] {item}." for item in self._take(playbook.corrective_actions, 6)],
            "",
            "7. Kiểm tra sau sửa",
            *[f"- [ ] {item}." for item in self._take(playbook.verification_steps, 5)],
            "- [ ] Chạy thử không tải/có tải theo điều kiện thực tế nếu an toàn cho phép.",
            "",
            "8. Nghiệm thu",
            "- [ ] Đối chiếu tài liệu OEM, bản vẽ, WPS/ITP hoặc tiêu chuẩn đã phê duyệt.",
            "- [ ] Lưu ảnh, số đo, video chạy thử, vật tư thay và người chịu trách nhiệm.",
            "- [ ] Maintenance Engineer/QA/QC/Workshop Manager ký xác nhận trước khi bàn giao.",
            "",
            "9. Phòng ngừa tái diễn",
            *[f"- [ ] {item}." for item in self._take(playbook.preventive_actions, 5)],
            "- [ ] Cập nhật CMMS/checklist ca sau bằng lỗi đã xác nhận.",
        ]
        return sanitize_user_output("\n".join(lines))

    def _take(self, values: tuple[str, ...], limit: int) -> tuple[str, ...]:
        return tuple(dict.fromkeys(value for value in values if value))[:limit]

    def _first(self, values: tuple[str, ...], fallback: str) -> str:
        return next((value for value in values if value), fallback)


instrument_runtime_tracing(globals())
module_loaded(__name__, __file__, ChecklistWriter)
