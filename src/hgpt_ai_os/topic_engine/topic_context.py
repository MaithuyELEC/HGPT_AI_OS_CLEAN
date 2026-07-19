from __future__ import annotations

from dataclasses import dataclass, field

from hgpt_ai_os.intelligence.topic_analyzer import TopicAnalysis


@dataclass(frozen=True)
class TopicContext:
    original_topic: str
    domain: str
    intent: str
    domain_family: str = "UNKNOWN"
    domain_scores: tuple[tuple[str, float], ...] = ()
    secondary_domains: tuple[str, ...] = ()
    subdomain: str = ""
    topic_intent: str = "GENERAL_GUIDANCE"
    object_or_system: str = ""
    process: str = ""
    audience: str = ""
    expected_output_style: str = ""
    risk_level: str = "Medium"
    available_evidence: tuple[str, ...] = ()
    missing_evidence: tuple[str, ...] = ()
    topic_nature: str = "general-life"
    entities: dict[str, tuple[str, ...]] = field(default_factory=dict)
    equipment: tuple[str, ...] = ()
    components: tuple[str, ...] = ()
    materials: tuple[str, ...] = ()
    processes: tuple[str, ...] = ()
    failures: tuple[str, ...] = ()
    severity: str = "Medium"
    standards: tuple[str, ...] = ()
    failure_mode: str = ""
    failure_intelligence: dict[str, tuple[str, ...]] = field(default_factory=dict)
    confidence: float = 0.0
    knowledge_query: str = ""
    playbook_key: str = ""
    signals: tuple[str, ...] = ()

    def get(self, category: str) -> tuple[str, ...]:
        return self.entities.get(category, ())

    def to_topic_analysis(self) -> TopicAnalysis:
        keywords = [
            value.lower()
            for value in (
                *self.equipment,
                *self.components,
                *self.failures,
                *self.processes,
                self.intent,
            )
            if value
        ]
        return TopicAnalysis(
            original_topic=self.original_topic,
            search_query=self.knowledge_query or self.original_topic,
            keywords=list(dict.fromkeys(keywords)),
            normalized_topic=(self.knowledge_query or self.original_topic).lower(),
            category=self.domain_family or self.domain or "GENERAL_LIFE",
            process=self.process or (self.processes[0] if self.processes else "general guidance"),
            operation=self.intent,
            risk=f"{self.severity} Severity" if self.severity else "",
            standards=list(self.standards),
        )


def compact_topic_context(context: TopicContext) -> str:
    rows = [
        ("Domain", context.domain),
        ("Domain Family", context.domain_family),
        ("Secondary Domains", ", ".join(context.secondary_domains)),
        ("Subdomain", context.subdomain),
        ("Intent", context.intent),
        ("Content Intent", context.topic_intent),
        ("Topic Nature", context.topic_nature),
        ("Object/System", context.object_or_system),
        ("Audience", context.audience),
        ("Output Style", context.expected_output_style),
        ("Equipment", ", ".join(context.equipment)),
        ("Components", ", ".join(context.components)),
        ("Processes", ", ".join(context.processes)),
        ("Failures", ", ".join(context.failures)),
        ("Severity", context.severity),
        ("Standards", ", ".join(context.standards)),
        ("Failure Mode", context.failure_mode),
        ("Playbook", context.playbook_key),
        ("Knowledge Query", context.knowledge_query),
        ("Available Evidence", ", ".join(context.available_evidence)),
        ("Missing Evidence", ", ".join(context.missing_evidence)),
        ("Confidence", f"{context.confidence:.2f}"),
    ]
    return "\n".join(f"- {label}: {value or 'not enough evidence'}" for label, value in rows)
