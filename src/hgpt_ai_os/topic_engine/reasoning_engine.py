from __future__ import annotations

from dataclasses import dataclass

from hgpt_ai_os.diagnostics import instrument_runtime_tracing, module_loaded, trace_call

from .engineering_context import EngineeringContext
from .entity_extractor import EntityExtraction
from .intent_detector import IntentResult
from .knowledge_ranker import KnowledgeFact
from .problem_analyzer import ProblemAnalysis
from .topic_context import TopicContext
from .topic_parser import ParsedTopic


@dataclass(frozen=True)
class ReasoningObject:
    topic: str
    topic_context: TopicContext
    parsed: ParsedTopic
    intent: IntentResult
    entities: EntityExtraction
    engineering_context: EngineeringContext
    problem: ProblemAnalysis
    knowledge_facts: tuple[KnowledgeFact, ...]
    decision: str
    possible_mechanisms: tuple[str, ...]
    evidence: tuple[str, ...]
    most_probable_cause: str
    corrective_actions: tuple[str, ...]
    preventive_actions: tuple[str, ...]
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
        topic_context: TopicContext,
    ) -> ReasoningObject:
        trace_call("ReasoningEngine.reason", self, selected_topic=parsed.original)
        controls = engineering_context.graph.get("Repair / Control", ()) or problem.root_cause_candidates
        verification = engineering_context.graph.get("Inspection", ()) or ("visual evidence", "measurement record", "review approval")
        evidence = tuple(
            dict.fromkeys(
                (
                    *problem.recommended_inspection[:4],
                    *(fact.text for fact in knowledge_facts[:2]),
                )
            )
        ) or verification
        possible_mechanisms = tuple(
            dict.fromkeys(
                (
                    f"{cause} can trigger {problem.immediate_cause}"
                    for cause in problem.possible_causes[:5]
                )
            )
        )
        corrective_actions = tuple(dict.fromkeys((*problem.recommended_action[:5], *controls[:3])))
        preventive_actions = tuple(
            dict.fromkeys(
                (
                    "standardize the inspection hold point",
                    "record measured evidence before release",
                    "train operators on the abnormal-condition trigger",
                    "review recurring losses in the daily production meeting",
                    *(
                        f"trend {item}"
                        for item in verification[:2]
                        if item.lower() not in {"vt", "ut", "rt", "mt", "pt"}
                    ),
                )
            )
        )
        decision = (
            f"Treat this as {intent.intent.lower()} work: start from {problem.immediate_cause}, "
            f"test {problem.hidden_cause}, confirm {problem.root_cause}, apply corrective controls, "
            "then release only after verification evidence is recorded."
        )
        return ReasoningObject(
            topic=parsed.original,
            topic_context=topic_context,
            parsed=parsed,
            intent=intent,
            entities=entities,
            engineering_context=engineering_context,
            problem=problem,
            knowledge_facts=knowledge_facts,
            decision=decision,
            possible_mechanisms=possible_mechanisms,
            evidence=evidence,
            most_probable_cause=problem.root_cause,
            corrective_actions=corrective_actions,
            preventive_actions=preventive_actions,
            controls=tuple(dict.fromkeys(controls)),
            verification=tuple(dict.fromkeys(verification)),
        )


instrument_runtime_tracing(globals())
module_loaded(__name__, __file__, ReasoningEngine)
