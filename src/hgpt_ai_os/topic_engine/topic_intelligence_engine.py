from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from hgpt_ai_os.diagnostics import instrument_runtime_tracing, module_loaded, trace_call

from .entity_extractor import EngineeringEntityExtractor
from .failure_intelligence import FailureIntelligenceLibrary
from .intent_detector import IntentDetector
from .topic_context import TopicContext
from .topic_parser import TopicParser


def normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value or "")
    stripped = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    stripped = stripped.replace("đ", "d").replace("Đ", "D").lower()
    return re.sub(r"[^a-z0-9]+", " ", stripped).strip()


def contains_phrase(haystack: str, phrase: str) -> bool:
    normalized = normalize_text(phrase)
    if not normalized:
        return False
    return re.search(r"(?<![a-z0-9])" + re.escape(normalized) + r"(?![a-z0-9])", haystack) is not None


@dataclass(frozen=True)
class ProfileEntry:
    canonical: str
    category: str
    aliases: tuple[str, ...]
    domain: str = ""
    parent: str = ""
    severity: str = ""


class TopicProfileStore:
    def __init__(self, path: Path | None = None) -> None:
        trace_call("TopicProfileStore.__init__", self)
        self.path = path or Path(__file__).with_name("topic_intelligence_profiles.json")
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.entities = self._entries(data.get("entities", ()))
        self.failures = self._entries(data.get("failures", ()), category="Failure")
        self.intents = self._entries(data.get("intents", ()), category="Intent")
        self.standards = self._entries(data.get("standards", ()), category="Standard")
        self.severity_rules = tuple(data.get("severity_rules", ()))
        self.playbooks = tuple(data.get("playbooks", ()))

    def _entries(self, raw_entries: list[dict[str, Any]], category: str = "") -> tuple[ProfileEntry, ...]:
        return tuple(
            ProfileEntry(
                canonical=str(item["canonical"]),
                category=str(item.get("category") or category),
                aliases=tuple(str(alias) for alias in item.get("aliases", ())),
                domain=str(item.get("domain", "")),
                parent=str(item.get("parent", "")),
                severity=str(item.get("severity", "")),
            )
            for item in raw_entries
        )


class EntityExtractor:
    def __init__(self, profiles: TopicProfileStore) -> None:
        self.profiles = profiles
        self.engineering_extractor = EngineeringEntityExtractor()
        self.parser = TopicParser()

    def extract(self, topic: str) -> tuple[dict[str, tuple[str, ...]], tuple[str, ...]]:
        normalized = normalize_text(topic)
        parsed = self.parser.parse(topic)
        engineering = self.engineering_extractor.extract(parsed)
        buckets: dict[str, list[str]] = {
            key: list(values)
            for key, values in engineering.entities.items()
        }
        signals: list[str] = []
        profile_domains: list[str] = []
        profile_values: set[str] = set()

        for entry in self.profiles.entities:
            if self._matches(normalized, entry):
                buckets.setdefault(entry.category, []).append(entry.canonical)
                if entry.category == "Component" and entry.parent:
                    buckets.setdefault("Equipment", []).append(entry.parent)
                    profile_values.add(entry.parent)
                signals.append(entry.canonical)
                profile_values.add(entry.canonical)
                if entry.domain:
                    profile_domains.append(entry.domain)

        if self._non_industrial_profile(profile_domains):
            buckets = {
                category: [
                    value
                    for value in values
                    if value in profile_values or category in {"Standard"}
                ]
                for category, values in buckets.items()
            }

        frozen = {
            category: tuple(dict.fromkeys(values))
            for category, values in buckets.items()
            if values
        }
        return frozen, tuple(dict.fromkeys(signals))

    def _non_industrial_profile(self, domains: list[str]) -> bool:
        return bool(domains) and not any(self._is_industrial_domain(domain) for domain in domains)

    def _is_industrial_domain(self, domain: str) -> bool:
        industrial_markers = (
            "Industrial",
            "Welding",
            "Steel",
            "Production",
            "Maintenance",
            "Automation",
            "Quality",
            "Mechanical",
            "Fabrication",
            "Digital",
        )
        return any(marker in domain for marker in industrial_markers)

    def _matches(self, normalized_topic: str, entry: ProfileEntry) -> bool:
        return any(
            contains_phrase(normalized_topic, alias)
            for alias in (entry.canonical, *entry.aliases)
        )


