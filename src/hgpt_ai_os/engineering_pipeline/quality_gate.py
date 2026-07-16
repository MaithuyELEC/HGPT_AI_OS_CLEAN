from __future__ import annotations

import re
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
        "symptoms": 3,
        "failure mechanisms": 3,
        "root causes": 3,
        "inspection": 5,
        "measurements": 4,
        "tools": 4,
        "decision logic": 2,
        "repair": 3,
        "verification": 3,
        "acceptance criteria": 3,
        "prevention": 3,
        "lessons learned": 3,
        "common mistakes": 3,
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

        if self._looks_like_title_swap(record):
            issues.append("Only topic title changed; record lacks topic-specific engineering detail.")

        if topic_intent.topic_type in {"FAULT_DIAGNOSIS", "DEFECT_ANALYSIS", "SAFETY_RISK", "QA_QC_NONCONFORMITY"} and self._has_short_root_cause_blocks(record):
            issues.append("Root cause blocks are too short for field troubleshooting.")

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
            lower_text = text.lower()
            for phrase in self._GENERIC_PHRASES:
                if phrase in lower_text:
                    issues.append(f"{name} contains generic fallback text: {phrase}.")
            if topic_intent is not None:
                for issue in self._text_semantic_issues(name, text, topic_intent):
                    issues.append(issue)
        return EngineeringQualityReport(accepted=not issues, issues=tuple(issues))

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
                if term in normalized and term not in topic_intent.normalized_topic:
                    issues.append(f"{name} forces a failure-template detail into {topic_intent.topic_type}: {term}.")
        domain_forbidden = {
            "WELDING_ENGINEERING": ("vong bi", "bom thuy luc", "cau truc dut cap"),
            "HYDRAULIC_PNEUMATIC": ("ro khi duong han", "chieu day son", "cap cau truc"),
            "CRANE_LIFTING": ("ro khi duong han", "bom thuy luc mat ap", "son bong troc"),
            "TPM_LEAN_KAIZEN": ("vong bi bi keu", "bom thuy luc mat ap", "duong han saw ro khi"),
        }
        for term in domain_forbidden.get(topic_intent.primary_domain, ()):
            if term in normalized and term not in topic_intent.normalized_topic:
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
        replacements = str.maketrans(
            {
                "Đ": "D",
                "đ": "d",
                "ă": "a",
                "â": "a",
                "á": "a",
                "à": "a",
                "ả": "a",
                "ã": "a",
                "ạ": "a",
                "é": "e",
                "è": "e",
                "ẻ": "e",
                "ẽ": "e",
                "ẹ": "e",
                "ê": "e",
                "í": "i",
                "ì": "i",
                "ỉ": "i",
                "ĩ": "i",
                "ị": "i",
                "ó": "o",
                "ò": "o",
                "ỏ": "o",
                "õ": "o",
                "ọ": "o",
                "ô": "o",
                "ơ": "o",
                "ú": "u",
                "ù": "u",
                "ủ": "u",
                "ũ": "u",
                "ụ": "u",
                "ư": "u",
                "ý": "y",
                "ỳ": "y",
                "ỷ": "y",
                "ỹ": "y",
                "ỵ": "y",
            }
        )
        return re.sub(r"\s+", " ", value.translate(replacements).lower())
