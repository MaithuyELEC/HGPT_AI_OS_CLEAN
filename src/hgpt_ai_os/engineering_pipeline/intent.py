from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import asdict, dataclass


SUPPORTED_DOMAINS = (
    "STEEL_STRUCTURE_FABRICATION",
    "WELDING_ENGINEERING",
    "QA_QC_STEEL",
    "MECHANICAL_MAINTENANCE",
    "ELECTROMECHANICAL_MAINTENANCE",
    "HYDRAULIC_PNEUMATIC",
    "CRANE_LIFTING",
    "PRODUCTION_EQUIPMENT",
    "TPM_LEAN_KAIZEN",
    "GENERAL_KNOWLEDGE",
)

TOPIC_TYPES = (
    "FAULT_DIAGNOSIS",
    "DEFECT_ANALYSIS",
    "MAINTENANCE_PROCEDURE",
    "PROCESS_GUIDE",
    "MANAGEMENT_METHOD",
    "INVESTMENT_EVALUATION",
    "TECHNICAL_EXPLANATION",
    "SAFETY_RISK",
    "QA_QC_NONCONFORMITY",
    "LEAN_IMPROVEMENT",
)


@dataclass(frozen=True)
class TopicIntent:
    original_topic: str
    normalized_topic: str
    primary_domain: str
    secondary_domain: str
    topic_type: str
    main_entity: str
    component: str
    observed_condition: str
    expected_user_goal: str
    safety_level: str
    knowledge_grounding_required: bool
    manufacturer_dependency: bool
    standard_dependency: bool
    ambiguity_flags: tuple[str, ...]
    prohibited_assumptions: tuple[str, ...]
    request_id: str
    topic_fingerprint: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def analyze_topic_intent(topic: str) -> TopicIntent:
    original = topic.strip()
    normalized = _normalize(original)
    primary_domain, secondary_domain = _classify_domain(normalized)
    topic_type = _classify_topic_type(normalized, primary_domain)
    entity, component = _entity_and_component(normalized, primary_domain)
    observed_condition = _observed_condition(normalized, topic_type)
    expected_goal = _expected_goal(topic_type)
    safety_level = _safety_level(normalized, primary_domain, topic_type)
    ambiguity = _ambiguity_flags(normalized)
    prohibited = _prohibited_assumptions(topic_type, primary_domain, normalized)
    manufacturer_dependency = bool(
        re.search(r"\b(model|manual|oem|mhi|hmi|password|mat khau|ma loi|bao loi)\b", normalized)
    )
    standard_dependency = primary_domain in {"WELDING_ENGINEERING", "QA_QC_STEEL", "CRANE_LIFTING"}
    grounding_required = topic_type in {
        "FAULT_DIAGNOSIS",
        "DEFECT_ANALYSIS",
        "QA_QC_NONCONFORMITY",
        "SAFETY_RISK",
        "INVESTMENT_EVALUATION",
    }
    fingerprint = hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:12]
    return TopicIntent(
        original_topic=original,
        normalized_topic=normalized,
        primary_domain=primary_domain,
        secondary_domain=secondary_domain,
        topic_type=topic_type,
        main_entity=entity,
        component=component,
        observed_condition=observed_condition,
        expected_user_goal=expected_goal,
        safety_level=safety_level,
        knowledge_grounding_required=grounding_required,
        manufacturer_dependency=manufacturer_dependency,
        standard_dependency=standard_dependency,
        ambiguity_flags=ambiguity,
        prohibited_assumptions=prohibited,
        request_id=f"req_{fingerprint}",
        topic_fingerprint=fingerprint,
    )


def _classify_domain(text: str) -> tuple[str, str]:
    if any(term in text for term in ("tpm", "bao tri tu quan", "tu quan", "5s", "kaizen", "lean", "oee")):
        return "TPM_LEAN_KAIZEN", ""
    if any(term in text for term in ("may cat laser", "may khoan cnc", "may can ton", "day chuyen han dam", "3 trong 1")):
        return "PRODUCTION_EQUIPMENT", ""
    scores = {domain: sum(1 for term in terms if term in text) for domain, terms in _DOMAIN_TERMS.items()}
    primary = max(scores, key=scores.get)
    if scores[primary] <= 0:
        primary = "GENERAL_KNOWLEDGE"
    secondary = ""
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    if len(ranked) > 1 and ranked[1][1] > 0:
        secondary = ranked[1][0]
    return primary, secondary


