from __future__ import annotations

from dataclasses import dataclass, field
import re


_CATEGORY_RULES = {
    "Maintenance": (
        "maintenance",
        "repair",
        "shutdown",
        "overhaul",
        "inspection",
        "condition monitoring",
        "bảo trì",
        "bao tri",
        "sửa chữa",
        "sua chua",
        "đại tu",
        "dai tu",
        "hỏng",
        "hong",
        "sự cố",
        "su co",
    ),
    "Quality": (
        "quality",
        "inspection",
        "defect",
        "tolerance",
        "testing",
        "nonconformance",
        "rework",
        "chất lượng",
        "chat luong",
        "kiểm tra",
        "kiem tra",
        "lỗi",
        "loi",
        "khuyết tật",
        "khuyet tat",
        "fit up",
        "fit-up",
        "khe hở",
        "khe ho",
        "mối hàn",
        "moi han",
        "crack",
        "nứt",
        "nut",
        "porosity",
        "rỗ khí",
        "ro khi",
        "lack of fusion",
        "không ngấu",
        "khong ngau",
    ),
    "Safety": (
        "safety",
        "hazard",
        "incident",
        "permit",
        "lockout",
        "confined space",
        "ppe",
        "an toàn",
        "an toan",
        "nguy hiểm",
        "nguy hiem",
        "tai nạn",
        "tai nan",
        "pccc",
        "loto",
    ),
    "Production": (
        "production",
        "throughput",
        "capacity",
        "line",
        "bottleneck",
        "yield",
        "cycle time",
        "sản xuất",
        "san xuat",
        "năng suất",
        "nang suat",
        "công suất",
        "cong suat",
        "tiến độ",
        "tien do",
    ),
    "Design": (
        "design",
        "specification",
        "drawing",
        "prototype",
        "material selection",
        "engineering change",
        "thiết kế",
        "thiet ke",
        "bản vẽ",
        "ban ve",
        "thông số kỹ thuật",
        "thong so ky thuat",
    ),
}

_PROCESS_RULES = {
    "Welding": (
        "welding",
        "hàn",
        "han",
    ),
    "Painting": (
        "painting",
        "sơn",
        "son",
    ),
    "Blasting": (
        "blasting",
        "phun bi",
    ),
    "Cutting": (
        "cutting",
        "cắt",
        "cat",
    ),
    "Machining": (
        "machining",
        "gia công",
        "gia cong",
    ),
    "Assembly": (
        "assembly",
        "lắp ráp",
        "lap rap",
    ),
    "Inspection": (
        "inspection",
        "kiểm tra",
        "kiem tra",
    ),
    "Fabrication": (
        "fabrication",
        "cutting",
        "cắt",
        "cat",
        "forming",
        "bending",
        "machining",
        "gia công",
        "gia cong",
        "welding",
        "hàn",
        "han",
    ),
    "Installation": (
        "installation",
        "fit up",
        "fit-up",
        "fastening",
        "alignment",
        "commissioning",
    ),
    "Heat Treatment": (
        "heat treatment",
        "annealing",
        "quenching",
        "tempering",
        "normalizing",
    ),
    "Surface Treatment": (
        "surface",
        "coating",
        "painting",
        "sơn",
        "son",
        "galvanizing",
        "blasting",
        "phun bi",
        "passivation",
    ),
    "Quality Control": (
        "quality control",
        "inspection",
        "kiểm tra",
        "kiem tra",
        "qa",
        "qc",
        "ndt",
        "ultrasonic",
        "radiography",
        "dimensional",
    ),
}

_OPERATION_RULES = {
    "Inspect": (
        "inspect",
        "inspection",
        "kiểm tra",
        "kiem tra",
        "audit",
        "verify",
        "measure",
        "test",
    ),
    "Optimize": (
        "optimize",
        "improve",
        "cải tiến",
        "cai tien",
        "reduce",
        "increase",
        "debottleneck",
        "lean",
    ),
    "Troubleshoot": (
        "troubleshoot",
        "failure",
        "root cause",
        "breakdown",
        "hỏng",
        "hong",
        "sự cố",
        "su co",
        "diagnose",
        "corrective action",
    ),
    "Plan": (
        "plan",
        "schedule",
        "lập kế hoạch",
        "lap ke hoach",
        "estimate",
        "forecast",
        "resource",
    ),
    "Control": (
        "control",
        "monitor",
        "standardize",
        "calibrate",
        "validate",
        "kiểm soát",
        "kiem soat",
    ),
}

