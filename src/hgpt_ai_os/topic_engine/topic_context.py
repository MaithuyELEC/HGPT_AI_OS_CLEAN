from __future__ import annotations

from dataclasses import dataclass, field

from hgpt_ai_os.intelligence.topic_analyzer import TopicAnalysis


@dataclass(frozen=True)
class TopicContext:
    original_topic: str
    domain: str
    intent: str
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
            category=self.domain or "General",
            process=self.processes[0] if self.processes else "Unknown",
            operation=self.intent,
            risk=f"{self.severity} Severity" if self.severity else "",
            standards=list(self.standards),
        )


def compact_topic_context(context: TopicContext) -> str:
    rows = [
        ("Domain", context.domain),
        ("Intent", context.intent),
        ("Equipment", ", ".join(context.equipment)),
        ("Components", ", ".join(context.components)),
        ("Processes", ", ".join(context.processes)),
        ("Failures", ", ".join(context.failures)),
        ("Severity", context.severity),
        ("Standards", ", ".join(context.standards)),
        ("Failure Mode", context.failure_mode),
        ("Playbook", context.playbook_key),
        ("Knowledge Query", context.knowledge_query),
        ("Confidence", f"{context.confidence:.2f}"),
    ]
    return "\n".join(f"- {label}: {value or 'None'}" for label, value in rows)
