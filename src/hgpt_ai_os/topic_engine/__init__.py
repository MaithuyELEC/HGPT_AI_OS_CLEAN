from __future__ import annotations

from .content_planner import ContentPlan, ContentPlanner
from .engineering_context import EngineeringContext, EngineeringContextBuilder
from .entity_extractor import EngineeringEntityExtractor, EntityExtraction
from .intent_detector import IntentDetector, IntentResult
from .knowledge_ranker import KnowledgeFact, KnowledgeRanker
from .problem_analyzer import ProblemAnalysis, ProblemAnalyzer
from .reasoning_engine import ReasoningEngine, ReasoningObject
from .topic_parser import ParsedTopic, TopicParser
from .writers import (
    ChannelWriter,
    ChecklistWriter,
    FacebookWriter,
    ImagePromptWriter,
    SeoWriter,
    TikTokWriter,
    VideoPromptWriter,
)


class TopicIntelligenceEngine:
    def __init__(self) -> None:
        self.parser = TopicParser()
        self.intent_detector = IntentDetector()
        self.entity_extractor = EngineeringEntityExtractor()
        self.context_builder = EngineeringContextBuilder()
        self.problem_analyzer = ProblemAnalyzer()
        self.knowledge_ranker = KnowledgeRanker()
        self.reasoning_engine = ReasoningEngine()
        self.content_planner = ContentPlanner()
        self.writers = {
            "facebook": FacebookWriter(),
            "tiktok": TikTokWriter(),
            "video": VideoPromptWriter(),
            "image": ImagePromptWriter(),
            "seo": SeoWriter(),
            "checklist": ChecklistWriter(),
            "channel": ChannelWriter(),
        }

    def reason(self, topic: str, context: str = "") -> ReasoningObject:
        parsed = self.parser.parse(topic)
        intent = self.intent_detector.detect(parsed)
        entities = self.entity_extractor.extract(parsed)
        engineering_context = self.context_builder.build(topic, entities)
        problem = self.problem_analyzer.analyze(topic, intent, entities, engineering_context)
        facts = self.knowledge_ranker.rank(context, parsed.keywords)
        return self.reasoning_engine.reason(
            parsed=parsed,
            intent=intent,
            entities=entities,
            engineering_context=engineering_context,
            problem=problem,
            knowledge_facts=facts,
        )

    def generate(self, topic: str, channel: str, context: str = "") -> str:
        reasoning = self.reason(topic, context)
        plan = self.content_planner.plan(reasoning, channel)
        writer = self.writers.get(plan.channel, self.writers["channel"])
        return writer.write(reasoning, plan)


__all__ = [
    "ContentPlan",
    "ContentPlanner",
    "EngineeringContext",
    "EngineeringContextBuilder",
    "EngineeringEntityExtractor",
    "EntityExtraction",
    "IntentDetector",
    "IntentResult",
    "KnowledgeFact",
    "KnowledgeRanker",
    "ParsedTopic",
    "ProblemAnalysis",
    "ProblemAnalyzer",
    "ReasoningEngine",
    "ReasoningObject",
    "TopicIntelligenceEngine",
    "TopicParser",
]
