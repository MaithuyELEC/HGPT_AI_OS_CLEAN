from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from .intent import TopicIntent, analyze_topic_intent
from .record import EngineeringRecord


@dataclass(frozen=True)
class EngineeringQualityReport:
    accepted: bool
    issues: tuple[str, ...]


class EngineeringQualityGate:
    _GENERIC_PHRASES = (
        "generic engineering",
        "same as above",
        "only topic title changed",
        "general information",
        "nội dung chung",
        "thông tin chung chung",
        "thiết bị phù hợp",
        "thiết bị/khu vực theo hồ sơ kỹ thuật",
        "cụm chức năng cần kiểm tra",
        "chi tiết liên quan cần xác nhận",
        "triệu chứng bất thường cần ghi nhận",
        "thông số đo cần ghi lại trước và sau sửa",
        "kiểm tra hiện trường theo phiếu kiểm đã phê duyệt",
        "cần kiểm tra thêm",
        "cần xác nhận thêm",
        "kiểm tra tổng quát",
        "xử lý theo quy trình",
        "sửa chữa theo quy trình",
    )

    _FAULT_MIN_COUNTS = {
        "symptoms": 5,
        "failure mechanisms": 4,
        "root causes": 3,
        "inspection": 6,
        "measurements": 5,
        "tools": 5,
        "decision logic": 2,
        "repair": 5,
        "verification": 4,
        "acceptance criteria": 4,
        "prevention": 4,
        "lessons learned": 4,
        "common mistakes": 4,
    }
    _NON_FAULT_MIN_COUNTS = {
        "inspection": 4,
        "tools": 2,
        "decision logic": 2,
        "verification": 2,
        "acceptance criteria": 2,
        "prevention": 2,
        "lessons learned": 2,
        "common mistakes": 2,
    }

    _UNSUPPORTED_NUMBER_PATTERN = re.compile(
        r"\b\d+(?:[.,]\d+)?\s*(?:°c|oc|a|v|kw|bar|mpa|mm/s|mm|cm|m/min|rpm|hz|%|giờ|ngày|tháng)\b",
        re.IGNORECASE,
    )
    _PLACEHOLDER_PATTERN = re.compile(
        r"(\{\{[^}]+\}\}|\[[a-z0-9_ -]*placeholder[a-z0-9_ -]*\]|<[^>]*placeholder[^>]*>|"
        r"\b(?:todo|tbd|lorem ipsum|insert here|replace me|draft_record)\b)",
        re.IGNORECASE,
    )
    _INTERNAL_VARIABLE_PATTERN = re.compile(
        r"\b(?:topic_intent|topic_context|retrieved_context|quality_feedback|"
        r"engineering_schema|field_contracts|source_keys|safe_failure|request_id|"
        r"topic_fingerprint|primary_domain|secondary_domain|expected_user_goal|"
        r"prohibited_assumptions|ambiguity_flags)\b",
        re.IGNORECASE,
    )
    _SECTION_MARKERS = {
        "facebook.docx": ("Mở đầu", "Phân tích nguyên nhân gốc", "Cách xử lý thực tế", "Bài học rút ra"),
        "seo.docx": ("H1:", "H2:", "Câu hỏi thường gặp", "Tóm tắt"),
        "image_prompt.docx": ("subject -", "scene -", "camera -", "negative prompt -"),
        "video_prompt.docx": ("Opening Hook:", "Diagnosis:", "Verification:", "Ending:"),
        "approval_checklist.docx": ("Phiếu kiểm", "Xác nhận sau sửa"),
    }

    def validate_record(self, record: EngineeringRecord, topic_intent: TopicIntent | None = None) -> EngineeringQualityReport:
        topic_intent = topic_intent or analyze_topic_intent(record.topic)
        issues: list[str] = []
        required = {
            "title": record.title,
            "problem": record.problem,
            "equipment": record.equipment,
            "inspection": record.inspection_procedure,
            "verification": record.verification,
            "prevention": record.preventive_maintenance,
            "lessons learned": record.lessons_learned,
        }
        if topic_intent.topic_type in {"FAULT_DIAGNOSIS", "DEFECT_ANALYSIS", "SAFETY_RISK", "QA_QC_NONCONFORMITY"}:
            required.update(
                {
                    "component": record.component,
                    "symptoms": record.failure_symptom,
                    "root causes": record.root_causes,
                    "repair": record.repair_procedure,
                }
            )
        for label, values in required.items():
            if not values:
                issues.append(f"No {label}.")

        count_fields = {
            "symptoms": record.failure_symptom,
            "failure mechanisms": record.failure_mechanisms,
            "root causes": record.root_causes,
            "inspection": record.inspection_procedure,
            "measurements": record.measurements,
            "tools": record.tools_required,
            "decision logic": record.decision_logic,
            "repair": record.repair_procedure,
            "verification": record.verification,
            "acceptance criteria": record.acceptance_criteria,
            "prevention": record.preventive_maintenance,
            "lessons learned": record.lessons_learned,
            "common mistakes": record.common_mistakes,
        }
        minimums = (
            self._FAULT_MIN_COUNTS
            if topic_intent.topic_type in {"FAULT_DIAGNOSIS", "DEFECT_ANALYSIS", "SAFETY_RISK", "QA_QC_NONCONFORMITY"}
            else self._NON_FAULT_MIN_COUNTS
        )
        for label, values in count_fields.items():
            if label not in minimums:
                continue
            minimum = minimums[label]
            if len(values) < minimum:
                issues.append(f"{label} is too thin: {len(values)}/{minimum}.")

        if self._requires_hazard_controls(record) and len(record.safety_controls) < 3:
            issues.append("Safety controls are too thin for hazardous energy work.")

        body = "\n".join(str(value) for value in record.to_dict().values()).lower()
        for phrase in self._GENERIC_PHRASES:
            if phrase in body:
                issues.append(f"Repeated generic text detected: {phrase}.")
        issues.extend(self._leak_issues("EngineeringRecord", body))

        if self._looks_like_title_swap(record):
            issues.append("Only topic title changed; record lacks topic-specific engineering detail.")

        if topic_intent.topic_type in {"FAULT_DIAGNOSIS", "DEFECT_ANALYSIS", "SAFETY_RISK", "QA_QC_NONCONFORMITY"} and self._has_short_root_cause_blocks(record):
            issues.append("Root cause blocks are too short for field troubleshooting.")

        if topic_intent.topic_type in {"FAULT_DIAGNOSIS", "DEFECT_ANALYSIS", "SAFETY_RISK", "QA_QC_NONCONFORMITY"}:
            issues.extend(self._root_cause_contract_issues(record))

        issues.extend(self._semantic_issues(record, topic_intent))

        return EngineeringQualityReport(accepted=not issues, issues=tuple(issues))

    def validate_documents(self, documents: dict[str, str], topic_intent: TopicIntent | None = None) -> EngineeringQualityReport:
        issues: list[str] = []
        normalized = {
            name: self._fingerprint(text)
            for name, text in documents.items()
            if name != "hashtags.docx"
        }
        if len(set(normalized.values())) < max(2, len(normalized) - 1):
            issues.append("Repeated generic text across channel documents.")
        for name, text in documents.items():
            if not text.strip():
                issues.append(f"{name} is empty.")
            if self._has_duplicate_paragraphs(text):
                issues.append(f"{name} contains duplicate paragraphs.")
            for marker in self._SECTION_MARKERS.get(name, ()):
                if marker not in text:
                    issues.append(f"{name} is missing required section marker: {marker}.")
            issues.extend(self._leak_issues(name, text))
            lower_text = text.lower()
            for phrase in self._GENERIC_PHRASES:
                if phrase in lower_text:
                    issues.append(f"{name} contains generic fallback text: {phrase}.")
            if topic_intent is not None:
                for issue in self._text_semantic_issues(name, text, topic_intent):
                    issues.append(issue)
        return EngineeringQualityReport(accepted=not issues, issues=tuple(issues))

    def _leak_issues(self, name: str, text: str) -> list[str]:
        issues: list[str] = []
        if self._PLACEHOLDER_PATTERN.search(text):
            issues.append(f"{name} contains placeholder text.")
        if self._INTERNAL_VARIABLE_PATTERN.search(text):
            issues.append(f"{name} contains internal variable/schema leakage.")
        if self._wrong_language_ratio(text):
            issues.append(f"{name} appears to be in the wrong language.")
        return issues

    def _has_duplicate_paragraphs(self, text: str) -> bool:
        paragraphs = [
            re.sub(r"\s+", " ", paragraph.strip().lower())
            for paragraph in re.split(r"\n{2,}", text)
            if len(paragraph.strip()) > 80
        ]
        return len(paragraphs) != len(set(paragraphs))

    def _wrong_language_ratio(self, text: str) -> bool:
        words = re.findall(r"[A-Za-zÀ-ỹ]+", text)
        if len(words) < 80:
            return False
        vietnamese_markers = re.findall(r"[ăâđêôơưáàảãạắằẳẵặấầẩẫậéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ]", text.lower())
        ascii_alpha = re.findall(r"\b[a-z]{4,}\b", text.lower())
        allowed = {"hook", "real", "shop", "scenario", "root", "cause", "analysis", "practical", "solution", "lesson", "learned", "call", "action", "opening", "failure", "diagnosis", "repair", "verification", "ending", "summary", "subject", "scene", "camera", "lighting", "composition", "materials", "motion", "negative", "prompt", "h1", "h2", "faq"}
        englishish = [word for word in ascii_alpha if word not in allowed]
        return len(vietnamese_markers) < 12 and len(englishish) > 45

    def _looks_like_title_swap(self, record: EngineeringRecord) -> bool:
        tokens = set(re.findall(r"[a-zA-ZÀ-ỹ0-9]+", record.topic.lower()))
        details = " ".join(
            (
                *record.root_causes,
                *record.inspection_procedure,
                *record.repair_procedure,
                *record.verification,
            )
        ).lower()
        detail_tokens = set(re.findall(r"[a-zA-ZÀ-ỹ0-9]+", details))
        return len(detail_tokens.difference(tokens)) < 16

    def _requires_hazard_controls(self, record: EngineeringRecord) -> bool:
        body = " ".join(
            (
                record.topic,
                record.domain,
                record.problem,
                *record.equipment,
                *record.component,
                *record.failure_symptom,
                *record.root_causes,
            )
        ).lower()
        return bool(
            re.search(
                r"\b(điện|motor|động cơ|vfd|biến tần|thủy lực|khí nén|áp|cầu trục|cáp|"
                r"palang|nâng|laser|khí cắt|gas|nhiệt|quay|áp suất)\b",
                body,
            )
        )

    def _has_short_root_cause_blocks(self, record: EngineeringRecord) -> bool:
        for item in record.root_causes:
            word_count = len(re.findall(r"[a-zA-ZÀ-ỹ0-9]+", item))
            if word_count < 45:
                return True
        return False

    def _root_cause_contract_issues(self, record: EngineeringRecord) -> list[str]:
        required_terms = (
            ("ranking", ("hạng", "ưu tiên", "xác suất", "khả năng")),
            ("mechanism", ("cơ chế", "vì sao", "nguyên nhân")),
            ("evidence", ("kiểm tra", "bằng chứng", "đối chiếu", "quan sát")),
            ("measurement", ("đo", "dữ liệu", "thông số")),
            ("tool", ("dụng cụ", "thiết bị đo", "nguồn lực", "phiếu kiểm")),
            ("decision logic", ("logic", "nếu", "quyết định")),
            ("corrective action", ("sửa", "khắc phục", "hiệu chỉnh", "thực hiện")),
            ("verification", ("xác nhận", "kiểm chứng", "chạy thử", "đo lại")),
            ("acceptance", ("tiêu chí", "nghiệm thu", "chấp nhận")),
        )
        issues: list[str] = []
        for index, item in enumerate(record.root_causes, start=1):
            normalized = item.lower()
            missing = [
                label
                for label, markers in required_terms
                if not any(marker in normalized for marker in markers)
            ]
            if missing:
                issues.append(
                    f"Root cause {index} misses required field-analysis element(s): "
                    + ", ".join(missing)
                    + "."
                )
        return issues

    def _fingerprint(self, text: str) -> str:
        words = re.findall(r"[a-zA-ZÀ-ỹ0-9]+", text.lower())
        return " ".join(words[:80])

    def _semantic_issues(self, record: EngineeringRecord, topic_intent: TopicIntent) -> list[str]:
        body = "\n".join(str(value) for value in record.to_dict().values())
        issues = self._text_semantic_issues("EngineeringRecord", body, topic_intent)
        if record.primary_domain and record.primary_domain != topic_intent.primary_domain:
            issues.append("TopicIntent primary_domain mismatch.")
        if record.topic_type and record.topic_type != topic_intent.topic_type:
            issues.append("TopicIntent topic_type mismatch.")
        if topic_intent.main_entity:
            normalized_body = self._normalize(body)
            entity_tokens = [token for token in re.findall(r"[a-z0-9]+", self._normalize(topic_intent.main_entity)) if len(token) > 2]
            if entity_tokens and not any(token in normalized_body for token in entity_tokens[:4]):
                issues.append("Main entity is not represented in the engineering record.")
        return issues

    def _text_semantic_issues(self, name: str, text: str, topic_intent: TopicIntent) -> list[str]:
        issues: list[str] = []
        normalized = self._normalize(text)
        if topic_intent.topic_type in {"MANAGEMENT_METHOD", "PROCESS_GUIDE", "INVESTMENT_EVALUATION", "TECHNICAL_EXPLANATION"}:
            forbidden = ("vong bi", "o bi", "dong co bi nong", "ap suat may nen", "rung mm/s", "dong dien tung pha")
            for term in forbidden:
                if self._contains_normalized_term(normalized, term) and not self._contains_normalized_term(topic_intent.normalized_topic, term):
                    issues.append(f"{name} forces a failure-template detail into {topic_intent.topic_type}: {term}.")
            contamination_terms = (
                "dong co",
                "bom thuy luc",
                "cum truyen dong",
                "cuon day stator",
                "khop noi",
                "van an toan",
                "rung rms",
                "dong dien tung pha",
                "ap suat lam viec",
            )
            unrelated_terms = [
                term
                for term in contamination_terms
                if self._contains_normalized_term(normalized, term)
                and not self._contains_normalized_term(topic_intent.normalized_topic, term)
            ]
            if len(unrelated_terms) >= 3:
                issues.append(
                    f"{name} forces unrelated fault-diagnosis template details into {topic_intent.topic_type}: "
                    + ", ".join(unrelated_terms[:5])
                    + "."
                )
        domain_forbidden = {
            "WELDING_ENGINEERING": ("vong bi", "bom thuy luc", "cau truc dut cap"),
            "HYDRAULIC_PNEUMATIC": ("ro khi duong han", "chieu day son", "cap cau truc"),
            "CRANE_LIFTING": ("ro khi duong han", "bom thuy luc mat ap", "son bong troc"),
            "TPM_LEAN_KAIZEN": ("vong bi bi keu", "bom thuy luc mat ap", "duong han saw ro khi"),
        }
        for term in domain_forbidden.get(topic_intent.primary_domain, ()):
            if self._contains_normalized_term(normalized, term) and not self._contains_normalized_term(topic_intent.normalized_topic, term):
                issues.append(f"{name} contains unrelated domain contamination: {term}.")
        if "password" in normalized or "mat khau" in normalized or "bypass" in normalized:
            if "mhi" in topic_intent.normalized_topic or "hmi" in topic_intent.normalized_topic:
                issues.append(f"{name} contains prohibited access-bypass content.")
        for match in self._UNSUPPORTED_NUMBER_PATTERN.finditer(text):
            window = text[max(0, match.start() - 90) : match.end() + 90].lower()
            if not any(marker in window for marker in ("theo", "oem", "manual", "wsp", "wps", "itp", "tiêu chuẩn", "tieu chuan", "người dùng cung cấp", "nguoi dung cung cap")):
                issues.append(f"{name} contains unsupported numeric value: {match.group(0)}.")
        return issues

    def _normalize(self, value: str) -> str:
        ascii_text = unicodedata.normalize("NFD", value.replace("Đ", "D").replace("đ", "d"))
        ascii_text = "".join(
            character
            for character in ascii_text
            if unicodedata.category(character) != "Mn"
        )
        return re.sub(r"\s+", " ", ascii_text.lower())

    def _contains_normalized_term(self, text: str, term: str) -> bool:
        pattern = r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])"
        return re.search(pattern, text) is not None
