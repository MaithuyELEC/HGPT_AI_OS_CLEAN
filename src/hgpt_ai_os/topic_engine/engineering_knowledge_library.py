from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from hgpt_ai_os.core.resource_path import resource_path


KNOWLEDGE_CONTRACT_FIELDS = (
    "equipment",
    "failure_mechanism",
    "failure_modes",
    "symptoms",
    "root_causes",
    "root_cause_tree",
    "inspection_procedure",
    "measuring_instruments",
    "measurements",
    "acceptance_criteria",
    "related_standards",
    "repair_procedure_sop",
    "verification_after_repair",
    "preventive_maintenance",
    "common_mistakes",
    "lessons_learned",
    "digital_factory_recommendations",
)


@dataclass(frozen=True)
class EngineeringRootCause:
    cause: str
    category: str
    symptoms: tuple[str, ...]
    inspection: tuple[str, ...]
    instruments: tuple[str, ...]
    measurements: tuple[str, ...]
    acceptance: tuple[str, ...]
    repair: tuple[str, ...]
    verification: tuple[str, ...]
    prevention: tuple[str, ...]


@dataclass(frozen=True)
class EngineeringPlaybook:
    key: str
    aliases: tuple[str, ...]
    domain: str
    process: str
    equipment: tuple[str, ...]
    failure_mechanism: tuple[str, ...]
    failure_modes: tuple[str, ...]
    symptoms: tuple[str, ...]
    root_causes: tuple[EngineeringRootCause, ...]
    root_cause_tree: tuple[str, ...]
    inspection_procedure: tuple[str, ...]
    measuring_instruments: tuple[str, ...]
    measurements: tuple[str, ...]
    acceptance_criteria: tuple[str, ...]
    related_standards: tuple[str, ...]
    repair_procedure_sop: tuple[str, ...]
    verification_after_repair: tuple[str, ...]
    preventive_maintenance: tuple[str, ...]
    common_mistakes: tuple[str, ...]
    lessons_learned: tuple[str, ...]
    digital_factory_recommendations: tuple[str, ...]
    production_impact: str
    safety_risks: tuple[str, ...]
    quality_risks: tuple[str, ...]
    hashtags: tuple[str, ...]
    match_groups: tuple[tuple[str, ...], ...]


class EngineeringKnowledgeLibrary:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or resource_path("hgpt_ai_os/topic_engine/engineering_knowledge_playbooks.json")
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        self.contract = tuple(raw["contract"]["required_fields"])
        self.playbooks = {
            playbook.key: playbook
            for playbook in (self._playbook(item) for item in raw.get("playbooks", ()))
        }
        self._validate_library()

    def get(self, key: str) -> EngineeringPlaybook | None:
        return self.playbooks.get(key)

    def all(self) -> tuple[EngineeringPlaybook, ...]:
        return tuple(self.playbooks.values())

    def _playbook(self, item: dict[str, Any]) -> EngineeringPlaybook:
        return EngineeringPlaybook(
            key=str(item["key"]),
            aliases=self._tuple(item.get("aliases")),
            domain=str(item["domain"]),
            process=str(item["process"]),
            equipment=self._tuple(item.get("equipment")),
            failure_mechanism=self._tuple(item.get("failure_mechanism")),
            failure_modes=self._tuple(item.get("failure_modes")),
            symptoms=self._tuple(item.get("symptoms")),
            root_causes=tuple(self._root_cause(root_cause) for root_cause in item.get("root_causes", ())),
            root_cause_tree=self._tuple(item.get("root_cause_tree")),
            inspection_procedure=self._tuple(item.get("inspection_procedure")),
            measuring_instruments=self._tuple(item.get("measuring_instruments")),
            measurements=self._tuple(item.get("measurements")),
            acceptance_criteria=self._tuple(item.get("acceptance_criteria")),
            related_standards=self._tuple(item.get("related_standards")),
            repair_procedure_sop=self._tuple(item.get("repair_procedure_sop")),
            verification_after_repair=self._tuple(item.get("verification_after_repair")),
            preventive_maintenance=self._tuple(item.get("preventive_maintenance")),
            common_mistakes=self._tuple(item.get("common_mistakes")),
            lessons_learned=self._tuple(item.get("lessons_learned")),
            digital_factory_recommendations=self._tuple(item.get("digital_factory_recommendations")),
            production_impact=str(item.get("production_impact", "")),
            safety_risks=self._tuple(item.get("safety_risks")),
            quality_risks=self._tuple(item.get("quality_risks")),
            hashtags=self._tuple(item.get("hashtags")),
            match_groups=tuple(tuple(group) for group in item.get("match_groups", ())),
        )

    def _root_cause(self, item: dict[str, Any]) -> EngineeringRootCause:
        return EngineeringRootCause(
            cause=str(item["cause"]),
            category=str(item["category"]),
            symptoms=self._tuple(item.get("symptoms")),
            inspection=self._tuple(item.get("inspection")),
            instruments=self._tuple(item.get("instruments")),
            measurements=self._tuple(item.get("measurements")),
            acceptance=self._tuple(item.get("acceptance")),
            repair=self._tuple(item.get("repair")),
            verification=self._tuple(item.get("verification")),
            prevention=self._tuple(item.get("prevention")),
        )

    def _validate_library(self) -> None:
        missing_contract = set(KNOWLEDGE_CONTRACT_FIELDS).difference(self.contract)
        if missing_contract:
            raise ValueError(f"Engineering knowledge contract is missing: {sorted(missing_contract)}")
        for playbook in self.playbooks.values():
            missing = [field for field in KNOWLEDGE_CONTRACT_FIELDS if not getattr(playbook, field)]
            if missing:
                raise ValueError(f"{playbook.key} missing knowledge fields: {', '.join(missing)}")
            if len(playbook.root_causes) < 3:
                raise ValueError(f"{playbook.key} must contain at least 3 root causes")
            if len(playbook.root_cause_tree) < 5:
                raise ValueError(f"{playbook.key} must contain a 5 Why tree")
            for root_cause in playbook.root_causes:
                for field in (
                    "symptoms",
                    "inspection",
                    "instruments",
                    "measurements",
                    "acceptance",
                    "repair",
                    "verification",
                    "prevention",
                ):
                    if not getattr(root_cause, field):
                        raise ValueError(f"{playbook.key}/{root_cause.cause} missing {field}")

    def _tuple(self, values: Any) -> tuple[str, ...]:
        if values is None:
            return ()
        return tuple(str(value) for value in values if str(value).strip())