def _classify_topic_type(text: str, domain: str) -> str:
    if domain == "GENERAL_KNOWLEDGE":
        return "PROCESS_GUIDE"
    if any(term in text for term in ("dau tu", "so sanh", "lua chon", "mua ", "roi", "hoan von")):
        return "INVESTMENT_EVALUATION"
    if any(term in text for term in ("khong ra khi", "bi khoa", "bao loi", "mat ap", "bi nong", "bi keu")):
        return "FAULT_DIAGNOSIS"
    if any(term in text for term in ("5s", "kaizen", "lean", "oee", "giam ", "cai tien", "lang phi")):
        return "LEAN_IMPROVEMENT" if any(term in text for term in ("giam ", "cai tien", "lang phi")) else "MANAGEMENT_METHOD"
    if any(term in text for term in ("tpm", "bao tri tu quan", "tu quan", "quan ly", "planned maintenance")):
        return "MANAGEMENT_METHOD"
    if any(term in text for term in ("ro khi", "nut", "undercut", "chay canh", "bong troc", "cong sau han", "khuyet tat")):
        return "DEFECT_ANALYSIS"
    if any(term in text for term in ("khong dat", "sai kich thuoc", "sai chieu day", "ncr", "capa", "itp")):
        return "QA_QC_NONCONFORMITY"
    if any(term in text for term in ("quy trinh", "phun bi", "son ket cau", "ga dinh", "fit up", "lap rap", "cat ", "khoan")):
        return "PROCESS_GUIDE"
    if any(term in text for term in ("bao tri", "bao duong", "kiem tra cap", "kiem tra dinh ky", "pm ")):
        return "MAINTENANCE_PROCEDURE"
    if any(term in text for term in ("la gi", "hoat dong the nao", "nguyen ly", "giai thich")):
        return "TECHNICAL_EXPLANATION"
    if any(term in text for term in ("mat phanh", "dut cap", "ro ri oxy", "nguy hiem", "an toan")):
        return "SAFETY_RISK"
    if domain in {"WELDING_ENGINEERING", "QA_QC_STEEL", "STEEL_STRUCTURE_FABRICATION"}:
        if any(term in text for term in ("loi", "hong", "mat", "khong", "bi ")):
            return "DEFECT_ANALYSIS"
    return "FAULT_DIAGNOSIS"


def _entity_and_component(text: str, domain: str) -> tuple[str, str]:
    for term, entity, component in _ENTITY_TERMS:
        if term in text:
            return entity, component
    return _DOMAIN_ENTITY[domain], ""


def _observed_condition(text: str, topic_type: str) -> str:
    conditions = (
        "ro khi",
        "bong troc",
        "mat ap",
        "bi nong",
        "bi keu",
        "dut cap",
        "khong ra khi",
        "sai kich thuoc",
        "bi khoa",
        "mat phanh",
    )
    for condition in conditions:
        if condition in text:
            return condition.replace("bi ", "").strip()
    if topic_type in {"MANAGEMENT_METHOD", "PROCESS_GUIDE", "INVESTMENT_EVALUATION", "TECHNICAL_EXPLANATION"}:
        return "none"
    return "condition requires field confirmation"


def _expected_goal(topic_type: str) -> str:
    return {
        "FAULT_DIAGNOSIS": "root cause, inspection, repair decision, verification",
        "DEFECT_ANALYSIS": "defect cause, containment, correction, prevention",
        "MAINTENANCE_PROCEDURE": "safe maintenance procedure and acceptance records",
        "PROCESS_GUIDE": "process control guidance",
        "MANAGEMENT_METHOD": "implementation guidance",
        "INVESTMENT_EVALUATION": "technical and operational investment evaluation",
        "TECHNICAL_EXPLANATION": "technical explanation",
        "SAFETY_RISK": "hazard control and safe response",
        "QA_QC_NONCONFORMITY": "NCR/CAPA disposition and reinspection",
        "LEAN_IMPROVEMENT": "waste reduction and sustainment plan",
    }[topic_type]


def _safety_level(text: str, domain: str, topic_type: str) -> str:
    if topic_type == "SAFETY_RISK" or domain == "CRANE_LIFTING":
        return "high"
    if any(term in text for term in ("dien", "thuy luc", "khi nen", "ap", "laser", "oxy", "phanh", "cap")):
        return "high"
    if domain in {"WELDING_ENGINEERING", "PRODUCTION_EQUIPMENT", "ELECTROMECHANICAL_MAINTENANCE"}:
        return "medium"
    return "normal"


def _ambiguity_flags(text: str) -> tuple[str, ...]:
    flags: list[str] = []
    if "mhi" in text:
        flags.append("MHI may mean HMI; do not assume password bypass or access-code cracking.")
    if "saw" in text:
        flags.append("SAW may refer to submerged arc welding in this domain.")
    return tuple(flags)


def _prohibited_assumptions(topic_type: str, domain: str, text: str) -> tuple[str, ...]:
    prohibited = [
        "unsupported temperature limit",
        "unsupported current limit",
        "unsupported vibration limit",
        "unsupported pressure limit",
        "unsupported dimensional tolerance",
        "invented WPS or welding parameter",
        "invented inspection acceptance value",
        "specific equipment model details not supplied by user",
    ]
    if topic_type in {"MANAGEMENT_METHOD", "PROCESS_GUIDE", "INVESTMENT_EVALUATION", "TECHNICAL_EXPLANATION"}:
        prohibited.extend(
            (
                "specific machine fault",
                "bearing damage",
                "motor current symptom",
                "compressor pressure symptom",
            )
        )
    if "mhi" in text or "hmi" in text:
        prohibited.extend(("manufacturer password", "access-code cracking", "disabling safety interlocks"))
    if domain != "CRANE_LIFTING":
        prohibited.append("crane wire rope content unless the topic is lifting equipment")
    if domain not in {"WELDING_ENGINEERING", "QA_QC_STEEL", "STEEL_STRUCTURE_FABRICATION"}:
        prohibited.append("welding defect content unless the topic is fabrication or QA/QC")
    return tuple(prohibited)


