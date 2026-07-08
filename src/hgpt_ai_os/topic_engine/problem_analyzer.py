from __future__ import annotations

from dataclasses import dataclass

from .engineering_context import EngineeringContext
from .entity_extractor import EntityExtraction
from .intent_detector import IntentResult


@dataclass(frozen=True)
class ProblemAnalysis:
    symptoms: tuple[str, ...]
    possible_causes: tuple[str, ...]
    root_cause_candidates: tuple[str, ...]
    production_impact: str
    quality_impact: str
    safety_impact: str
    cost_impact: str
    schedule_impact: str
    likelihood: str
    severity: str


class ProblemAnalyzer:
    def analyze(
        self,
        topic: str,
        intent: IntentResult,
        extraction: EntityExtraction,
        context: EngineeringContext,
    ) -> ProblemAnalysis:
        defects = extraction.get("Defect")
        machines = extraction.get("Machine")
        measurements = extraction.get("Measurement")
        risks = context.graph.get("Risk", ())
        causes = context.graph.get("Possible Causes", ())

        symptoms = defects or measurements or machines or ((topic or "engineering condition").strip(),)
        root_causes = causes[:4] or ("unclear standard work", "missing inspection evidence", "weak parameter control")
        severity = "High" if defects or "Failure" == intent.intent else "Medium"
        likelihood = "Medium-High" if causes else "Medium"

        return ProblemAnalysis(
            symptoms=tuple(dict.fromkeys(symptoms)),
            possible_causes=tuple(dict.fromkeys(causes or root_causes)),
            root_cause_candidates=tuple(dict.fromkeys(root_causes)),
            production_impact="May slow the work cell, create rework, or interrupt handoff to the next operation.",
            quality_impact="May create rejection risk unless evidence, acceptance criteria, and repair controls are clear.",
            safety_impact="Requires checking exposure to heat, moving equipment, dust, sharp edges, or blocked access.",
            cost_impact="Rework, waiting time, extra consumables, and repeated inspection can increase total cost.",
            schedule_impact="Open defects or unclear release criteria can delay delivery and downstream assembly.",
            likelihood=likelihood,
            severity=severity,
        )