_RISK_RULES = {
    "High Safety Risk": (
        "fatality",
        "explosion",
        "fire",
        "confined space",
        "lockout",
        "hazardous",
        "nguy hiểm",
        "nguy hiem",
        "tai nạn",
        "tai nan",
        "cháy nổ",
        "chay no",
    ),
    "Quality Risk": (
        "defect",
        "crack",
        "nứt",
        "nut",
        "corrosion",
        "contamination",
        "nonconformance",
        "out of tolerance",
        "distortion",
        "biến dạng",
        "bien dang",
        "porosity",
        "rỗ khí",
        "ro khi",
        "lack of fusion",
        "không ngấu",
        "khong ngau",
    ),
    "Schedule Risk": (
        "delay",
        "chậm tiến độ",
        "cham tien do",
        "downtime",
        "bottleneck",
        "critical path",
        "late",
    ),
    "Cost Risk": (
        "scrap",
        "phế phẩm",
        "phe pham",
        "rework",
        "làm lại",
        "lam lai",
        "waste",
        "overrun",
        "inefficiency",
    ),
}

_STANDARD_RULES = {
    "ISO 9001": (
        "iso 9001",
        "quality management",
        "quản lý chất lượng",
        "quan ly chat luong",
        "qms",
    ),
    "ISO 14001": (
        "iso 14001",
        "environmental",
        "ems",
    ),
    "ISO 45001": (
        "iso 45001",
        "occupational health",
        "ohs",
        "safety management",
        "an toàn lao động",
        "an toan lao dong",
        "quản lý an toàn",
        "quan ly an toan",
    ),
    "ASME": (
        "asme",
        "pressure vessel",
        "boiler",
        "piping",
    ),
    "AWS D1.1": (
        "aws d1.1",
        "structural welding",
        "welding code",
        "hàn kết cấu",
        "han ket cau",
        "quy phạm hàn",
        "quy pham han",
    ),
    "ISO 3834": (
        "iso 3834",
        "welding quality",
        "chất lượng hàn",
        "chat luong han",
        "yêu cầu chất lượng hàn",
        "yeu cau chat luong han",
    ),
    "EN 1090": (
        "en 1090",
        "structural steel",
        "steel structure execution",
        "kết cấu thép",
        "ket cau thep",
        "thi công kết cấu thép",
        "thi cong ket cau thep",
    ),
    "AISC": (
        "aisc",
        "steel construction",
        "american institute of steel construction",
        "kết cấu thép mỹ",
        "ket cau thep my",
        "tiêu chuẩn thép mỹ",
        "tieu chuan thep my",
    ),
    "ASTM": (
        "astm",
        "material standard",
        "test method",
    ),
}


@dataclass(frozen=True)
class TopicAnalysis:
    original_topic: str
    search_query: str
    keywords: list[str] = field(default_factory=list)
    normalized_topic: str = ""
    category: str = "General"
    process: str = "Unknown"
    operation: str = ""
    risk: str = ""
    standards: list[str] = field(default_factory=list)


class TopicAnalyzer:
    def analyze(self, topic: str) -> TopicAnalysis:
        clean_topic = self._clean(topic)
        normalized_topic = self._normalize(clean_topic)
        return TopicAnalysis(
            original_topic=topic,
            search_query=clean_topic,
            keywords=self._keywords(clean_topic),
            normalized_topic=normalized_topic,
            category=self._match_rule(normalized_topic, _CATEGORY_RULES, "General"),
            process=self._match_rule(normalized_topic, _PROCESS_RULES, "Unknown"),
            operation=self._match_rule(normalized_topic, _OPERATION_RULES, ""),
            risk=self._match_rule(normalized_topic, _RISK_RULES, ""),
            standards=self._matching_rules(normalized_topic, _STANDARD_RULES),
        )

    def _normalize(self, topic: str) -> str:
        return self._clean(topic).lower()

    def _clean(self, topic: str) -> str:
        return re.sub(r"\s+", " ", re.sub(r"[-_,.:;]+", " ", topic)).strip()

    def _match_rule(
        self,
        normalized_topic: str,
        rules: dict[str, tuple[str, ...]],
        default: str,
    ) -> str:
        for value, terms in rules.items():
            if any(self._normalize(term) in normalized_topic for term in terms):
                return value

        return default

    def _matching_rules(
        self,
        normalized_topic: str,
        rules: dict[str, tuple[str, ...]],
    ) -> list[str]:
        return [
            value
            for value, terms in rules.items()
            if any(self._normalize(term) in normalized_topic for term in terms)
        ]

    def _keywords(self, topic: str) -> list[str]:
        words = []

        for raw_word in self._clean(topic).split():
            word = raw_word.strip("!?()[]{}\"'").lower()
            if len(word) >= 3 and word not in words:
                words.append(word)

        return words
