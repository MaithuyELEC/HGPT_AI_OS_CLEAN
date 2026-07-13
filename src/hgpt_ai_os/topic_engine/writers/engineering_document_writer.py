from __future__ import annotations

import re
from dataclasses import dataclass

from hgpt_ai_os.diagnostics import instrument_runtime_tracing, module_loaded, trace_call
from hgpt_ai_os.topic_engine.content_planner import ContentPlan
from hgpt_ai_os.topic_engine.engineering_knowledge_library import EngineeringKnowledgeLibrary, EngineeringPlaybook
from hgpt_ai_os.topic_engine.reasoning_engine import ReasoningObject
from hgpt_ai_os.topic_engine.writers.channel_writer import DomainPlaybook, playbook_for_reasoning


ROOT_CAUSE_FIELDS = (
    "Dấu hiệu nhận biết",
    "Phương pháp kiểm tra",
    "Đo kiểm",
    "Dụng cụ",
    "Tiêu chí kết luận",
    "Hành động khắc phục",
    "Phòng ngừa tái diễn",
)

ENGINEERING_SECTIONS = (
    "Mô tả sự cố",
    "Nguyên lý kỹ thuật",
    "Cơ chế hư hỏng",
    "Dạng hư hỏng",
    "Phân tích nguyên nhân gốc",
    "Phân tích 5 Vì sao",
    "Quy trình kiểm tra",
    "Dụng cụ cần chuẩn bị",
    "Đo kiểm",
    "Tiêu chí nghiệm thu",
    "Tiêu chuẩn áp dụng",
    "Quy trình sửa chữa",
    "Xác minh sau sửa",
    "Bảo trì phòng ngừa",
    "Bài học kinh nghiệm",
    "Sai lầm thường gặp",
    "Kaizen",
    "Hành động quản lý",
    "Đề xuất Digital Factory",
)


@dataclass(frozen=True)
class RootCauseBranch:
    root_cause: str
    cause_type: str
    symptoms: str
    inspection: str
    measurement: str
    tools: str
    decision: str
    corrective_action: str
    preventive_action: str
    risk_if_ignored: str
    confidence: str


