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
            context.domain_family,
            *context.secondary_domains,
            context.object_or_system,
            *context.equipment,
            *context.components,
            *context.materials,
            context.process,
            *context.processes,
            *context.failures,
            context.topic_intent,
        )
        return " ".join(value for value in dict.fromkeys(ordered) if value)


class UniversalTopicAnalyzer:
    DOMAIN_FAMILIES = (
        "STRUCTURAL_STEEL",
        "MECHANICAL_FABRICATION",
        "EQUIPMENT_MAINTENANCE",
        "ELECTRICAL_MAINTENANCE",
        "WELDING",
        "QA_QC",
        "SAFETY",
        "LEAN_KAIZEN_5S_TPM",
        "PRODUCTION_MANAGEMENT",
        "PROJECT_MANAGEMENT",
        "GENERAL_EDUCATION",
        "GENERAL_LIFE",
        "MARKETING_CONTENT",
        "UNKNOWN",
    )

    _DOMAIN_SIGNALS: dict[str, tuple[str, ...]] = {
        "STRUCTURAL_STEEL": ("ket cau thep", "steel structure", "dam", "cot", "bulong neo", "lap dung", "fit up", "fitup"),
        "MECHANICAL_FABRICATION": ("co khi", "gia cong", "che tao", "cat laser", "phun bi", "son phu", "bevel", "bavia"),
        "EQUIPMENT_MAINTENANCE": ("bao tri", "bao duong", "hong", "keu", "rung", "qua nhiet", "bac dan", "vong bi", "hop so", "may nen", "cau truc"),
        "ELECTRICAL_MAINTENANCE": ("dong co", "motor", "plc", "vfd", "bien tan", "dien", "3 pha", "overcurrent", "cap dien", "tu dien"),
        "WELDING": ("han", "welding", "saw", "mig", "tig", "wps", "pqr", "ro khi", "porosity", "undercut"),
        "QA_QC": ("qaqc", "qa qc", "qc", "kiem tra", "nghiem thu", "itp", "ndt", "vt", "ut", "mt", "pt", "rt", "dft", "ncr"),
        "SAFETY": ("an toan", "safety", "loto", "ppe", "nguy hiem", "tai nan", "dien giat", "nga cao", "near miss"),
        "LEAN_KAIZEN_5S_TPM": ("5s", "kaizen", "lean", "tpm", "lang phi", "cai tien", "seiri", "seiton"),
        "PRODUCTION_MANAGEMENT": ("quan ly san xuat", "ke hoach san xuat", "nang suat", "tien do", "line", "ca san xuat", "workshop manager"),
        "PROJECT_MANAGEMENT": ("du an", "project", "schedule", "milestone", "nguon luc", "risk register", "ke hoach trien khai"),
        "GENERAL_EDUCATION": ("hoc", "dao tao", "training", "n5", "tieng anh", "tieng nhat", "giao duc"),
        "GENERAL_LIFE": ("cham soc", "nau", "du lich", "gia dinh", "day con", "husky", "mai", "suc khoe", "giam can", "trong rau"),
        "MARKETING_CONTENT": ("facebook", "tiktok", "seo", "quang cao", "ban hang", "marketing", "content", "hashtag"),
    }

    _INTENT_SIGNALS: dict[str, tuple[str, ...]] = {
        "EXPLAIN": ("la gi", "what", "giai thich", "vi sao", "tai sao", "nguyen ly"),
        "DIAGNOSE": ("chan doan", "nguyen nhan", "root cause", "tai sao", "bi keu", "bi nong"),
        "TROUBLESHOOT": ("khac phuc", "xu ly", "sua", "hong", "loi", "fault", "failure", "khong chay"),
        "SOP": ("sop", "quy trinh", "huong dan thao tac", "work instruction"),
        "CHECKLIST": ("checklist", "kiem tra", "danh muc", "nghiem thu"),
        "TRAINING": ("dao tao", "training", "bai hoc", "huong dan", "hoc"),
        "MANAGEMENT": ("quan ly", "manager", "phan cong", "kpi", "tien do"),
        "IMPROVEMENT": ("cai tien", "kaizen", "5s", "lean", "tpm", "toi uu", "nang suat"),
        "SAFETY_WARNING": ("an toan", "safety", "canh bao", "tai nan", "loto", "ppe"),
        "INVESTMENT_ANALYSIS": ("dau tu", "capex", "opex", "roi", "hoan von", "mua may"),
        "SOCIAL_CONTENT": ("facebook", "tiktok", "bai dang", "post", "viral"),
        "SEO_CONTENT": ("seo", "tu khoa", "article", "blog"),
        "IMAGE_PROMPT": ("image prompt", "prompt anh", "gemini tao anh", "tao anh"),
        "VIDEO_PROMPT": ("video prompt", "prompt video", "veo", "tao video"),
        "GENERAL_GUIDANCE": ("cach", "nen", "kinh nghiem", "huong dan"),
    }

    def analyze(
        self,
        topic: str,
        entities: dict[str, tuple[str, ...]],
        failures: tuple[str, ...],
        intent: str,
        severity: str,
    ) -> dict[str, Any]:
        normalized = normalize_text(topic)
        topic_intent = self._intent(normalized, failures, intent)
        domain_scores = self._domain_scores(normalized, entities, failures, topic_intent)
        primary = domain_scores[0][0] if domain_scores else "UNKNOWN"
        secondary = tuple(domain for domain, score in domain_scores[1:4] if score >= 0.28)
        evidence = self._evidence(topic, entities, failures)
        object_or_system = self._object_or_system(topic, entities)
        process = self._process(topic, entities, primary)
        return {
            "domain_family": primary,
            "domain_scores": domain_scores,
            "secondary_domains": secondary,
            "subdomain": self._subdomain(primary, entities),
            "topic_intent": topic_intent,
            "object_or_system": object_or_system,
            "process": process,
            "audience": self._audience(primary, topic_intent),
            "expected_output_style": self._style(topic_intent),
            "risk_level": self._risk_level(primary, topic_intent, severity),
            "available_evidence": evidence[0],
            "missing_evidence": evidence[1],
            "topic_nature": self._nature(primary, topic_intent),
        }

    def _domain_scores(
        self,
        normalized: str,
        entities: dict[str, tuple[str, ...]],
        failures: tuple[str, ...],
        topic_intent: str,
    ) -> tuple[tuple[str, float], ...]:
        scores: dict[str, float] = {domain: 0.0 for domain in self.DOMAIN_FAMILIES}
        entity_text = normalize_text(" ".join(value for values in entities.values() for value in values))
        haystack = f"{normalized} {entity_text}"
        for domain, signals in self._DOMAIN_SIGNALS.items():
            hits = sum(1 for signal in signals if contains_phrase(haystack, signal))
            if hits:
                scores[domain] += min(0.82, 0.24 + hits * 0.13)
        if failures:
            scores["EQUIPMENT_MAINTENANCE"] += 0.22
            scores["SAFETY"] += 0.08
        if entities.get("Standard"):
            scores["QA_QC"] += 0.18
        if topic_intent == "IMPROVEMENT" and scores["LEAN_KAIZEN_5S_TPM"] > 0:
            scores["LEAN_KAIZEN_5S_TPM"] += 0.35
        if topic_intent == "SAFETY_WARNING" and scores["SAFETY"] > 0:
            scores["SAFETY"] += 0.35
        if topic_intent in {"DIAGNOSE", "TROUBLESHOOT"} and failures:
            scores["EQUIPMENT_MAINTENANCE"] += 0.2
        if entities.get("Process") and not any(score > 0 for score in scores.values()):
            scores["PRODUCTION_MANAGEMENT"] += 0.35
        if not any(score > 0 for score in scores.values()):
            scores["GENERAL_LIFE"] = 0.36
            scores["UNKNOWN"] = 0.25
        ordered = sorted(
            ((domain, round(min(score, 0.98), 2)) for domain, score in scores.items() if score > 0),
            key=lambda item: (item[1], item[0] != "UNKNOWN"),
            reverse=True,
        )
        return tuple(ordered)

    def _intent(self, normalized: str, failures: tuple[str, ...], legacy_intent: str) -> str:
        scored: list[tuple[int, str]] = []
        for intent, signals in self._INTENT_SIGNALS.items():
            hits = sum(1 for signal in signals if contains_phrase(normalized, signal))
            if hits:
                scored.append((hits, intent))
        if scored:
            scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
            return scored[0][1]
        if failures:
            return "DIAGNOSE"
        return {
            "Troubleshooting": "TROUBLESHOOT",
            "SOP": "SOP",
            "Training": "TRAINING",
            "Improvement": "IMPROVEMENT",
            "Inspection": "CHECKLIST",
        }.get(legacy_intent, "GENERAL_GUIDANCE")

    def _evidence(
        self,
        topic: str,
        entities: dict[str, tuple[str, ...]],
        failures: tuple[str, ...],
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        available = []
        if topic.strip():
            available.append("user topic")
        for label, values in (
            ("object/system", entities.get("Equipment", ()) + entities.get("Machine", ()) + entities.get("Component", ())),
            ("process", entities.get("Process", ())),
            ("material", entities.get("Material", ())),
            ("failure symptom", failures),
            ("standard", entities.get("Standard", ())),
        ):
            if values:
                available.append(label)
        missing = ["site photos or measured evidence", "model/OEM details", "exact operating condition"]
        if not failures:
            missing.append("confirmed failure mode")
        if not entities.get("Standard"):
            missing.append("applicable standard or acceptance criterion")
        return tuple(dict.fromkeys(available)), tuple(dict.fromkeys(missing))

    def _object_or_system(self, topic: str, entities: dict[str, tuple[str, ...]]) -> str:
        values = entities.get("Equipment", ()) + entities.get("Machine", ()) + entities.get("Component", ())
        return ", ".join(dict.fromkeys(values)) or topic.strip()

    def _process(self, topic: str, entities: dict[str, tuple[str, ...]], domain: str) -> str:
        if entities.get("Process"):
            return entities["Process"][0]
        if domain == "LEAN_KAIZEN_5S_TPM":
            return "workplace improvement and sustainment"
        if domain in {"GENERAL_LIFE", "GENERAL_EDUCATION", "MARKETING_CONTENT"}:
            return "practical guidance"
        return topic.strip()

    def _subdomain(self, domain: str, entities: dict[str, tuple[str, ...]]) -> str:
        values = entities.get("Process", ()) + entities.get("Equipment", ()) + entities.get("Machine", ())
        return values[0] if values else domain.replace("_", " ").title()

    def _audience(self, domain: str, intent: str) -> str:
        if domain in {"GENERAL_LIFE", "GENERAL_EDUCATION", "MARKETING_CONTENT"}:
            return "người đọc phổ thông cần hướng dẫn thực tế"
        if intent in {"MANAGEMENT", "IMPROVEMENT", "INVESTMENT_ANALYSIS"}:
            return "quản lý xưởng, kỹ sư sản xuất và người ra quyết định"
        return "kỹ thuật viên, QA/QC, bảo trì, tổ trưởng và quản lý hiện trường"

    def _style(self, intent: str) -> str:
        return {
            "DIAGNOSE": "diagnostic field guide",
            "TROUBLESHOOT": "troubleshooting workflow",
            "SOP": "step-by-step operating procedure",
            "CHECKLIST": "audit-ready checklist",
            "TRAINING": "training lesson",
            "MANAGEMENT": "management brief",
            "IMPROVEMENT": "operational improvement plan",
            "INVESTMENT_ANALYSIS": "decision and trade-off analysis",
            "SOCIAL_CONTENT": "social media post",
            "SEO_CONTENT": "search article",
            "IMAGE_PROMPT": "visual generation prompt",
            "VIDEO_PROMPT": "video generation prompt",
        }.get(intent, "practical guidance")

    def _risk_level(self, domain: str, intent: str, severity: str) -> str:
        if intent == "SAFETY_WARNING" or severity in {"High", "Critical"}:
            return "High"
        if domain in {"GENERAL_LIFE", "GENERAL_EDUCATION", "MARKETING_CONTENT"}:
            return "Low"
        return severity or "Medium"

    def _nature(self, domain: str, intent: str) -> str:
        if intent in {"SOCIAL_CONTENT", "SEO_CONTENT", "IMAGE_PROMPT", "VIDEO_PROMPT"}:
            return "promotional"
        if domain in {"GENERAL_LIFE", "GENERAL_EDUCATION"}:
            return "general-life" if domain == "GENERAL_LIFE" else "educational"
        if intent in {"MANAGEMENT", "IMPROVEMENT", "INVESTMENT_ANALYSIS"}:
            return "managerial"
        if intent == "TRAINING":
            return "educational"
        return "technical"


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
        self.universal_analyzer = UniversalTopicAnalyzer()
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
        universal = self.universal_analyzer.analyze(topic, entities, failures, intent, severity)

        context = TopicContext(
            original_topic=topic,
            domain=domain,
            intent=intent,
            domain_family=universal["domain_family"],
            domain_scores=universal["domain_scores"],
            secondary_domains=universal["secondary_domains"],
            subdomain=universal["subdomain"],
            topic_intent=universal["topic_intent"],
            object_or_system=universal["object_or_system"],
            process=universal["process"],
            audience=universal["audience"],
            expected_output_style=universal["expected_output_style"],
            risk_level=universal["risk_level"],
            available_evidence=universal["available_evidence"],
            missing_evidence=universal["missing_evidence"],
            topic_nature=universal["topic_nature"],
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
