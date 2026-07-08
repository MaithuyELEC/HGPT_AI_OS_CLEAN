from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from .engineering_dictionary import EngineeringConcept, all_concepts
from .topic_parser import ParsedTopic


ENTITY_FIELDS = (
    "Equipment",
    "Machine",
    "Process",
    "Material",
    "Component",
    "Defect",
    "Failure",
    "Tool",
    "Standard",
    "Measurement",
    "Risk",
    "System",
    "Production",
    "Department",
    "Role",
)


DOMAIN_PHRASES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("Failure", "continuous breakdown", ("hỏng liên tục", "hong lien tuc", "breakdown", "hư liên tục")),
    ("Failure", "overheating", ("quá nhiệt", "qua nhiet", "overheat", "overheating")),
    ("Failure", "peeling", ("bong tróc", "bong troc", "peeling", "flaking")),
    ("Failure", "air porosity", ("rỗ khí", "ro khi", "porosity", "bọ khí")),
    ("Production", "work in process", ("wip", "bán thành phẩm", "ban thanh pham")),
    ("Production", "hold point", ("hold point", "điểm dừng", "diem dung")),
    ("Production", "rework", ("rework", "sửa lỗi", "sua loi", "sửa hàng")),
    ("Production", "downtime", ("downtime", "dừng máy", "dung may", "ngừng máy")),
    ("Production", "cycle time", ("cycle time", "thời gian chu kỳ", "thoi gian chu ky")),
    ("Production", "handoff", ("handoff", "bàn giao", "ban giao", "chuyển công đoạn")),
    ("Tool", "angle grinder", ("máy mài cầm tay", "may mai cam tay", "angle grinder", "hand grinder")),
    ("Tool", "torque wrench", ("torque wrench", "cờ lê lực", "co le luc")),
    ("Tool", "DFT gauge", ("dft gauge", "máy đo dft", "may do dft")),
)


def _plain(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text or "")
    stripped = "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
    return stripped.replace("đ", "d").replace("Đ", "D").lower()


def _contains_phrase(haystack: str, phrase: str) -> bool:
    pattern = r"(?<!\w)" + re.escape(phrase.lower()) + r"(?!\w)"
    return re.search(pattern, haystack) is not None


@dataclass(frozen=True)
class EntityExtraction:
    entities: dict[str, tuple[str, ...]]
    concepts: tuple[EngineeringConcept, ...]

    def get(self, category: str) -> tuple[str, ...]:
        return self.entities.get(category, ())


class EngineeringEntityExtractor:
    def extract(self, parsed: ParsedTopic) -> EntityExtraction:
        haystack = f"{parsed.normalized} {' '.join(parsed.keywords)}"
        plain_haystack = _plain(haystack)
        found: list[EngineeringConcept] = []
        entities: dict[str, list[str]] = {field: [] for field in ENTITY_FIELDS}

        for concept in all_concepts():
            aliases = tuple(dict.fromkeys((*concept.aliases, concept.canonical.lower())))
            if any(
                _contains_phrase(haystack, alias) or _contains_phrase(plain_haystack, _plain(alias))
                for alias in aliases
            ):
                found.append(concept)
                entities.setdefault(concept.category, []).append(concept.canonical)

        for category, canonical, aliases in DOMAIN_PHRASES:
            if any(
                _contains_phrase(haystack, alias) or _contains_phrase(plain_haystack, _plain(alias))
                for alias in aliases
            ):
                entities.setdefault(category, []).append(canonical)

        for phrase in parsed.phrases:
            if any(marker in phrase for marker in ("máy", "may", "machine")):
                entities.setdefault("Machine", []).append(phrase)
            if any(marker in phrase for marker in ("lỗi", "loi", "hỏng", "hong", "defect", "failure")):
                entities.setdefault("Failure", []).append(phrase)

        if "qaqc" in haystack or "qc" in haystack:
            entities["Department"].append("QA/QC")
            entities["Role"].append("QC Inspector")
        if "supervisor" in haystack or "giám sát" in haystack:
            entities["Role"].append("Supervisor")
        if "iso" in haystack or "aws" in haystack or "astm" in haystack:
            entities["Standard"].append("Referenced standard")

        frozen = {
            field: tuple(dict.fromkeys(values))
            for field, values in entities.items()
            if values
        }
        return EntityExtraction(frozen, tuple(dict.fromkeys(found)))
