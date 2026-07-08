from __future__ import annotations

from dataclasses import dataclass

from .entity_extractor import EntityExtraction


@dataclass(frozen=True)
class EngineeringContext:
    graph: dict[str, tuple[str, ...]]
    summary: str


class EngineeringContextBuilder:
    def build(self, topic: str, extraction: EntityExtraction) -> EngineeringContext:
        processes = extraction.get("Process")
        defects = extraction.get("Defect")
        failures = extraction.get("Failure")
        machines = extraction.get("Machine")
        components = extraction.get("Component")
        measurements = extraction.get("Measurement")
        risks = extraction.get("Risk")
        standards = extraction.get("Standard")
        production_terms = extraction.get("Production")

        causes = []
        inspections = []
        actions = []
        concept_risks = []
        for concept in extraction.concepts:
            causes.extend(concept.causes)
            inspections.extend(concept.inspections)
            actions.extend(concept.actions)
            concept_risks.extend(concept.risks)

        graph = {
            "Topic": ((topic or "").strip(),),
            "Process": processes,
            "Defect": defects,
            "Failure": failures,
            "Machine": machines,
            "Component": components,
            "Measurement": measurements,
            "Standard": standards,
            "Production": production_terms,
            "Risk": tuple(dict.fromkeys((*risks, *concept_risks))),
            "Possible Causes": tuple(dict.fromkeys(causes)),
            "Inspection": tuple(dict.fromkeys(inspections)),
            "Repair / Control": tuple(dict.fromkeys(actions)),
        }
        graph = {key: value for key, value in graph.items() if value}

        subject = ", ".join(processes or defects or failures or machines or ("engineering topic",))
        summary = f"{topic} is treated as a {subject} case requiring cause, impact, control, and verification."
        return EngineeringContext(graph, summary)
