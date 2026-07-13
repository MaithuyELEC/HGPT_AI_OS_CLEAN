from __future__ import annotations

from hgpt_ai_os.diagnostics import instrument_runtime_tracing, module_loaded, trace_call
from hgpt_ai_os.topic_engine.content_planner import ContentPlan
from hgpt_ai_os.topic_engine.reasoning_engine import ReasoningObject
from hgpt_ai_os.topic_engine.writers.channel_writer import inline, playbook_for_reasoning, sanitize_user_output


class FacebookWriter:
    def write(self, reasoning: ReasoningObject, plan: ContentPlan) -> str:
        trace_call("Facebook Writer", self, selected_topic=reasoning.topic, writer_selected=plan.channel, writer_class=self.__class__.__name__)
        playbook = playbook_for_reasoning(reasoning)
        trace_call("Selected playbook", self, selected_topic=reasoning.topic, selected_playbook=playbook.key, writer_selected=plan.channel, writer_class=self.__class__.__name__)
        causes = playbook.likely_causes[:5]
        inspections = playbook.inspection_steps[:6]
        repairs = playbook.corrective_actions[:4]
        extra_repairs = tuple(item.lstrip("- ").strip() for item in playbook.extra_corrective_actions[:2])
        verification = playbook.verification_steps[:4]
        lessons = playbook.lessons_learned[:3] or playbook.preventive_actions[:3]
        mistakes = playbook.common_mistakes[:3]
        standards = self._standards(playbook)
        return sanitize_user_output("\n".join(
            [
                f"{reasoning.topic}: sửa nhanh chưa chắc là sửa đúng.",
                "",
                (
                    f"Khi {inline(playbook.typical_symptoms[:2], reasoning.topic).lower()}, đội hiện trường không nên đi thẳng vào thay vật tư. "
                    f"Vấn đề phải được đọc theo {playbook.process}: tách triệu chứng, đo bằng chứng, khóa nguyên nhân rồi mới cho thiết bị hoặc công đoạn vận hành lại."
                ),
                "",
                "Mô tả kỹ thuật ngắn",
                playbook.technical_mechanism,
                "",
                "Nguyên nhân cần ưu tiên",
                *[f"{index}. {cause}: kiểm bằng {inspections[(index - 1) % len(inspections)]}." for index, cause in enumerate(causes, 1)],
                "",
                "Trình tự kiểm tra thiết yếu",
                *[f"- {item}" for item in inspections],
                *[f"- Đo kiểm: {item}" for item in playbook.measurements[:3]],
                "",
                "Bằng chứng phải có trước khi kết luận",
                (
                    "Một nguyên nhân chỉ được giữ lại khi có đủ ba lớp bằng chứng: dấu hiệu quan sát được, số đo hoặc trạng thái vận hành, "
                    "và kiểm tra sau sửa chứng minh triệu chứng không quay lại. Nếu chỉ có một lớp bằng chứng, đó mới là giả thuyết chẩn đoán, chưa phải kết luận kỹ thuật."
                ),
                (
                    "Với lỗi thiết bị, ảnh hiện trường cần cho thấy đúng vị trí lỗi, vật tư liên quan, thông số trên nhãn máy và điều kiện vận hành lúc phát hiện. "
                    "Với lỗi hàn hoặc bề mặt, phải giữ lại ảnh trước khi mài/sửa để QA/QC truy vết được quyết định."
                ),
                "",
                "Nguyên tắc sửa đúng",
                *[f"- {item}" for item in repairs],
                *[f"- {item}" for item in extra_repairs],
                "- Sau sửa phải chạy thử hoặc kiểm tra lại đúng điều kiện đã phát hiện lỗi; không bàn giao nếu thiếu ảnh, số đo và người xác nhận.",
                "",
                "Xác minh sau sửa",
                *[f"- {item}" for item in verification],
                (
                    "Nếu chưa có giới hạn định lượng trong hồ sơ, không tự bịa ngưỡng. "
                    "Đối chiếu tài liệu OEM, bản vẽ, WPS/ITP hoặc tiêu chuẩn đã phê duyệt rồi mới ký nghiệm thu."
                ),
                (
                    "Hồ sơ bàn giao cần ghi rõ Maintenance Engineer chịu trách nhiệm kỹ thuật, QA/QC xác nhận bằng chứng, "
                    "Workshop Manager xác nhận điều kiện vận hành và thời điểm cho phép chạy lại."
                ),
                "",
                "Điều dễ làm sai",
                *[f"- {item}" for item in mistakes],
                "- Thay vật tư theo kinh nghiệm nhưng không khóa điều kiện tạo lỗi.",
                "- Bỏ qua chạy thử có tải hoặc bỏ qua điểm dùng xa nhất, khiến lỗi xuất hiện lại sau khi đội bảo trì rời hiện trường.",
                "",
                "Tiêu chuẩn và giới hạn",
                standards,
                "",
                "Bài học rút ra",
                *[f"- {item}" for item in lessons],
                "",
                "Gợi ý dùng trong họp đầu ca",
                (
                    f"Đưa một ảnh thật của {playbook.equipment} lên bảng, hỏi tổ vận hành đã thấy {inline(playbook.typical_symptoms[:1], reasoning.topic).lower()} "
                    f"ở công đoạn nào, ai ghi nhận {inline(playbook.measurements[:1], 'số đo đầu tiên')}, và khi nào phải dừng {playbook.process.lower()} "
                    "thay vì cố chạy tiếp. Cách này biến một sự cố thành tiêu chí quan sát hằng ngày, rồi cập nhật CMMS nếu lỗi có nguy cơ lặp lại."
                ),
                (
                    f"Khi {reasoning.topic.lower()} lặp lại, đừng chỉ hỏi ai sửa nhanh hơn. Hãy hỏi vì sao checklist chưa khóa được "
                    f"{inline(causes[:1], 'nguyên nhân chính')}, dữ liệu nào bị thiếu, và hành động phòng ngừa nào phải có owner, hạn hoàn thành, bằng chứng đóng việc."
                ),
                "",
                "Theo bạn, trong ca thật nên kiểm điểm nào trước: triệu chứng dễ thấy, số đo vận hành hay lịch sử bảo trì?",
            ]
        ))

    def _standards(self, playbook) -> str:
        if not playbook.standards:
            return "Đối chiếu tài liệu OEM, bản vẽ, WPS/ITP hoặc tiêu chuẩn đã phê duyệt."
        return "; ".join(f"{standard} dùng để đối chiếu phạm vi áp dụng, không thay thế bằng chứng hiện trường" for standard in playbook.standards[:3])


instrument_runtime_tracing(globals())
module_loaded(__name__, __file__, FacebookWriter)