class FailureExtractor:
    def __init__(self, profiles: TopicProfileStore) -> None:
        self.profiles = profiles

    def extract(self, topic: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
        normalized = normalize_text(topic)
        failures = [
            entry.canonical
            for entry in self.profiles.failures
            if any(contains_phrase(normalized, alias) for alias in (entry.canonical, *entry.aliases))
        ]
        severities = [
            entry.severity
            for entry in self.profiles.failures
            if entry.canonical in failures and entry.severity
        ]
        return tuple(dict.fromkeys(failures)), tuple(dict.fromkeys(severities))


class IntentDetectorV2:
    def __init__(self, profiles: TopicProfileStore) -> None:
        self.profiles = profiles
        self.legacy = IntentDetector()
        self.parser = TopicParser()

    def detect(self, topic: str, failures: tuple[str, ...]) -> tuple[str, float, tuple[str, ...]]:
        normalized = normalize_text(topic)
        scored: list[tuple[int, str, tuple[str, ...]]] = []
        for entry in self.profiles.intents:
            hits = tuple(
                alias
                for alias in entry.aliases
                if contains_phrase(normalized, alias)
            )
            if hits:
                scored.append((len(hits), entry.canonical, hits))

        if scored:
            scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
            score, intent, hits = scored[0]
            return intent, min(0.95, 0.5 + score * 0.15), hits

        if failures:
            return "Troubleshooting", 0.72, failures

        legacy = self.legacy.detect(self.parser.parse(topic))
        mapped = {
            "Problem": "Troubleshooting",
            "Failure": "Troubleshooting",
            "Procedure": "SOP",
            "Knowledge": "Training",
        }.get(legacy.intent, legacy.intent)
        return mapped, legacy.confidence, legacy.signals


class SeverityDetector:
    ORDER = ("Low", "Medium", "High", "Critical")

    def __init__(self, profiles: TopicProfileStore) -> None:
        self.profiles = profiles

    def detect(
        self,
        entities: dict[str, tuple[str, ...]],
        failures: tuple[str, ...],
        failure_severities: tuple[str, ...],
    ) -> str:
        scores = list(failure_severities)
        for rule in self.profiles.severity_rules:
            requires = rule.get("requires", {})
            if self._rule_matches(requires, entities, failures):
                scores.append(str(rule.get("severity", "Medium")))
        return max(scores or ["Medium"], key=self.ORDER.index)

    def _rule_matches(
        self,
        requires: dict[str, list[str]],
        entities: dict[str, tuple[str, ...]],
        failures: tuple[str, ...],
    ) -> bool:
        checks = {
            "equipment": entities.get("Equipment", ()) + entities.get("Machine", ()),
            "component": entities.get("Component", ()),
            "components": entities.get("Component", ()),
            "failure": failures,
            "failures": failures,
            "process": entities.get("Process", ()),
        }
        return all(
            any(value in checks.get(key, ()) for value in expected)
            for key, expected in requires.items()
        )


class KnowledgePlanner:
    def plan(self, context: TopicContext) -> str:
        ordered = (
            *context.equipment,
            *context.components,
            *context.materials,
            *context.processes,
            *context.failures,
            context.intent,
        )
        return " ".join(value for value in dict.fromkeys(ordered) if value)


class PlaybookSelector:
    def __init__(self, profiles: TopicProfileStore) -> None:
        self.profiles = profiles

    def select_key(self, entities: dict[str, tuple[str, ...]], failures: tuple[str, ...]) -> str:
        best: tuple[int, str] = (0, "")
        for playbook in self.profiles.playbooks:
            score = self._score(playbook.get("match", {}), entities, failures)
            if score > best[0]:
                best = (score, str(playbook.get("key", "")))
        return best[1]

    def _score(
        self,
        match: dict[str, list[str]],
        entities: dict[str, tuple[str, ...]],
        failures: tuple[str, ...],
    ) -> int:
        values = {
            "equipment": entities.get("Equipment", ()) + entities.get("Machine", ()),
            "components": entities.get("Component", ()),
            "materials": entities.get("Material", ()),
            "processes": entities.get("Process", ()),
            "failures": failures,
        }
        score = 0
        for key, expected in match.items():
            hits = sum(1 for value in expected if value in values.get(key, ()))
            if expected and hits == 0:
                return 0
            score += hits * 10
        return score


class TopicContextBuilder:
    def __init__(self, profiles: TopicProfileStore | None = None) -> None:
        self.profiles = profiles or TopicProfileStore()
        self.entity_extractor = EntityExtractor(self.profiles)
        self.failure_extractor = FailureExtractor(self.profiles)
        self.intent_detector = IntentDetectorV2(self.profiles)
        self.severity_detector = SeverityDetector(self.profiles)
        self.knowledge_planner = KnowledgePlanner()
        self.playbook_selector = PlaybookSelector(self.profiles)
        self.failure_library = FailureIntelligenceLibrary()

    def build(self, topic: str) -> TopicContext:
        trace_call("TopicContextBuilder.build", self, selected_topic=topic)
        entities, entity_signals = self.entity_extractor.extract(topic)
        failures, failure_severities = self.failure_extractor.extract(topic)
        if failures:
            entities = {
                **entities,
                "Failure": tuple(dict.fromkeys((*entities.get("Failure", ()), *failures))),
            }
        intent, intent_confidence, intent_signals = self.intent_detector.detect(topic, failures)
        severity = self.severity_detector.detect(entities, failures, failure_severities)
        domain = self._domain(entities)
        playbook_key = self.playbook_selector.select_key(entities, failures)
        failure_profile = self.failure_library.get(playbook_key) if playbook_key else None
        failure_intelligence = failure_profile.as_context() if failure_profile else {}
        trace_call(
            "Topic profile selected",
            self,
            selected_topic=topic,
            selected_domain=domain,
            selected_playbook=playbook_key,
            selected_profile=failure_profile.key if failure_profile else "None",
        )
        standards = tuple(
            dict.fromkeys(
                (
                    *entities.get("Standard", ()),
                    *self._profile_standards(topic),
                    *failure_intelligence.get("standards", ()),
                )
            )
        )
        confidence = self._confidence(entities, failures, intent_confidence, playbook_key)

        context = TopicContext(
            original_topic=topic,
            domain=domain,
            intent=intent,
            entities=entities,
            equipment=tuple(dict.fromkeys((*entities.get("Equipment", ()), *entities.get("Machine", ())))),
            components=entities.get("Component", ()),
            materials=entities.get("Material", ()),
            processes=entities.get("Process", ()),
            failures=failures,
            severity=severity,
            standards=standards,
            failure_mode=failure_profile.failure_mode if failure_profile else "",
            failure_intelligence=failure_intelligence,
            confidence=confidence,
            playbook_key=playbook_key,
            signals=tuple(
                dict.fromkeys(
                    (
                        *entity_signals,
                        *failures,
                        *intent_signals,
                        *(failure_intelligence.get("failure_mode", ())),
                    )
                )
            ),
        )
        trace_call(
            "TopicContextBuilder.result",
            self,
            selected_topic=topic,
            selected_domain=context.domain,
            selected_playbook=context.playbook_key,
        )
        return TopicContext(
            **{
                **context.__dict__,
                "knowledge_query": self.knowledge_planner.plan(context),
            }
        )

    def _profile_standards(self, topic: str) -> tuple[str, ...]:
        normalized = normalize_text(topic)
        return tuple(
            entry.canonical
            for entry in self.profiles.standards
            if any(contains_phrase(normalized, alias) for alias in (entry.canonical, *entry.aliases))
        )

    def _domain(self, entities: dict[str, tuple[str, ...]]) -> str:
        for entry in self.profiles.entities:
            values = entities.get(entry.category, ())
            if entry.domain and entry.canonical in values:
                if not self.entity_extractor._is_industrial_domain(entry.domain):
                    return "Out of Scope"
                return entry.domain
        if entities.get("Process"):
            return "Production"
        return "General"

    def _confidence(
        self,
        entities: dict[str, tuple[str, ...]],
        failures: tuple[str, ...],
        intent_confidence: float,
        playbook_key: str,
    ) -> float:
        score = 0.25 + intent_confidence * 0.25
        if entities:
            score += 0.2
        if failures:
            score += 0.2
        if playbook_key:
            score += 0.1
        return round(min(0.98, score), 2)


instrument_runtime_tracing(globals())
module_loaded(__name__, __file__, TopicContextBuilder)
