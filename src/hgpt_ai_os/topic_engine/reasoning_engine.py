from __future__ import annotations

from dataclasses import dataclass

from .engineering_context import EngineeringContext
from .entity_extractor import EntityExtraction
from .intent_detector import IntentResult
from .knowledge_ranker import KnowledgeFact
from .problem_analyzer import ProblemAnalysis
from .topic_parser import ParsedTopic


@dataclass(frozen=True)
class ReasoningObject:
    topic: str
    parsed: ParsedTopic
    intent: IntentResult
    entities: EntityExtraction
    engineering_context: EngineeringContext
    problem: ProblemAnalysis
    knowledge_facts: tuple[KnowledgeFact, ...]
    decision: str
    controls: tuple[str, ...]
    verification: tuple[str, ...]


class ReasoningEngine:
    def reason(
        self,
        parsed: ParsedTopic,
        intent: IntentResult,
        entities: EntityExtraction,
        engineering_context: EngineeringContext,
        problem: ProblemAnalysis,
        knowledge_facts: tuple[KnowledgeFact, ...],
    ) -> ReasoningObject:
        controls = engineering_context.graph.get("Repair / Control", ()) or problem.root_cause_candidates
        verification = engineering_context.graph.get("Inspection", ()) or ("visual evidence", "measurement record", "review approval")
        decision = (
            f"Treat this as {intent.intent.lower()} work: isolate the symptom, test likely causes, "
            "apply controls, then release only after verification evidence is recorded."
        )
        return ReasoningObject(
            topic=parsed.original,
            parsed=parsed,
            intent=intent,
            entities=entities,
            engineering_context=engineering_context,
            problem=problem,
            knowledge_facts=knowledge_facts,
            decision=decision,
            controls=tuple(dict.fromkeys(controls)),
            verification=tuple(dict.fromkeys(verification)),
        )
