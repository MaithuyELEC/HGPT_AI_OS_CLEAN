from __future__ import annotations

from dataclasses import dataclass

from .topic_parser import ParsedTopic


@dataclass(frozen=True)
class IntentResult:
    intent: str
    confidence: float
    signals: tuple[str, ...]


_INTENT_SIGNALS = {
    "Problem": ("lỗi", "loi", "problem", "issue", "defect", "porosity", "undercut", "rỗ", "hỏng", "fail"),
    "Question": ("why", "how", "what", "vì sao", "tai sao", "làm sao", "?"),
    "Maintenance": ("maintenance", "bảo trì", "bao tri", "lubrication", "bearing", "motor"),
    "Inspection": ("inspection", "kiểm tra", "kiem tra", "qaqc", "qc", "checklist", "nghiệm thu"),
    "Failure": ("failure", "fail", "hỏng", "dừng máy", "quá nhiệt", "overheat", "ncr"),
    "Improvement": ("improvement", "cải tiến", "kaizen", "5s", "lean", "optimize"),
    "Knowledge": ("knowledge", "kiến thức", "guide", "hướng dẫn", "standard"),
    "Procedure": ("procedure", "quy trình", "sop", "work instruction", "cách"),
    "Comparison": ("compare", "comparison", "so sánh", "vs", "versus"),
    "Optimization": ("optimization", "tối ưu", "toi uu", "năng suất", "productivity"),
}


class IntentDetector:
    def detect(self, parsed: ParsedTopic) -> IntentResult:
        haystack = f"{parsed.normalized} {' '.join(parsed.keywords)}"
        scores: dict[str, int] = {}
        signals: dict[str, list[str]] = {}
        for intent, terms in _INTENT_SIGNALS.items():
            hits = [term for term in terms if term in haystack]
            if hits:
                scores[intent] = len(hits)
                signals[intent] = hits

        if not scores:
            return IntentResult("Knowledge", 0.35, ())

        intent = max(scores, key=lambda key: (scores[key], key == "Problem"))
        confidence = min(0.95, 0.45 + scores[intent] * 0.18)
        return IntentResult(intent, confidence, tuple(signals[intent]))
