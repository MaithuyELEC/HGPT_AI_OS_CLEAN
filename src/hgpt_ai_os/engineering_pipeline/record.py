from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class EngineeringRecord:
    topic: str
    domain: str
    primary_domain: str = ""
    secondary_domain: str = ""
    topic_type: str = ""
    main_entity: str = ""
    observed_condition: str = ""
    expected_user_goal: str = ""
    safety_level: str = ""
    request_id: str = ""
    topic_fingerprint: str = ""
    title: str = ""
    problem: str = ""
    equipment: tuple[str, ...] = ()
    subsystem: str = ""
    component: tuple[str, ...] = ()
    failure_symptom: tuple[str, ...] = ()
    operating_context: str = ""
    working_principle: str = ""
    failure_mechanisms: tuple[str, ...] = ()
    root_causes: tuple[str, ...] = ()
    evidence_required: tuple[str, ...] = ()
    inspection_procedure: tuple[str, ...] = ()
    measurements: tuple[str, ...] = ()
    tools_required: tuple[str, ...] = ()
    decision_logic: tuple[str, ...] = ()
    repair_procedure: tuple[str, ...] = ()
    verification: tuple[str, ...] = ()
    acceptance_criteria: tuple[str, ...] = ()
    lessons_learned: tuple[str, ...] = ()
    common_mistakes: tuple[str, ...] = ()
    preventive_maintenance: tuple[str, ...] = ()
    safety_controls: tuple[str, ...] = ()
    kaizen: tuple[str, ...] = ()
    digital_factory_recommendations: tuple[str, ...] = ()
    applicable_standards: tuple[str, ...] = ()
    missing_information: tuple[str, ...] = ()
    ambiguity_flags: tuple[str, ...] = ()
    prohibited_assumptions: tuple[str, ...] = ()
    safe_failure: bool = False
    confidence: float = 0.0
    source_keys: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def tupled(values: Any) -> tuple[str, ...]:
        if values is None:
            return ()
        if isinstance(values, str):
            return (values.strip(),) if values.strip() else ()
        if isinstance(values, dict):
            return (EngineeringRecord._dict_to_text(values),)
        return tuple(EngineeringRecord._item_to_text(value) for value in values if EngineeringRecord._item_to_text(value))

    @staticmethod
    def _item_to_text(value: Any) -> str:
        if isinstance(value, dict):
            return EngineeringRecord._dict_to_text(value)
        return str(value).strip()

    @staticmethod
    def _dict_to_text(values: dict[str, Any]) -> str:
        parts: list[str] = []
        for key, value in values.items():
            label = str(key).replace("_", " ").strip()
            if isinstance(value, (list, tuple, set)):
                text = ", ".join(str(item).strip() for item in value if str(item).strip())
            else:
                text = str(value).strip()
            if label and text:
                parts.append(f"{label}: {text}")
        return ". ".join(parts).strip()

    @classmethod
    def merged_tuple(cls, *values: Any) -> tuple[str, ...]:
        merged: list[str] = []
        seen: set[str] = set()
        for value in values:
            for item in cls.tupled(value):
                key = item.casefold()
                if key not in seen:
                    seen.add(key)
                    merged.append(item)
        return tuple(merged)

    @classmethod
    def from_mapping(cls, values: dict[str, Any]) -> "EngineeringRecord":
        title = str(values.get("title", "")).strip()
        topic = str(values.get("topic", "")).strip() or title
        return cls(
            topic=topic,
            domain=str(values.get("domain", "")).strip(),
            primary_domain=str(values.get("primary_domain", "")).strip(),
            secondary_domain=str(values.get("secondary_domain", "")).strip(),
            topic_type=str(values.get("topic_type", "")).strip(),
            main_entity=str(values.get("main_entity", "")).strip(),
            observed_condition=str(values.get("observed_condition", "")).strip(),
            expected_user_goal=str(values.get("expected_user_goal", "")).strip(),
            safety_level=str(values.get("safety_level", "")).strip(),
            request_id=str(values.get("request_id", "")).strip(),
            topic_fingerprint=str(values.get("topic_fingerprint", "")).strip(),
            title=title,
            problem=str(values.get("problem", "")).strip(),
            equipment=cls.tupled(values.get("equipment")),
            subsystem=str(values.get("subsystem", "")).strip(),
            component=cls.tupled(values.get("component")),
            failure_symptom=cls.merged_tuple(values.get("failure_symptom"), values.get("symptoms")),
            operating_context=str(values.get("operating_context", "")).strip(),
            working_principle=str(values.get("working_principle", "")).strip(),
            failure_mechanisms=cls.tupled(values.get("failure_mechanisms")),
            root_causes=cls.tupled(values.get("root_causes")),
            evidence_required=cls.tupled(values.get("evidence_required")),
            inspection_procedure=cls.merged_tuple(values.get("inspection_procedure"), values.get("inspection")),
            measurements=cls.tupled(values.get("measurements")),
            tools_required=cls.tupled(values.get("tools_required")),
            decision_logic=cls.tupled(values.get("decision_logic")),
            repair_procedure=cls.merged_tuple(values.get("repair_procedure"), values.get("repair")),
            verification=cls.tupled(values.get("verification")),
            acceptance_criteria=cls.tupled(values.get("acceptance_criteria")),
            lessons_learned=cls.tupled(values.get("lessons_learned")),
            common_mistakes=cls.tupled(values.get("common_mistakes")),
            preventive_maintenance=cls.merged_tuple(values.get("preventive_maintenance"), values.get("prevention")),
            safety_controls=cls.tupled(values.get("safety_controls")),
            kaizen=cls.tupled(values.get("kaizen")),
            digital_factory_recommendations=cls.tupled(values.get("digital_factory_recommendations")),
            applicable_standards=cls.tupled(values.get("applicable_standards")),
            missing_information=cls.tupled(values.get("missing_information")),
            ambiguity_flags=cls.tupled(values.get("ambiguity_flags")),
            prohibited_assumptions=cls.tupled(values.get("prohibited_assumptions")),
            safe_failure=bool(values.get("safe_failure", False)),
            confidence=float(values.get("confidence", 0.0) or 0.0),
            source_keys=cls.tupled(values.get("source_keys")),
        )
