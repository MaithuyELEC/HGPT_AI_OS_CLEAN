from __future__ import annotations

from dataclasses import dataclass

from hgpt_ai_os.diagnostics import instrument_runtime_tracing

from .engineering_context import EngineeringContext
from .entity_extractor import EntityExtraction
from .intent_detector import IntentResult


@dataclass(frozen=True)
class ProblemAnalysis:
    symptoms: tuple[str, ...]
    possible_causes: tuple[str, ...]
    immediate_cause: str
    hidden_cause: str
    root_cause_candidates: tuple[str, ...]
    root_cause: str
    production_impact: str
    production_loss: str
    quality_impact: str
    quality_risk: str
    safety_impact: str
    safety_risk: str
    maintenance_risk: str
    cost_impact: str
    schedule_impact: str
    recommended_inspection: tuple[str, ...]
    recommended_action: tuple[str, ...]
    likelihood: str
    severity: str


def _first(values: tuple[str, ...], fallback: str) -> str:
    return values[0] if values else fallback


def _join(values: tuple[str, ...], fallback: str) -> str:
    return ", ".join(values) if values else fallback


class ProblemAnalyzer:
    def analyze(
        self,
        topic: str,
        intent: IntentResult,
        extraction: EntityExtraction,
        context: EngineeringContext,
    ) -> ProblemAnalysis:
        defects = extraction.get("Defect")
        failures = extraction.get("Failure")
        machines = extraction.get("Machine")
        components = extraction.get("Component")
        processes = extraction.get("Process")
        measurements = extraction.get("Measurement")
        standards = extraction.get("Standard")
        risks = context.graph.get("Risk", ())
        causes = context.graph.get("Possible Causes", ())
        inspections = context.graph.get("Inspection", ())
        actions = context.graph.get("Repair / Control", ())

        symptoms = defects or failures or measurements or machines or ((topic or "engineering condition").strip(),)
        root_causes = causes[:5] or (
            "unclear standard work",
            "missing inspection evidence",
            "weak parameter control",
            "late containment of abnormal condition",
        )
        immediate = _first(
            defects or failures or measurements,
            f"abnormal condition on {_join(processes or machines, 'the production process')}",
        )
        hidden = _first(
            tuple(cause for cause in root_causes if "missing" in cause or "poor" in cause or "weak" in cause),
            f"control plan does not yet prove {_join(inspections[:2], 'inspection evidence')}",
        )
        root = _first(
            tuple(cause for cause in root_causes if cause != immediate),
            "standard work and release criteria are not tight enough",
        )
        equipment = _join(machines or components or processes, "the affected equipment or work cell")
        severity = "High" if defects or "Failure" == intent.intent else "Medium"
        likelihood = "Medium-High" if causes else "Medium"
        recommended_inspection = inspections[:6] or (
            "visual evidence",
            "measurement record",
            "parameter log",
            "responsible-person release",
        )
        recommended_action = actions[:6] or (
            "contain the abnormal condition",
            "confirm acceptance criteria",
            "correct the parameter or component",
            "record release evidence",
        )
        quality_risk = (
            f"{_join(defects or failures, 'The defect')} can pass downstream if acceptance criteria, "
            "measurement evidence, and repair records are not closed."
        )
        safety_risk = (
            f"{equipment} may expose operators to stored energy, heat, sharp edges, moving parts, "
            "dust, lifting hazards, or blocked access during correction."
        )
        maintenance_risk = (
            f"Repeat abnormality on {equipment} can shorten bearing, motor, drive, seal, or tooling life "
            "when lubrication, alignment, temperature, and vibration evidence are missing."
        )

        return ProblemAnalysis(
            symptoms=tuple(dict.fromkeys(symptoms)),
            possible_causes=tuple(dict.fromkeys(causes or root_causes)),
            immediate_cause=immediate,
            hidden_cause=hidden,
            root_cause_candidates=tuple(dict.fromkeys(root_causes)),
            root_cause=root,
            production_impact=f"May slow {equipment}, create rework, or interrupt handoff to the next operation.",
            production_loss="Lost output appears as waiting time, retest time, rework hours, extra handling, and delayed release.",
            quality_impact=quality_risk,
            quality_risk=quality_risk,
            safety_impact=safety_risk,
            safety_risk=safety_risk,
            maintenance_risk=maintenance_risk,
            cost_impact="Cost grows through repeated labor, consumables, inspection, repair material, energy loss, and delayed delivery.",
            schedule_impact=f"Schedule risk increases when {_join(standards or inspections[:2], 'release evidence')} is not ready before the next handoff.",
            recommended_inspection=tuple(dict.fromkeys(recommended_inspection)),
            recommended_action=tuple(dict.fromkeys(recommended_action)),
            likelihood=likelihood,
            severity=severity,
        )


instrument_runtime_tracing(globals())
