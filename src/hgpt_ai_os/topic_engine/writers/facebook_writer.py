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
        return sanitize_user_output("\n".join(
            [
                "Hook",
                (
                    f"{reasoning.topic}: sửa nhanh chưa chắc là sửa đúng. "
                    f"Trong xưởng, dấu hiệu như {inline(playbook.typical_symptoms[:2], reasoning.topic).lower()} thường không làm chúng ta mất nhiều tiền ngay lúc nó xuất hiện. "
                    "Cái làm mất tiền là quyết định cho chạy tiếp khi đội chưa hiểu tại sao nó xuất hiện."
                ),
                (
                    "Một trưởng ca có kinh nghiệm không sợ phát hiện lỗi. Phát hiện lỗi sớm là điều tốt. "
                    "Điều đáng sợ là cả đội cùng gật đầu với một lời giải thích nghe hợp lý nhưng chưa có bằng chứng. "
                    "Khi đó nhà máy chỉ đang dời sự cố sang ca sau, sang công đoạn sau, hoặc sang khách hàng."
                ),
                "",
                "Real shop scenario",
                (
                    f"Hãy đặt mình vào ca sáng ở khu {playbook.process}. Tổ vận hành đang cần trả tiến độ, {playbook.equipment} đã vào nhịp, "
                    f"nhưng hiện trường bắt đầu có {inline(playbook.typical_symptoms[:2], reasoning.topic).lower()}. "
                    "Một người đề xuất xử lý ngay phần nhìn thấy. Một người khác bảo cứ chạy thêm một chút để kịp kế hoạch. "
                    "Đó là khoảnh khắc kỹ thuật phải thắng thói quen."
                ),
                (
                    "Nếu lúc này đội thay vật tư hoặc chỉnh máy theo cảm tính, có thể thiết bị chạy lại thật. "
                    "Nhưng chạy lại không có nghĩa là đã hết lỗi. Với sản xuất cơ khí, hàn, bảo trì hay QA/QC, câu hỏi quan trọng hơn là: điều kiện nào đã tạo ra lỗi, và điều kiện đó đã bị loại bỏ chưa?"
                ),
                (
                    f"Ở hiện trường thật, tôi muốn thấy người phụ trách giữ lại ảnh, vị trí, thông số hoặc trạng thái vận hành trước khi can thiệp. "
                    f"Các điểm cần nhìn không chỉ là lỗi đang kêu to nhất, mà còn là {inline(playbook.checklist_items[:4], 'các điểm kiểm soát chính').lower()}."
                ),
                "",
                "Root cause analysis",
                (
                    f"Về cơ chế, {playbook.technical_mechanism} "
                    "Vì vậy nguyên nhân gốc không phải là thứ chúng ta đoán cho nhanh, mà là điều kiện khi loại bỏ đi thì triệu chứng không quay lại trong cùng điều kiện làm việc."
                ),
                *[f"- Bắt đầu từ giả thuyết {cause}, rồi kiểm bằng: {inspections[(index - 1) % len(inspections)]}." for index, cause in enumerate(causes, 1)],
                (
                    f"Nếu chỉ thấy {inline(playbook.typical_symptoms[:1], reasoning.topic).lower()} mà kết luận ngay, đội đang nhầm triệu chứng với nguyên nhân. "
                    f"Nếu chỉ sửa {inline(repairs[:1], 'một thao tác khắc phục').lower()} mà không kiểm lại điều kiện gây lỗi, rủi ro {inline(playbook.quality_risks[:1], 'lỗi lặp lại').lower()} vẫn còn đó."
                ),
                "",
                "Practical solution",
                (
                    "Workflow cho kỹ thuật viên nên đi theo năm nhịp. Một: dừng hoặc cô lập đủ an toàn để giữ hiện trạng. "
                    "Hai: ghi bằng chứng trước khi xóa dấu vết. Ba: kiểm theo nguyên nhân có khả năng cao nhất. "
                    "Bốn: sửa đúng điểm tạo lỗi, không sửa theo phần dễ thấy nhất. Năm: xác nhận lại đúng điều kiện đã phát hiện lỗi."
                ),
                *[f"{index}. {item}." for index, item in enumerate(inspections[:4], 1)],
                *[f"{index + 4}. {item}." for index, item in enumerate(repairs[:3], 1)],
                *[f"- Sau sửa: {item}." for item in verification[:3]],
                *[f"- Bổ sung nếu cần: {item}." for item in extra_repairs],
                (
                    "Trước khi bàn giao, người phụ trách nên nói lại được một câu đầy đủ: lỗi được phát hiện bằng gì, nguyên nhân nào bị loại bỏ, sửa bằng hành động nào, và bằng chứng sau sửa nằm ở đâu. "
                    "Nếu câu này chưa nói được, hồ sơ bàn giao vẫn còn lỗ hổng."
                ),
                "",
                "Lesson learned",
                (
                    f"Bài học của {reasoning.topic.lower()} là đừng để một sự cố kết thúc bằng câu 'đã xử lý'. "
                    "Nó phải kết thúc bằng một điểm kiểm soát mới trong checklist, một owner rõ ràng, và một bằng chứng đủ để ca sau hiểu vì sao quyết định được đưa ra."
                ),
                *[f"- {item}." for item in lessons],
                "",
                (
                    f"Trong họp đầu ca, hãy đưa một ảnh thật của {playbook.equipment} lên bảng và hỏi cả tổ: dấu hiệu nào buộc phải dừng, ai được quyền xác nhận, và bằng chứng nào đủ để chạy lại? "
                    "Khi mọi người cùng trả lời được, tri thức kỹ thuật đã rời khỏi hồ sơ và trở thành thói quen vận hành."
                ),
                (
                    f"Khi ghi lại bài học, giữ nguyên các từ khóa hiện trường quan trọng như {inline((*playbook.standards[:2], *playbook.measurements[:3], *playbook.common_mistakes[:2]), 'tiêu chuẩn, điểm đo và lỗi thường gặp')} "
                    "để lần sau đội bảo trì, QA/QC và quản lý xưởng tìm đúng lịch sử xử lý."
                ),
                "",
                "Call To Action",
                (
                    f"Nếu gặp {reasoning.topic.lower()} trong ca thật, bạn sẽ kiểm trước {inline(playbook.typical_symptoms[:1], 'triệu chứng')}, "
                    f"{inline(causes[:1], 'nguyên nhân nghi ngờ')}, hay {inline(playbook.measurements[:1], 'điểm đo')}? "
                    "Chia sẻ cách đội bạn đang khóa lỗi để nó không quay lại."
                ),
            ]
        ))

    def _standards(self, playbook) -> str:
        if not playbook.standards:
            return "Đối chiếu tài liệu OEM, bản vẽ, WPS/ITP hoặc tiêu chuẩn đã phê duyệt."
        return "; ".join(f"{standard} dùng để đối chiếu phạm vi áp dụng, không thay thế bằng chứng hiện trường" for standard in playbook.standards[:3])


instrument_runtime_tracing(globals())
module_loaded(__name__, __file__, FacebookWriter)