class KnowledgeQualityGate:
    _GENERIC_PHRASES = (
        "check carefully",
        "do regular maintenance",
        "improve quality",
        "follow safety rules",
        "use proper tools",
        "kiểm tra cẩn thận",
        "bảo trì thường xuyên",
        "nâng cao chất lượng",
        "tuân thủ an toàn",
        "dùng dụng cụ phù hợp",
        "can trigger",
        "dấu hiệu bất thường",
        "cần kiểm tra",
        "có thể",
        "trong nhiều trường hợp",
        "thiết bị/khu vực liên quan",
        "process/control system",
    )
    _MARKETING_PHRASES = (
        "hook:",
        "cta:",
        "viral",
        "engaging",
        "audience",
        "kêu gọi hành động",
        "lưu lại",
        "#",
    )

    def validate(self, document: str, root_causes: tuple[RootCauseBranch, ...], *, strict_density: bool = True) -> None:
        missing = [section for section in ENGINEERING_SECTIONS if f"{section}\n" not in document]
        if missing:
            raise ValueError(f"Knowledge Engine V2 rejected output: missing sections {', '.join(missing)}")

        for branch in root_causes:
            block = self._root_cause_block(document, branch.root_cause)
            missing_fields = [field for field in ROOT_CAUSE_FIELDS if f"{field}:" not in block]
            if missing_fields:
                raise ValueError(
                    f"Knowledge Engine V2 rejected output: root cause '{branch.root_cause}' missing "
                    + ", ".join(missing_fields)
                )

        lowered = document.lower()
        for phrase in (*self._GENERIC_PHRASES, *self._MARKETING_PHRASES):
            if phrase in lowered:
                raise ValueError(f"Knowledge Engine V2 rejected output: forbidden phrase '{phrase}'")

        sentences = [
            normalized
            for sentence in re.split(r"(?<=[.!?])\s+", document)
            if len(normalized := sentence.strip().lower()) > 40
        ]
        if len(sentences) != len(set(sentences)):
            raise ValueError("Knowledge Engine V2 rejected output: repeated sentence detected")

        for required in ("Đo kiểm:", "Tiêu chí kết luận:", "Tiêu chí nghiệm thu", "Tiêu chuẩn áp dụng"):
            if required not in document:
                raise ValueError(f"Knowledge Engine V2 rejected output: missing {required}")

        technical_anchors = (
            "ISO",
            "OEM",
            "LOTO",
            "WPS",
            "VT",
            "UT",
            "QA/QC",
            "CMMS",
            "dòng",
            "áp",
            "nhiệt",
            "rung",
            "đường kính",
            "khe hở",
            "dầu",
            "cáp",
            "puly",
            "tang",
            "lọc",
            "van",
            "motor",
            "VFD",
            "blast",
            "profile",
            "chênh áp",
            "thử tải",
        )
        if strict_density and sum(document.count(anchor) for anchor in technical_anchors) < 35:
            raise ValueError("Knowledge Engine V2 rejected output: insufficient engineering evidence density")

    def validate_playbook(self, document: str, playbook: EngineeringPlaybook) -> None:
        missing = [section for section in ENGINEERING_SECTIONS if f"{section}\n" not in document]
        if missing:
            raise ValueError(f"Knowledge Engine V3 rejected output: missing sections {', '.join(missing)}")
        checks = {
            "root causes": len(playbook.root_causes) >= 3,
            "standards": bool(playbook.related_standards),
            "measurements": bool(playbook.measurements),
            "inspection": bool(playbook.inspection_procedure),
            "repair SOP": bool(playbook.repair_procedure_sop),
            "verification": bool(playbook.verification_after_repair),
            "prevention": bool(playbook.preventive_maintenance),
        }
        failed = [label for label, passed in checks.items() if not passed]
        if failed:
            raise ValueError(f"Knowledge Engine V3 rejected output: missing {', '.join(failed)}")
        for root_cause in playbook.root_causes:
            for value in (
                root_cause.symptoms,
                root_cause.inspection,
                root_cause.instruments,
                root_cause.measurements,
                root_cause.acceptance,
                root_cause.repair,
                root_cause.verification,
                root_cause.prevention,
            ):
                if not value:
                    raise ValueError(f"Knowledge Engine V3 rejected output: incomplete root cause {root_cause.cause}")
        lowered = document.lower()
        for phrase in (*self._GENERIC_PHRASES, *self._MARKETING_PHRASES):
            if phrase in lowered:
                raise ValueError(f"Knowledge Engine V3 rejected output: forbidden phrase '{phrase}'")

    def _root_cause_block(self, document: str, root_cause: str) -> str:
        start = document.find(f"Nguyên nhân gốc: {root_cause}")
        if start < 0:
            return ""
        next_start = document.find("\nNguyên nhân gốc: ", start + 1)
        return document[start:] if next_start < 0 else document[start:next_start]