def _normalize(value: str) -> str:
    value = value.replace("Đ", "D").replace("đ", "d")
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = "".join(char for char in normalized if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", ascii_text.lower()).strip()


_DOMAIN_TERMS = {
    "STEEL_STRUCTURE_FABRICATION": (
        "ket cau thep",
        "dam h",
        "cat",
        "khoan",
        "ga dinh",
        "lap rap",
        "chinh thang",
        "phun bi",
        "son",
        "dong goi",
        "lap dung",
    ),
    "WELDING_ENGINEERING": (
        "han",
        "saw",
        "smaw",
        "gmaw",
        "fcaw",
        "tig",
        "wps",
        "pqr",
        "wpq",
        "ndt",
        "ro khi",
        "khuyet tat",
        "pwht",
    ),
    "QA_QC_STEEL": (
        "qa",
        "qc",
        "itp",
        "ncr",
        "capa",
        "aws",
        "3834",
        "1090",
        "aisc",
        "jis",
        "kiem tra",
        "sai kich thuoc",
        "chieu day son",
    ),
    "MECHANICAL_MAINTENANCE": (
        "vong bi",
        "o bi",
        "hop giam toc",
        "khop noi",
        "xich",
        "day dai",
        "puly",
        "bom",
        "quat",
        "may nen",
        "boi tron",
        "can dong",
        "rung",
        "nhiet",
        "mon",
    ),
    "ELECTROMECHANICAL_MAINTENANCE": (
        "dong co",
        "3 pha",
        "contactor",
        "relay",
        "phanh",
        "cam bien",
        "limit switch",
        "bien tan",
        "tu dien",
        "qua tai",
        "mat pha",
        "lech pha",
    ),
    "HYDRAULIC_PNEUMATIC": (
        "thuy luc",
        "khi nen",
        "mat ap",
        "xy lanh",
        "van",
        "loc",
        "tich ap",
        "ro ri",
        "nhiem ban dau",
        "cavitation",
        "may say khi",
        "bo dieu ap",
    ),
    "CRANE_LIFTING": (
        "cau truc",
        "cap nang",
        "cap tai",
        "palang",
        "moc cau",
        "puly cap",
        "tang cuon",
        "ray",
        "bao qua tai",
        "iso 4309",
    ),
    "PRODUCTION_EQUIPMENT": (
        "may cat laser",
        "may khoan cnc",
        "may cua vong",
        "may can ton",
        "may lan ton",
        "day chuyen han dam",
        "3 trong 1",
        "shot blasting",
        "bang tai",
        "may ep",
        "hpu",
    ),
    "TPM_LEAN_KAIZEN": (
        "tpm",
        "bao tri tu quan",
        "tu quan",
        "5s",
        "kaizen",
        "lean",
        "oee",
        "quan ly truc quan",
        "the bat thuong",
        "kiem tra hang ngay",
        "kpi",
    ),
}

_DOMAIN_ENTITY = {
    "STEEL_STRUCTURE_FABRICATION": "steel structure fabrication process",
    "WELDING_ENGINEERING": "welding process",
    "QA_QC_STEEL": "steel QA/QC process",
    "MECHANICAL_MAINTENANCE": "mechanical equipment",
    "ELECTROMECHANICAL_MAINTENANCE": "electromechanical equipment",
    "HYDRAULIC_PNEUMATIC": "hydraulic or pneumatic system",
    "CRANE_LIFTING": "crane and lifting equipment",
    "PRODUCTION_EQUIPMENT": "steel fabrication production equipment",
    "TPM_LEAN_KAIZEN": "factory management system",
    "GENERAL_KNOWLEDGE": "general topic",
}

_ENTITY_TERMS = (
    ("bao tri tu quan", "autonomous maintenance system", "daily inspection and abnormality tagging"),
    ("duong han saw", "SAW weld", "weld bead"),
    ("saw", "SAW weld", "weld bead"),
    ("bom thuy luc", "hydraulic pump", "pump, relief valve, suction line"),
    ("cau truc", "overhead crane", "wire rope, hoist brake, drum, hook"),
    ("cap", "wire rope", "wire rope"),
    ("may cat laser", "laser cutting machine", "cutting gas train"),
    ("may can ton", "roll-forming machine control interface", "HMI/control panel"),
    ("dong co 3 pha", "three-phase motor", "stator, rotor, bearing, cooling fan"),
    ("vong bi", "motor bearing assembly", "bearing"),
    ("o bi", "motor bearing assembly", "bearing"),
    ("son", "steel coating system", "coating layer and substrate"),
    ("dam h", "H-beam fabrication", "web, flange, weld distortion"),
    ("5s", "5S management system", "work area standards"),
    ("day chuyen han dam 3 trong 1", "3-in-1 H-beam welding line", "assembly, welding, straightening stations"),
)
