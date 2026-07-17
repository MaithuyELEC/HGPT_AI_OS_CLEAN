from __future__ import annotations

from hgpt_ai_os.diagnostics import instrument_runtime_tracing, module_loaded, trace_call
from hgpt_ai_os.topic_engine.content_planner import ContentPlan
from hgpt_ai_os.topic_engine.reasoning_engine import ReasoningObject
from hgpt_ai_os.topic_engine.writers.channel_writer import inline, playbook_for_reasoning, sanitize_user_output


class SeoWriter:
    def write(self, reasoning: ReasoningObject, plan: ContentPlan) -> str:
        trace_call("SEO Writer", self, selected_topic=reasoning.topic, writer_selected=plan.channel, writer_class=self.__class__.__name__)
        playbook = playbook_for_reasoning(reasoning)
        trace_call("Selected playbook", self, selected_topic=reasoning.topic, selected_playbook=playbook.key, writer_selected=plan.channel, writer_class=self.__class__.__name__)
        symptoms = inline(playbook.typical_symptoms[:3], reasoning.topic)
        causes = playbook.likely_causes[:5]
        inspections = playbook.inspection_steps[:6]
        repairs = playbook.corrective_actions[:5]
        verification = playbook.verification_steps[:5]
        prevention = playbook.preventive_actions[:5]
        standards = self._standards(playbook)
        keywords = self._keywords(reasoning.topic, playbook)
        return sanitize_user_output("\n".join(
            [
                f"H1: {reasoning.topic}: nguyên nhân, kiểm tra, sửa chữa và phòng ngừa",
                "",
                "Introduction",
                (
                    f"{reasoning.topic} là vấn đề mà nhiều kỹ sư bảo trì, QA/QC và quản lý xưởng tìm kiếm khi hiện trường bắt đầu có {symptoms.lower()}. "
                    f"Nếu xử lý theo cảm tính, sự cố có thể tạo ra {inline(playbook.quality_risks[:2], 'rủi ro chất lượng').lower()} và ảnh hưởng trực tiếp đến {playbook.production_impact.lower()}"
                ),
                (
                    f"Bài viết này không sao chép hồ sơ kỹ thuật. Nội dung được viết lại thành một article dễ tra cứu về root cause, inspection, repair, acceptance, prevention và applicable standards cho {playbook.process}. "
                    f"Các search keywords chính gồm {', '.join(keywords[:6])}."
                ),
                "",
                "H2: Root cause của vấn đề",
                (
                    f"Về cơ chế, {playbook.technical_mechanism} "
                    "Điểm quan trọng là không nhầm triệu chứng với nguyên nhân gốc. Triệu chứng là thứ ta nhìn thấy hoặc nghe thấy; root cause là điều kiện làm triệu chứng quay lại nếu không bị loại bỏ."
                ),
                *[f"- {cause}." for cause in causes],
                (
                    f"Khi phân tích {reasoning.topic}, đội hiện trường nên hỏi ba câu: lỗi xuất hiện ở điều kiện nào, bằng chứng nào lặp lại được, và hành động nào khiến lỗi không quay lại. "
                    "Nếu câu trả lời chỉ dựa trên kinh nghiệm cá nhân, đó chưa phải root cause đủ mạnh để ký nghiệm thu."
                ),
                "",
                "H2: Inspection trước khi repair",
                (
                    "Inspection cần được làm trước khi sửa để không mất dấu vết hiện trường. Với lỗi thiết bị, cần ghi trạng thái vận hành, vị trí lỗi, vật tư liên quan và thông số đo. "
                    "Với lỗi hàn, sơn, fit-up hoặc QA/QC, cần giữ ảnh trước khi mài, sửa hoặc chuyển công đoạn."
                ),
                *[f"- {item}." for item in inspections],
                *[f"- Đo/ghi nhận: {item}." for item in playbook.measurements[:4]],
                (
                    "Một nguyên tắc SEO nhưng cũng là nguyên tắc kỹ thuật: người đọc phải tìm được câu trả lời rõ ràng. "
                    "Vì vậy phần inspection cần nói thẳng kiểm gì, ở đâu, bằng dụng cụ nào, và kết quả dùng để quyết định điều gì."
                ),
                "",
                "H2: Repair workflow và acceptance",
                (
                    f"Repair phải bám vào root cause. Với {playbook.equipment}, không nên chỉ thay vật tư hoặc chỉnh thông số để làm triệu chứng biến mất tạm thời. "
                    "Mục tiêu là loại bỏ điều kiện gây lỗi, sau đó xác nhận lại bằng cùng phương pháp đã phát hiện lỗi."
                ),
                *[f"- {item}." for item in repairs],
                (
                    "Acceptance là điểm phân biệt sửa xong và sửa đúng. Một kết quả được chấp nhận khi có bằng chứng trước/sau, tiêu chí pass/fail, người xác nhận, thời điểm kiểm tra và điều kiện vận hành rõ ràng."
                ),
                *[f"- Acceptance evidence: {item}." for item in verification],
                "",
                "H2: Common mistakes khi xử lý tại hiện trường",
                (
                    f"Sai lầm phổ biến nhất khi gặp {reasoning.topic} là xử lý phần dễ thấy trước rồi mới tìm nguyên nhân sau. "
                    "Cách này làm hiện trường sạch hơn trong vài phút, nhưng lại xóa mất dữ liệu để giải thích vì sao lỗi xuất hiện. "
                    "Sai lầm thứ hai là dùng checklist như thủ tục ký tên, không dùng nó như công cụ ra quyết định."
                ),
                (
                    f"Một sai lầm khác là không tách rõ trách nhiệm giữa người vận hành, bảo trì và QA/QC. "
                    f"Với {playbook.process}, người vận hành thường thấy triệu chứng đầu tiên, kỹ thuật viên xác nhận điều kiện gây lỗi, còn QA/QC hoặc người phụ trách nghiệm thu cần giữ tiêu chí acceptance. "
                    "Khi ba vai trò này không cùng nhìn một bằng chứng, tranh cãi sau sửa gần như chắc chắn xảy ra."
                ),
                (
                    "Để tránh lặp lại, mỗi lần xử lý nên có một dòng kết luận ngắn: triệu chứng là gì, root cause đã xác nhận là gì, repair đã làm gì, acceptance dựa trên bằng chứng nào, và prevention giao cho ai. "
                    "Dòng kết luận này giúp bài học đi vào ca sau thay vì nằm yên trong hồ sơ."
                ),
                "",
                "H2: Prevention và applicable standards",
                (
                    f"Prevention cho {reasoning.topic} nên biến bài học hiện trường thành checklist, lịch bảo trì, hold point hoặc bước kiểm tra trong ITP. "
                    "Nếu sự cố đã xảy ra một lần, hãy xem lại liệu checklist hiện tại có giúp người vận hành nhận diện sớm dấu hiệu hay không."
                ),
                *[f"- {item}." for item in prevention],
                (
                    f"Applicable standards: {standards}. "
                    "Tiêu chuẩn không thay thế bằng chứng hiện trường; tiêu chuẩn giúp đội xác định tiêu chí kiểm tra, phạm vi nghiệm thu và cách lưu hồ sơ."
                ),
                "",
                "FAQ",
                f"Q: Dấu hiệu nào thường gặp khi xảy ra {reasoning.topic}?\nA: Các dấu hiệu thường gặp gồm {symptoms}.",
                f"Q: Root cause cần kiểm tra đầu tiên là gì?\nA: Bắt đầu từ {inline(causes[:2], 'nguyên nhân có khả năng cao')}, sau đó đối chiếu với bằng chứng đo kiểm.",
                f"Q: Repair có cần làm ngay không?\nA: Cần kiểm soát an toàn ngay, nhưng repair chính thức nên đi sau inspection để tránh xóa dấu vết và sửa sai nguyên nhân.",
                f"Q: Acceptance cần những bằng chứng nào?\nA: Cần ảnh hoặc số đo trước/sau, điều kiện vận hành, người xác nhận và tiêu chí pass/fail liên quan đến {playbook.process}.",
                f"Q: Làm sao prevention hiệu quả hơn?\nA: Đưa {inline(playbook.typical_symptoms[:1], 'dấu hiệu sớm')} vào checklist ca sau, gán owner theo dõi và cập nhật SOP nếu lỗi có nguy cơ lặp lại.",
                "",
                "Summary",
                (
                    f"{reasoning.topic} nên được xử lý như một chuỗi hoàn chỉnh: nhận diện triệu chứng, tìm root cause, inspection có bằng chứng, repair đúng nguyên nhân, acceptance rõ tiêu chí và prevention có owner. "
                    "Khi bài viết SEO giữ được logic này, người đọc không chỉ tìm thấy từ khóa; họ tìm thấy một cách làm có thể áp dụng trong nhà máy."
                ),
            ]
        ))

    def _standards(self, playbook) -> str:
        if playbook.standards:
            return "; ".join(playbook.standards[:5])
        return "bản vẽ được phê duyệt, ITP, checklist QA/QC, hướng dẫn OEM, WPS/PQR hoặc quy trình bảo trì nội bộ"

    def _keywords(self, topic: str, playbook) -> list[str]:
        values = [
            topic,
            f"{topic} root cause",
            f"{topic} inspection",
            f"{topic} repair",
            f"{topic} acceptance",
            f"{topic} prevention",
            playbook.process,
            playbook.equipment,
        ]
        seen = []
        for value in values:
            cleaned = " ".join(str(value).split())
            if cleaned and cleaned.lower() not in {item.lower() for item in seen}:
                seen.append(cleaned)
        return seen


instrument_runtime_tracing(globals())
module_loaded(__name__, __file__, SeoWriter)
