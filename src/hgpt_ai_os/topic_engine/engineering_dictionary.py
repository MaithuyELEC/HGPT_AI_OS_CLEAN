from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EngineeringConcept:
    canonical: str
    category: str
    aliases: tuple[str, ...]
    causes: tuple[str, ...] = ()
    inspections: tuple[str, ...] = ()
    actions: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()


CONCEPTS: tuple[EngineeringConcept, ...] = (
    EngineeringConcept("SAW", "Process", ("saw", "submerged arc", "hàn saw"), ("wet flux", "rust", "oil", "incorrect travel speed"), ("VT", "UT", "weld parameter log"), ("dry flux", "clean joint", "confirm voltage/current/travel speed"), ("lack of fusion", "porosity", "slag inclusion")),
    EngineeringConcept("MIG welding", "Process", ("mig", "gmaw", "hàn mig", "mối hàn mig"), ("dirty edge", "unstable shielding gas", "wrong torch angle"), ("VT", "MT", "gas flow check"), ("clean edge", "verify gas", "lock welding parameters"), ("porosity", "undercut", "rework")),
    EngineeringConcept("Wire", "Material", ("wire", "dây hàn"), ("wrong diameter", "rusted wire"), ("wire spool check",), ("replace damaged wire",), ("arc instability",)),
    EngineeringConcept("Flux", "Material", ("flux", "thuốc hàn"), ("wet flux", "contamination"), ("dryness check",), ("bake and store flux correctly",), ("porosity", "slag")),
    EngineeringConcept("Travel Speed", "Measurement", ("travel speed", "tốc độ hàn"), ("too fast", "too slow"), ("parameter log",), ("set WPS range",), ("undercut", "low heat input")),
    EngineeringConcept("Voltage", "Measurement", ("voltage", "điện áp", "áp hàn"), ("too high", "too low"), ("machine display check",), ("set approved WPS value",), ("spatter", "undercut")),
    EngineeringConcept("Current", "Measurement", ("current", "dòng hàn", "amperage"), ("wrong current range",), ("clamp meter",), ("reset welding current",), ("lack of penetration")),
    EngineeringConcept("Heat Input", "Measurement", ("heat input", "nhiệt đầu vào"), ("low heat input", "excessive heat input"), ("WPS calculation",), ("balance current voltage and speed",), ("distortion", "lack of fusion")),
    EngineeringConcept("Porosity", "Defect", ("porosity", "rỗ khí", "ro khi"), ("moisture", "oil", "rust", "unstable shielding gas"), ("VT", "RT", "UT"), ("remove defect", "clean surface", "reweld"), ("rejection", "leak path")),
    EngineeringConcept("Undercut", "Defect", ("undercut", "cháy cạnh"), ("high voltage", "wrong travel speed", "poor angle"), ("VT", "weld gauge"), ("grind and repair", "adjust parameters"), ("fatigue crack initiation",)),
    EngineeringConcept("Slag", "Defect", ("slag", "xỉ hàn", "slag inclusion"), ("poor cleaning", "wrong angle"), ("VT", "UT"), ("remove slag between passes",), ("inclusion rejection",)),
    EngineeringConcept("Penetration", "Defect", ("penetration", "ngấu", "thiếu ngấu"), ("low current", "bad fit-up", "low heat input"), ("UT", "macro test"), ("correct joint prep", "increase qualified heat input"), ("structural weakness",)),
    EngineeringConcept("Laser cutting", "Process", ("laser", "cắt laser"), ("dirty lens", "wrong focus", "gas pressure issue"), ("kerf inspection", "lens inspection"), ("clean lens", "set focus", "verify gas"), ("bad kerf", "dross")),
    EngineeringConcept("Nozzle", "Component", ("nozzle", "đầu phun"), ("wear", "misalignment"), ("visual check",), ("replace nozzle",), ("poor cut quality",)),
    EngineeringConcept("Lens", "Component", ("lens", "thấu kính"), ("dust", "heat damage"), ("lens inspection",), ("clean or replace lens",), ("laser power loss",)),
    EngineeringConcept("Gas", "Material", ("gas", "khí", "shielding gas", "assist gas"), ("low flow", "contamination"), ("flow meter", "pressure check"), ("set correct pressure and flow",), ("porosity", "poor kerf")),
    EngineeringConcept("Kerf", "Measurement", ("kerf", "rãnh cắt"), ("wrong focus", "bad nozzle"), ("kerf width check",), ("adjust focus and speed",), ("fit-up error",)),
    EngineeringConcept("Focus", "Measurement", ("focus", "tiêu điểm"), ("wrong focus height",), ("focus test",), ("reset focus",), ("dross", "rough edge")),
    EngineeringConcept("Piercing", "Process", ("piercing", "đục lỗ laser"), ("wrong pierce time",), ("pierce quality check",), ("adjust pierce parameters",), ("splash", "edge damage")),
    EngineeringConcept("Grinding", "Process", ("grinding", "mài", "mài sửa"), ("over grinding", "wrong disc"), ("profile check",), ("control removal depth",), ("dimension loss", "surface damage")),
    EngineeringConcept("Bearing", "Component", ("bearing", "ổ bi", "bạc đạn"), ("poor lubrication", "misalignment", "dust"), ("vibration", "temperature", "noise"), ("lubricate", "align", "replace bearing"), ("machine stop", "shaft damage")),
    EngineeringConcept("Rotor", "Component", ("rotor",), ("imbalance", "dust buildup"), ("vibration check",), ("balance rotor",), ("motor vibration",)),
    EngineeringConcept("Brush", "Component", ("brush", "chổi than"), ("wear", "dust"), ("visual inspection",), ("replace brush",), ("sparking",)),
    EngineeringConcept("Switch", "Component", ("switch", "công tắc"), ("loose contact",), ("continuity check",), ("replace switch",), ("unsafe start",)),
    EngineeringConcept("Gear", "Component", ("gear", "bánh răng"), ("wear", "poor lubrication"), ("backlash check",), ("lubricate or replace",), ("gearbox failure",)),
    EngineeringConcept("Dust", "Risk", ("dust", "bụi"), ("poor housekeeping",), ("visual inspection",), ("clean and isolate source",), ("fire risk", "machine wear")),
    EngineeringConcept("5S", "Process", ("5s", "kaizen", "lean"), ("undefined location", "weak daily audit"), ("5S audit", "shadow board check"), ("sort set shine standardize sustain", "mark material flow"), ("waiting waste", "trip hazard")),
    EngineeringConcept("Visual management", "Tool", ("visual", "shadow board", "quản lý trực quan"), ("missing labels",), ("area audit",), ("label tools and material lanes",), ("search time",)),
    EngineeringConcept("Material Flow", "Process", ("material flow", "luồng vật tư"), ("cross flow", "waiting waste"), ("layout walk",), ("separate input WIP output lanes",), ("waiting waste", "handling damage")),
    EngineeringConcept("Painting", "Process", ("painting", "sơn", "coating", "sơn phủ"), ("humidity", "poor blast profile", "dust"), ("DFT", "adhesion", "dew point"), ("control surface prep and environment",), ("corrosion", "recoat")),
    EngineeringConcept("DFT", "Measurement", ("dft", "thickness", "độ dày màng sơn"), ("uneven application",), ("DFT gauge",), ("repair low or high DFT areas",), ("coating failure",)),
    EngineeringConcept("Adhesion", "Measurement", ("adhesion", "độ bám dính"), ("contamination", "wrong profile"), ("adhesion test",), ("reblast and repaint failed area",), ("peeling",)),
    EngineeringConcept("Blast Profile", "Measurement", ("blast", "profile", "phun bi", "độ nhám"), ("wrong abrasive", "low profile"), ("profile tape",), ("reset blasting parameters",), ("poor coating adhesion")),
    EngineeringConcept("Humidity", "Measurement", ("humidity", "độ ẩm", "dew point"), ("high humidity", "surface condensation"), ("dew point meter",), ("hold painting until condition is acceptable",), ("blistering",)),
    EngineeringConcept("Maintenance", "Process", ("maintenance", "bảo trì", "bao tri"), ("reactive maintenance", "missing schedule"), ("PM checklist", "condition monitoring"), ("plan preventive maintenance",), ("downtime",)),
    EngineeringConcept("Alignment", "Measurement", ("alignment", "căn chỉnh", "dong tam"), ("misalignment",), ("laser alignment", "straight edge"), ("align coupling and shaft",), ("bearing damage",)),
    EngineeringConcept("Lubrication", "Process", ("lubrication", "bôi trơn", "boi tron"), ("wrong grease", "low grease"), ("lubrication log",), ("apply correct lubricant on schedule",), ("bearing heat",)),
    EngineeringConcept("Motor", "Machine", ("motor", "động cơ", "dong co"), ("overload", "poor cooling", "bearing fault"), ("current", "temperature", "vibration"), ("clean cooling path", "check load", "inspect bearing"), ("overheat", "unplanned stop")),
    EngineeringConcept("Gearbox", "Machine", ("gearbox", "hộp số"), ("low oil", "gear wear"), ("oil level", "vibration"), ("change oil", "inspect gear"), ("drive failure",)),
    EngineeringConcept("Vibration", "Measurement", ("vibration", "rung", "độ rung"), ("imbalance", "misalignment", "bearing fault"), ("vibration reading",), ("balance align and inspect bearing",), ("fatigue", "downtime")),
)


def all_concepts() -> tuple[EngineeringConcept, ...]:
    return CONCEPTS
