from __future__ import annotations

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
    "Tool",
    "Standard",
    "Measurement",
    "Risk",
    "Department",
    "Role",
)


@dataclass(frozen=True)
class EntityExtraction:
    entities: dict[str, tuple[str, ...]]
    concepts: tuple[EngineeringConcept, ...]

    def get(self, category: str) -> tuple[str, ...]:
        return self.entities.get(category, ())


class EngineeringEntityExtractor:
    def extract(self, parsed: ParsedTopic) -> EntityExtraction:
        haystack = f"{parsed.normalized} {' '.join(parsed.keywords)}"
        found: list[EngineeringConcept] = []
        entities: dict[str, list[str]] = {field: [] for field in ENTITY_FIELDS}

        for concept in all_concepts():
            if any(alias in haystack for alias in concept.aliases):
                found.append(concept)
                entities.setdefault(concept.category, []).append(concept.canonical)

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