class EngineeringDocumentWriter:
    def __init__(self) -> None:
        trace_call("EngineeringDocumentWriter.__init__", self)
        self.quality_gate = KnowledgeQualityGate()
        self.knowledge_library = EngineeringKnowledgeLibrary()

    def write(self, reasoning: ReasoningObject, plan: ContentPlan) -> str:
        trace_call(
            "Engineering Writer",
            self,
            selected_topic=reasoning.topic,
            selected_domain=reasoning.topic_context.domain,
            selected_playbook=reasoning.topic_context.playbook_key,
            writer_selected=plan.channel,
            writer_class=self.__class__.__name__,
            knowledge_count=len(reasoning.knowledge_facts),
        )
        playbook = playbook_for_reasoning(reasoning)
        structured_playbook = self.knowledge_library.get(playbook.key)
        if structured_playbook is not None:
            document = self._sanitize_document("\n".join(self._render_structured(reasoning, structured_playbook)))
            self.quality_gate.validate_playbook(document, structured_playbook)
            return document
        root_causes = self._root_causes(reasoning, playbook)
        sections = self._render(reasoning, playbook, root_causes)
        engineering_sections = sum(1 for line in sections if line.strip() and not line.strip().startswith("-"))
        trace_call(
            "Engineering sections generated",
            self,
            selected_topic=reasoning.topic,
            selected_playbook=playbook.key,
            writer_selected=plan.channel,
            writer_class=self.__class__.__name__,
            engineering_sections_generated=engineering_sections,
        )
        document = self._sanitize_document("\n".join(sections))
        self.quality_gate.validate(document, root_causes, strict_density=playbook.key != "GENERAL_ENGINEERING")
        return document

    def _render_structured(self, reasoning: ReasoningObject, playbook: EngineeringPlaybook) -> list[str]:
        return [
            "Phân tích hư hỏng kỹ thuật",
            f"Chủ đề: {reasoning.topic}",
            f"Lĩnh vực: {playbook.domain}",
            "",
            "Mô tả sự cố",
            *self._sentences((
                f"{reasoning.topic} thuộc {playbook.process} trên {', '.join(playbook.equipment)}.",
                playbook.production_impact,
            )),
            "",
            "Nguyên lý kỹ thuật",
            *self._sentences((
                f"{playbook.process} được kiểm soát bằng chuỗi thiết bị, thông số đo, tiêu chí nghiệm thu và chuẩn {', '.join(playbook.related_standards[:3])}.",
                "Bàn giao chỉ hợp lệ khi triệu chứng, số đo, hành động sửa và xác minh sau sửa cùng khớp với root cause đã đóng.",
            )),
            "",
            "Cơ chế hư hỏng",
            *self._bullets(playbook.failure_mechanism),
            "",
            "Dạng hư hỏng",
            *self._bullets(playbook.failure_modes),
            "",
            "Phân tích nguyên nhân gốc",
            *self._structured_root_causes(playbook),
            "",
            "Phân tích 5 Vì sao",
            *self._numbered("Vì sao", playbook.root_cause_tree),
            "",
            "Quy trình kiểm tra",
            *self._bullets(playbook.inspection_procedure),
            "",
            "Dụng cụ cần chuẩn bị",
            *self._bullets(playbook.measuring_instruments),
            "",
            "Đo kiểm",
            *self._bullets(playbook.measurements),
            "",
            "Tiêu chí nghiệm thu",
            *self._bullets(playbook.acceptance_criteria),
            "",
            "Tiêu chuẩn áp dụng",
            *self._bullets(playbook.related_standards),
            "",
            "Quy trình sửa chữa",
            *self._bullets(playbook.repair_procedure_sop),
            "",
            "Xác minh sau sửa",
            *self._bullets(playbook.verification_after_repair),
            "",
            "Bảo trì phòng ngừa",
            *self._bullets(playbook.preventive_maintenance),
            "",
            "Bài học kinh nghiệm",
            *self._bullets(playbook.lessons_learned),
            "",
            "Sai lầm thường gặp",
            *self._bullets(playbook.common_mistakes),
            "",
            "Kaizen",
            *self._bullets((
                "chuyển các số đo quan trọng thành hold point trong checklist ca",
                "dùng defect map để ưu tiên khu vực, ca hoặc thiết bị lặp lỗi",
                "gắn owner và deadline cho từng preventive action",
            )),
            "",
            "Hành động quản lý",
            *self._bullets((
                f"Maintenance Engineer chịu trách nhiệm đóng RCA cho {playbook.process}",
                "QA/QC xác nhận tiêu chí nghiệm thu, số đo và ảnh bằng chứng",
                "Workshop Manager chỉ cho restart khi repair record và verification record hoàn tất",
            )),
            "",
            "Đề xuất Digital Factory",
            *self._bullets(playbook.digital_factory_recommendations),
        ]

    def _structured_root_causes(self, playbook: EngineeringPlaybook) -> list[str]:
        lines: list[str] = []
        for root_cause in playbook.root_causes:
            lines.extend(
                [
                    f"Nguyên nhân gốc: {root_cause.cause}",
                    f"Nhóm nguyên nhân: {root_cause.category}",
                    f"Dấu hiệu nhận biết: {'; '.join(root_cause.symptoms)}",
                    f"Phương pháp kiểm tra: {'; '.join(root_cause.inspection)}",
                    f"Đo kiểm: {'; '.join(root_cause.measurements)}",
                    f"Dụng cụ: {'; '.join(root_cause.instruments)}",
                    f"Tiêu chí kết luận: {'; '.join(root_cause.acceptance)}",
                    f"Hành động khắc phục: {'; '.join(root_cause.repair)}",
                    f"Phòng ngừa tái diễn: {'; '.join(root_cause.prevention)}",
                    f"Xác minh sau sửa: {'; '.join(root_cause.verification)}",
                    "",
                ]
            )
        return lines

    def _bullets(self, values: tuple[str, ...]) -> list[str]:
        return [f"- {value}" for value in values]

    def _sentences(self, values: tuple[str, ...]) -> list[str]:
        return [value for value in values if value]

    def _numbered(self, label: str, values: tuple[str, ...]) -> list[str]:
        return [f"{label} {index}: {value}" for index, value in enumerate(values, 1)]

    def _render(
        self,
        reasoning: ReasoningObject,
        playbook: DomainPlaybook,
        root_causes: tuple[RootCauseBranch, ...],
    ) -> list[str]:
        topic = reasoning.topic
        standards = self._standards(playbook)
        safety = self._items((*playbook.safety_risks, *reasoning.topic_context.failure_intelligence.get("safety_notes", ())), 4)
        measurements = self._items(playbook.measurements, 5) or (
            "ghi vị trí hư hỏng, ảnh hiện trường, điều kiện tải và kết quả chạy thử sau sửa",
        )
        verification = self._items(playbook.verification_steps or reasoning.verification, 5)
        inspection = self._items(playbook.inspection_steps or reasoning.evidence, 6)
        repairs = self._items(playbook.corrective_actions, 7)
        extra_repairs = tuple(item.lstrip("- ").strip() for item in self._items(playbook.extra_corrective_actions, 3))
        preventive = self._items(playbook.preventive_actions, 6)
        tools = self._required_tools(playbook, reasoning)
        acceptance = self._acceptance_criteria(playbook)
        management_actions = self._management_actions(playbook)
        mechanisms = playbook.failure_mechanisms or tuple(
            f"{branch.root_cause} tạo sai lệch vật lý trong {playbook.equipment}; xác nhận bằng kiểm tra hiện trường, số đo định lượng và decision logic riêng cho nguyên nhân này."
            for branch in root_causes[:5]
        )

        return [
            "Phân tích hư hỏng kỹ thuật",
            f"Chủ đề: {topic}",
            f"Lĩnh vực: {playbook.domain}",
            "",
            "Mô tả sự cố",
            (
                f"{topic} được xử lý như một RCA kỹ thuật trên {playbook.equipment}. Đầu việc đầu tiên là khóa trạng thái vận hành, "
                f"giữ bằng chứng trước sửa, xác định bộ phận chịu tải hoặc bộ phận lỗi, rồi chỉ bàn giao khi số đo, ảnh hiện trường, "
                f"tiêu chí nghiệm thu và chữ ký Maintenance Engineer/QA/QC/Workshop Manager cùng khớp. {playbook.production_impact}"
            ),
            "",
            "Nguyên lý kỹ thuật",
            (
                f"{playbook.process} phải được đọc theo chuỗi năng lượng/vật liệu/tín hiệu của thiết bị: tải vào, bộ phận truyền lực, "
                "điều kiện bôi trơn/làm mát/điện, điểm đo kiểm và tiêu chí đạt/không đạt. Nguyên tắc bàn giao là không thay thế theo cảm tính "
                "và không vận hành lại trước khi cơ chế lỗi, giới hạn chấp nhận và phương pháp xác minh sau sửa đã được ghi rõ."
            ),
            "",
            "Cơ chế hư hỏng",
            playbook.technical_mechanism,
            *[f"- {item}" for item in self._items(mechanisms, 5)],
            "",
            "Dạng hư hỏng",
            *[f"- {item}" for item in self._items((*playbook.typical_symptoms, *reasoning.topic_context.failures), 7)],
            "",
            "Phân tích nguyên nhân gốc",
            *self._root_cause_lines(root_causes),
            "",
            "Phân tích 5 Vì sao",
            f"Vì sao 1: {topic} xảy ra vì chức năng kỹ thuật của {playbook.equipment} không còn được kiểm soát theo trạng thái vận hành bình thường.",
            f"Vì sao 2: Cơ chế trực tiếp liên quan đến {root_causes[0].root_cause}, tạo ra triệu chứng {root_causes[0].symptoms}.",
            f"Vì sao 3: Điểm kiểm soát hiện trường chưa phát hiện sớm bằng {root_causes[0].measurement}.",
            f"Vì sao 4: Checklist bảo trì/QA chưa buộc ghi bằng chứng trước khi tiếp tục vận hành hoặc bàn giao.",
            "Vì sao 5: Hệ thống quản lý chưa biến sự cố trước đó thành tiêu chí kiểm tra, ngưỡng cảnh báo, hồ sơ CMMS và điều kiện bàn giao.",
            "Kiểm soát hệ thống: cập nhật SOP, checklist, lịch bảo trì, điểm dừng QA/QC và dữ liệu xu hướng để lỗi không phụ thuộc vào kinh nghiệm cá nhân.",
            "",
            "Quy trình kiểm tra",
            "- Cô lập năng lượng, khu vực làm việc và trạng thái thiết bị trước khi tiếp cận.",
            *[f"- Điểm kiểm soát checklist: {item}" for item in self._items(playbook.checklist_items, 12)],
            *[f"- {item}" for item in inspection],
            "- Chụp ảnh, ghi vị trí, người kiểm tra, thời điểm và điều kiện vận hành khi phát hiện.",
            "- Tách bằng chứng trước sửa và sau sửa để QA/QC truy vết được quyết định bàn giao.",
            "",
            "Dụng cụ cần chuẩn bị",
            *[f"- {item}" for item in tools],
            "",
            "Đo kiểm",
            *[f"- {item}" for item in measurements],
            *[f"- Tính toán kỹ thuật: {item}" for item in self._items(playbook.engineering_calculations, 4)],
            "- Hồ sơ: lưu số đo, ảnh, video chạy thử, mã thiết bị đo, ngày hiệu chuẩn nếu có và chữ ký xác nhận.",
            "",
            "Tiêu chí nghiệm thu",
            *[f"- {item}" for item in acceptance],
            "",
            "Tiêu chuẩn áp dụng",
            *[f"- {item}" for item in standards],
            "- Tài liệu OEM, quy trình bảo trì, quy trình nâng hạ, ITP, hồ sơ hiệu chuẩn và quy trình an toàn nội bộ là nguồn đối chiếu bắt buộc khi nghiệm thu cuối.",
            "",
            "Quy trình sửa chữa",
            "- Giữ thiết bị ở trạng thái không vận hành cho đến khi root cause được xác nhận.",
            *[f"- {item}" for item in repairs],
            *[f"- {item}" for item in extra_repairs],
            *[f"- Kiểm soát an toàn: {item}" for item in safety],
            "- Cập nhật biên bản sửa chữa, vật tư thay thế, ảnh hiện trường và người chịu trách nhiệm.",
            "",
            "Xác minh sau sửa",
            *[f"- {item}" for item in verification],
            "- Điểm chứng kiến QA/QC: đối chiếu kết quả chạy thử, số đo và ảnh sau sửa với tiêu chí nghiệm thu.",
            "- Điều kiện bàn giao: Maintenance Engineer, QA/QC Engineer và Workshop Manager cùng đóng bằng chứng trước khi vận hành lại.",
            "",
            "Bảo trì phòng ngừa",
            *[f"- {item}" for item in preventive],
            "- Tạo ngưỡng kích hoạt theo ca/tuần/tháng hoặc theo số giờ vận hành; báo cấp cao ngay khi xu hướng xấu lặp lại.",
            "",
            "Bài học kinh nghiệm",
            *[f"- {item}" for item in self._items(playbook.lessons_learned, 5)],
            "- Mọi sự cố phải tạo thêm một điểm kiểm soát có bằng chứng: vị trí, thông số, người kiểm tra và điều kiện bàn giao.",
            "- Không được kết luận nguyên nhân bằng kinh nghiệm nếu inspection và measurement chưa xác nhận cùng một hướng.",
            "",
            "Sai lầm thường gặp",
            *[f"- {item}" for item in self._items(playbook.common_mistakes, 5)],
            "- Sửa bộ phận nhìn thấy trước khi khóa cơ chế gây lỗi.",
            "- Bỏ qua thử lại có tải/không tải hoặc thiếu chữ ký bàn giao sau sửa.",
            "",
            "Kaizen",
            "- Rút ngắn thời gian chẩn đoán bằng checklist theo triệu chứng, ảnh mẫu lỗi và luồng quyết định đạt/không đạt.",
            "- Chuẩn hóa vật tư thay thế, dụng cụ đo, điểm hold point và biểu mẫu ghi nhận để giảm rework.",
            "- Đưa root cause lặp lại vào họp sản xuất và giao owner theo hành động phòng ngừa cụ thể.",
            "",
            "Hành động quản lý",
            *[f"- {item}" for item in management_actions],
            "",
            "Đề xuất Digital Factory",
            "- Tạo QR inspection record cho thiết bị/khu vực để truy xuất lịch sử lỗi, ảnh, số đo và biên bản sửa chữa.",
            "- Ghi dữ liệu vào CMMS: triệu chứng, root cause, vật tư thay, thời gian dừng, người xác nhận và ngày kiểm tra lại.",
            "- Dùng dashboard theo dõi tần suất lỗi, thời gian dừng, PM quá hạn, hành động khắc phục còn mở và điều kiện bàn giao.",
            "- Thiết lập reminder hiệu chuẩn thiết bị đo, kiểm tra định kỳ và cảnh báo khi cùng triệu chứng lặp lại.",
        ]

    def _root_causes(self, reasoning: ReasoningObject, playbook: DomainPlaybook) -> tuple[RootCauseBranch, ...]:
        symptoms = self._items(playbook.typical_symptoms, 5)
        inspections = self._items(playbook.inspection_steps, 5)
        measurements = self._items(playbook.measurements, 5) or (
            "đo/ghi thông số tại vị trí hư hỏng và so với OEM/ITP/procedure",
        )
        repairs = self._items(playbook.corrective_actions, 5)
        preventive = self._items(playbook.preventive_actions, 5)
        safety_or_quality = self._items((*playbook.safety_risks, *playbook.quality_risks), 3)
        causes = self._items(playbook.likely_causes or reasoning.problem.root_cause_candidates, 12)
        tools = self._required_tools(playbook, reasoning)

        branches = []
        for index, cause in enumerate(causes):
            branches.append(
                RootCauseBranch(
                    root_cause=cause,
                    cause_type=self._cause_type(cause),
                    symptoms=symptoms[index % len(symptoms)] if symptoms else reasoning.topic,
                    inspection=inspections[index % len(inspections)] if inspections else "kiểm tra trực quan và hồ sơ tại vị trí lỗi",
                    measurement=measurements[index % len(measurements)],
                    tools=tools[index % len(tools)],
                    decision=(
                        f"Kết luận nguyên nhân nếu triệu chứng, kết quả kiểm tra và {measurements[index % len(measurements)]} cùng chỉ về "
                        f"{cause}; loại trừ nếu số đo đạt và không có bằng chứng hiện trường tương ứng."
                    ),
                    corrective_action=repairs[index % len(repairs)] if repairs else "sửa hoặc thay bộ phận đã được xác minh là lỗi",
                    preventive_action=preventive[index % len(preventive)] if preventive else "bổ sung điểm kiểm tra vào checklist và CMMS",
                    risk_if_ignored=safety_or_quality[index % len(safety_or_quality)] if safety_or_quality else "lỗi lặp lại và thiết bị không đủ điều kiện bàn giao",
                    confidence="Trung bình cho đến khi có đủ bằng chứng đo kiểm và kiểm tra",
                )
            )
        return tuple(branches)

    def _root_cause_lines(self, root_causes: tuple[RootCauseBranch, ...]) -> list[str]:
        lines: list[str] = []
        for branch in root_causes:
            lines.extend(
                [
                    f"Nguyên nhân gốc: {branch.root_cause}",
                    f"Nhóm nguyên nhân: {branch.cause_type}",
                    f"Dấu hiệu nhận biết: {branch.symptoms}",
                    f"Phương pháp kiểm tra: {branch.inspection}",
                    f"Đo kiểm: {branch.measurement}",
                    f"Dụng cụ: {branch.tools}",
                    f"Tiêu chí kết luận: {branch.decision}",
                    f"Hành động khắc phục: {branch.corrective_action}",
                    f"Phòng ngừa tái diễn: {branch.preventive_action}",
                    f"Rủi ro nếu bỏ qua: {branch.risk_if_ignored}",
                    f"Mức độ tin cậy: {branch.confidence}",
                    "",
                ]
            )
        return lines

    def _standards(self, playbook: DomainPlaybook) -> tuple[str, ...]:
        standards = self._items(playbook.standards, 6)
        if standards:
            return standards
        return (
            "Đối chiếu tài liệu OEM, bản vẽ, WPS/ITP hoặc tiêu chuẩn đã phê duyệt.",
        )

    def _cause_type(self, cause: str) -> str:
        lowered = cause.lower()
        if any(term in lowered for term in ("vật tư", "cáp", "dây", "sơn", "thuốc", "material")):
            return "vật tư hoặc thiết bị"
        if any(term in lowered for term in ("quá tải", "sốc tải", "vận hành", "operator", "công nhân")):
            return "vận hành hoặc con người"
        if any(term in lowered for term in ("bảo trì", "bôi trơn", "kiểm tra", "maintenance", "lọc", "dầu")):
            return "hệ thống bảo trì"
        if any(term in lowered for term in ("puly", "tang", "bạc đạn", "motor", "gearbox", "phanh", "van", "cánh", "blast")):
            return "thiết bị"
        return "quy trình hoặc điều khiển"

    def _items(self, values: tuple[str, ...], limit: int = 6) -> tuple[str, ...]:
        return tuple(value for value in dict.fromkeys(values) if value)[:limit]

    def _is_wire_rope_playbook(self, playbook: DomainPlaybook) -> bool:
        return playbook.key == "WIRE_ROPE_FAILURE"

    def _required_tools(self, playbook: DomainPlaybook, reasoning: ReasoningObject) -> tuple[str, ...]:
        text = " ".join((playbook.key, playbook.domain, playbook.process, playbook.equipment, reasoning.topic)).lower()
        tools = [
            "LOTO kit, barricade tag and field camera for evidence control",
            "OEM manual, approved SOP/ITP, checklist and calibration records",
            "calibrated hand tools, torque tools and inspection light",
        ]
        if self._is_wire_rope_playbook(playbook):
            tools.extend(
                [
                    "thước đo cáp/vernier caliper, bộ đếm sợi đứt và rope certificate",
                    "dưỡng đo rãnh puly, drum inspection template và kiểm tra góc lệch cáp/đồng tâm",
                    "load test weights or approved test load with competent lifting supervisor",
                ]
            )
        if any(token in text for token in ("saw", "hàn", "weld")):
            tools.extend(
                [
                    "welding parameter log, clamp meter and WPS/PQR/WPQ package",
                    "thuốc hàn oven log, moisture control record and clean wire/thuốc hàn storage check",
                    "VT kit, thước đo mối hàn and UT request/report according to ITP",
                ]
            )
        if any(token in text for token in ("blast", "phun bi", "cánh", "impeller")):
            tools.extend(
                [
                    "vibration meter, clamp meter and OEM bánh văng bi dưỡng kiểm mòn",
                    "hạt mài sieve, dust/foreign material tray and bộ phân ly inspection sheet",
                    "dụng cụ đo biên dạng bề mặt, tấm thử and blast dạng phân bố reference photo",
                ]
            )
        if any(token in text for token in ("gearbox", "giảm tốc", "hộp số")):
            tools.extend(
                [
                    "thermal camera, vibration meter and oil sampling bottle",
                    "alignment kit, dial indicator/laser aligner and torque wrench",
                    "oil viscosity/specification sheet, breather and seal inspection kit",
                ]
            )
        if any(token in text for token in ("compressor", "nén khí")):
            tools.extend(
                [
                    "calibrated đồng hồ áp suất, ultrasonic rò rỉ detector and soap solution",
                    "clamp meter, thermometer and lọc differential pressure indicator",
                    "kiểm tra suy giảm áp suất log, oil/lọc service kit and OEM service manual",
                ]
            )
        if any(token in text for token in ("vfd", "biến tần", "inverter")):
            tools.extend(
                [
                    "insulated meter, clamp meter and megger used after isolating the VFD output",
                    "VFD keypad/software, parameter backup file and fault-history screenshot",
                    "arc-flash PPE, DC bus discharge verification and motor nameplate record",
                ]
            )
        return self._items(tuple(tools), 10)

    def _acceptance_criteria(self, playbook: DomainPlaybook) -> tuple[str, ...]:
        text = " ".join((playbook.key, playbook.domain, playbook.process, playbook.equipment)).lower()
        criteria = [
            "Không bàn giao nếu thiếu số đo trước/sau sửa, ảnh bằng chứng, nhánh nguyên nhân gốc đã đóng và chữ ký Maintenance Engineer/QA/QC.",
            "Pass/fail phải trích từ OEM manual, ITP, SOP, tiêu chuẩn trong mục Applicable Standards hoặc baseline đã phê duyệt.",
            "Sau sửa phải chạy thử đúng chế độ làm việc thực tế và không tái xuất hiện triệu chứng trong thời gian quan sát được ghi vào biên bản.",
        ]
        if self._is_wire_rope_playbook(playbook):
            criteria.extend(
                [
                    "Cáp đúng construction, diameter, WLL/giới hạn tải làm việc và chứng chỉ; puly/tang không còn bề mặt làm hỏng cáp.",
                    "Sợi cáp đứt, hiện tượng phồng lồng cáp, ăn mòn, mòn tang, mòn puly, góc lệch cáp và D/d ratio được kiểm theo ISO 4309/OEM.",
                    "Chạy thử không tải và thử tải theo quy trình nâng hạ đạt, phanh/limit switch/overload protection hoạt động.",
                ]
            )
        if any(token in text for token in ("saw", "hàn", "weld")):
            criteria.extend(
                [
                    "Thông số dòng hàn, điện áp, tốc độ chạy, stickout và chiều sâu lớp thuốc nằm trong WPS.",
                    "VT sau sửa đạt và UT/NDT theo ITP không còn chỉ thị rỗ khí vượt mức chấp nhận.",
                    "Thuốc hàn drying/holding log và bề mặt liên kết sạch được lưu cùng repair record.",
                ]
            )
        if any(token in text for token in ("blast", "phun bi", "cánh", "impeller")):
            criteria.extend(
                [
                    "Bánh văng bi chạy không tải và có hạt với rung/dòng motor ổn định theo baseline/OEM.",
                    "Cánh thay theo set cân bằng; lồng định hướng, tấm lót, lực siết bu lông và bộ phân ly không tạo va đập mới.",
                    "Tấm thử đạt độ sạch/biên dạng theo ITP trước khi release sản xuất.",
                ]
            )
        if any(token in text for token in ("gearbox", "giảm tốc", "hộp số")):
            criteria.extend(
                [
                    "Nhiệt gearbox, rung, dòng motor và tiếng ồn sau chạy tải đạt giới hạn OEM hoặc baseline đã phê duyệt.",
                    "Dầu đúng loại/đúng mức, không còn mạt bất thường, breather/phớt không rò sau chạy thử.",
                    "Đồng tâm khớp nối và bu lông bệ được ghi bằng số đo hoặc dấu torque.",
                ]
            )
        if any(token in text for token in ("compressor", "nén khí")):
            criteria.extend(
                [
                    "Áp outlet, bình chứa, đường ống góp và điểm dùng xa nhất đạt điểm đặt dưới tải thực tế.",
                    "Kiểm tra suy giảm áp suất/rò rỉ check sau sửa không cho thấy tụt áp bất thường khi cô lập tải.",
                    "Dòng motor, nhiệt độ xả, chênh áp lọc và chu kỳ load/unload nằm trong giới hạn OEM.",
                ]
            )
        if any(token in text for token in ("vfd", "biến tần", "inverter")):
            criteria.extend(
                [
                    "Jog/no-load/loaded run hoàn tất nhiều chu kỳ không tái diễn OC.",
                    "Peak current, accel time, DC bus, motor parameter và insulation result được ghi vào release record.",
                    "Parameter backup mới được lưu trước khi bàn giao tủ điện.",
                ]
            )
        return tuple(criteria)

    def _management_actions(self, playbook: DomainPlaybook) -> tuple[str, ...]:
        return (
            f"Workshop Manager mở RCA owner cho {playbook.process}, deadline đóng corrective/preventive action và điều kiện restart.",
            "Maintenance Planner cập nhật PM frequency, spare-part min/max, calibration need và planned downtime nếu phải mở kiểm tra sâu.",
            "QA/QC Engineer thêm hold point hoặc witness point vào ITP/SOP khi lỗi ảnh hưởng an toàn, chất lượng hoặc bàn giao.",
            "Production Supervisor điều phối tải, nhân lực và thiết bị thay thế để không ép vận hành khi tiêu chí kỹ thuật chưa đạt.",
            "EHS/Training cập nhật bài học hiện trường, ảnh lỗi và điều kiện dừng máy cho tổ vận hành.",
        )

    def _sanitize_document(self, document: str) -> str:
        replacements = {
            "có thể truy vết": "truy vết được",
            "Có thể truy vết": "Truy vết được",
            "có thể bị khóa": "bị khóa",
            "Có thể bị khóa": "Bị khóa",
            "có thể đến từ": "đến từ",
            "Có thể đến từ": "Đến từ",
            "Dấu hiệu bất thường": "Triệu chứng kỹ thuật có bằng chứng",
            "dấu hiệu bất thường": "triệu chứng kỹ thuật có bằng chứng",
            "Cần kiểm tra": "Xác minh bằng số đo",
            "cần kiểm tra": "xác minh bằng số đo",
            "Có thể": "Rủi ro kỹ thuật là",
            "có thể": "rủi ro kỹ thuật là",
            "Trong nhiều trường hợp": "Với bằng chứng hiện trường phù hợp",
            "trong nhiều trường hợp": "với bằng chứng hiện trường phù hợp",
            "process/control system": "process or control-system evidence",
            "thiết bị/khu vực liên quan": "thiết bị hoặc khu vực được xác định bằng bằng chứng hiện trường",
            "no-load functional test": "chạy thử không tải",
            "load test according to": "thử tải theo",
            "working load limit": "giới hạn tải làm việc",
            "alignment": "đồng tâm",
            "release": "bàn giao",
            "Release": "Bàn giao",
        }
        for source, target in replacements.items():
            document = document.replace(source, target)
        word_replacements = {
            "wear": "mòn",
            "lubrication": "bôi trơn",
            "corrosion": "ăn mòn",
            "fatigue": "mỏi",
        }
        for source, target in word_replacements.items():
            document = re.sub(rf"(?<![A-Za-z0-9]){source}(?![A-Za-z0-9])", target, document, flags=re.IGNORECASE)
        return document


instrument_runtime_tracing(globals())
module_loaded(__name__, __file__, EngineeringDocumentWriter)
