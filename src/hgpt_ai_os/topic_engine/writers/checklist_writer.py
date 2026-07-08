from __future__ import annotations

from hgpt_ai_os.topic_engine.content_planner import ContentPlan
from hgpt_ai_os.topic_engine.reasoning_engine import ReasoningObject
from hgpt_ai_os.topic_engine.writers.channel_writer import inline


_SAW_ITEMS = (
    "Flux dryness and baking record",
    "Wire type, diameter, condition, and storage",
    "Voltage within approved WPS range",
    "Current within approved WPS range",
    "Travel Speed recorded for the joint",
    "Stickout / electrode extension controlled",
    "Plate Cleanliness: no oil, rust, moisture, or loose scale",
    "Flux Depth sufficient to cover the arc",
    "Repair method approved before gouging or grinding",
    "Inspection: VT plus UT/RT when required by ITP",
)

_MAINTENANCE_ITEMS = (
    "Bearing condition: noise, play, seal, and grease condition",
    "Motor current, temperature, cooling path, and terminal tightness",
    "Lubrication type, interval, quantity, and contamination",
    "Alignment of shaft, coupling, pulley, or gearbox",
    "Vibration reading and trend against baseline",
    "Temperature reading at bearing, motor, gearbox, and panel",
    "Fastener torque, base looseness, guard, and bracket condition",
    "Noise source separated from bearing, gear, belt, chain, or fan",
)

_PAINT_ITEMS = (
    "Surface cleanliness before primer",
    "Blast Profile and abrasive condition",
    "Dew point, steel temperature, and humidity record",
    "DFT gauge calibration and spot reading map",
    "Adhesion / cross-cut / pull-off result when required",
    "Repair area feathered, cleaned, repainted, and rechecked",
)

_LASER_5S_ITEMS = (
    "Input material lane separated from finished parts",
    "Nozzle, lens, focus, and assist gas check recorded",
    "Scrap, dross, and offcut bin clearly marked",
    "Shadow board or fixed location for tools and gauges",
    "Daily 5S photo standard and owner assigned",
    "WIP label prevents material mix-up after cutting",
)


class ChecklistWriter:
    def write(self, reasoning: ReasoningObject, plan: ContentPlan) -> str:
        domain_items = self._domain_items(reasoning)
        lines = [
            f"Engineering inspection checklist: {reasoning.topic}",
            "",
            "Scope:",
            f"- [ ] Confirm affected process/equipment: {inline((*reasoning.entities.get('Process'), *reasoning.entities.get('Machine')), reasoning.topic)}",
            f"- [ ] Confirm symptom/failure mode: {inline((*reasoning.problem.symptoms, *reasoning.entities.get('Failure')), reasoning.topic)}",
            "",
            "Domain-specific checks:",
        ]
        lines.extend(f"- [ ] {item}" for item in domain_items)
        lines.extend(["", "Root-cause checks:"])
        lines.extend(f"- [ ] Verify {item}" for item in reasoning.problem.root_cause_candidates[:6])
        lines.extend(["", "Recommended inspection:"])
        lines.extend(f"- [ ] Check {item}" for item in reasoning.problem.recommended_inspection[:6])
        lines.extend(["", "Corrective action:"])
        lines.extend(f"- [ ] Apply {item}" for item in reasoning.corrective_actions[:6])
        lines.extend(["", "Preventive action:"])
        lines.extend(f"- [ ] Standardize {item}" for item in reasoning.preventive_actions[:5])
        lines.extend(
            [
                "",
                "Release decision:",
                "- [ ] Record photo, measurement, responsible person, date, and acceptance criteria.",
                "- [ ] Confirm quality, safety, maintenance, cost, and schedule impacts are closed before handoff.",
            ]
        )
        return "\n".join(lines)

    def _domain_items(self, reasoning: ReasoningObject) -> tuple[str, ...]:
        text = " ".join(
            (
                reasoning.topic.lower(),
                " ".join(reasoning.entities.get("Process")).lower(),
                " ".join(reasoning.entities.get("Machine")).lower(),
                " ".join(reasoning.entities.get("Defect")).lower(),
            )
        )
        items: list[str] = []
        if "saw" in text:
            items.extend(_SAW_ITEMS)
        if any(term in text for term in ("maintenance", "motor", "bearing", "gearbox", "compressor", "máy mài", "grinding")):
            items.extend(_MAINTENANCE_ITEMS)
        if any(term in text for term in ("paint", "sơn", "coating", "adhesion", "peeling")):
            items.extend(_PAINT_ITEMS)
        if any(term in text for term in ("laser", "5s")):
            items.extend(_LASER_5S_ITEMS)
        items.extend(reasoning.problem.recommended_inspection[:4])
        return tuple(dict.fromkeys(items))
