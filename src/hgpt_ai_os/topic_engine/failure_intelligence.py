from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_FAILURE_FIELDS = (
    "symptoms",
    "root_causes",
    "failure_mechanism",
    "inspection_points",
    "measurements",
    "engineering_calculation",
    "standards",
    "repair_steps",
    "verification_steps",
    "preventive_actions",
    "engineering_notes",
    "common_mistakes",
    "lessons_learned",
    "safety_notes",
)


@dataclass(frozen=True)
class FailureProfile:
    key: str
    failure_mode: str
    symptoms: tuple[str, ...]
    root_causes: tuple[str, ...]
    failure_mechanism: tuple[str, ...]
    inspection_points: tuple[str, ...]
    measurements: tuple[str, ...]
    engineering_calculation: tuple[str, ...]
    standards: tuple[str, ...]
    repair_steps: tuple[str, ...]
    verification_steps: tuple[str, ...]
    preventive_actions: tuple[str, ...]
    engineering_notes: tuple[str, ...]
    common_mistakes: tuple[str, ...]
    lessons_learned: tuple[str, ...]
    safety_notes: tuple[str, ...]

    def as_context(self) -> dict[str, tuple[str, ...]]:
        return {
            "failure_mode": (self.failure_mode,),
            "symptoms": self.symptoms,
            "root_causes": self.root_causes,
            "failure_mechanism": self.failure_mechanism,
            "inspection_points": self.inspection_points,
            "measurements": self.measurements,
            "engineering_calculation": self.engineering_calculation,
            "standards": self.standards,
            "repair_steps": self.repair_steps,
            "verification_steps": self.verification_steps,
            "preventive_actions": self.preventive_actions,
            "engineering_notes": self.engineering_notes,
            "common_mistakes": self.common_mistakes,
            "lessons_learned": self.lessons_learned,
            "safety_notes": self.safety_notes,
        }


class FailureIntelligenceLibrary:
    def __init__(self, path: Path | None = None, locale: str = "vi") -> None:
        self.path = path or Path(__file__).with_name("failure_intelligence_library.json")
        self.locale = locale if locale in {"vi", "en"} else "vi"
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.profiles = {
            profile.key: profile
            for profile in (self._profile(item) for item in data.get("profiles", ()))
        }

    def get(self, key: str) -> FailureProfile | None:
        return self.profiles.get(key)

    def _profile(self, item: dict[str, Any]) -> FailureProfile:
        missing = [field for field in REQUIRED_FAILURE_FIELDS if not item.get(field)]
        if missing:
            raise ValueError(f"Failure profile {item.get('key', '<unknown>')} missing: {', '.join(missing)}")
        return FailureProfile(
            key=str(item["key"]),
            failure_mode=self._text(item.get("failure_mode") or item["key"]),
            symptoms=self._tuple(item["symptoms"]),
            root_causes=self._tuple(item["root_causes"]),
            failure_mechanism=self._tuple(item["failure_mechanism"]),
            inspection_points=self._tuple(item["inspection_points"]),
            measurements=self._tuple(item["measurements"]),
            engineering_calculation=self._tuple(item["engineering_calculation"]),
            standards=self._tuple(item["standards"]),
            repair_steps=self._tuple(item["repair_steps"]),
            verification_steps=self._tuple(item["verification_steps"]),
            preventive_actions=self._tuple(item["preventive_actions"]),
            engineering_notes=self._tuple(item["engineering_notes"]),
            common_mistakes=self._tuple(item["common_mistakes"]),
            lessons_learned=self._tuple(item["lessons_learned"]),
            safety_notes=self._tuple(item["safety_notes"]),
        )

    def _text(self, value: Any) -> str:
        if isinstance(value, dict):
            localized = value.get(self.locale) or value.get("vi") or value.get("en") or value.get("id")
            return str(localized).strip()
        return str(value).strip()

    def _tuple(self, values: list[Any]) -> tuple[str, ...]:
        return tuple(text for value in values if (text := self._text(value)))
