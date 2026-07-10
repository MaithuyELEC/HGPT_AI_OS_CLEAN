from __future__ import annotations

from pathlib import Path

from hgpt_ai_os.intelligence.knowledge_ranker import KnowledgeRanker
from hgpt_ai_os.intelligence.topic_analyzer import TopicAnalysis, TopicAnalyzer
from hgpt_ai_os.knowledge.models import KnowledgeResult
from hgpt_ai_os.knowledge.repository import FileKnowledgeRepository, KnowledgeRepository


KNOWLEDGE_THRESHOLD = 0.35


class KnowledgeRetrievalPipeline:
    """Single production path for knowledge retrieval and ranking."""

    def __init__(
        self,
        knowledge_root: str | Path = "knowledge",
        repository: KnowledgeRepository | None = None,
        analyzer: TopicAnalyzer | None = None,
        ranker: KnowledgeRanker | None = None,
    ):
        self.repository = repository or FileKnowledgeRepository(Path(knowledge_root))
        self.analyzer = analyzer or TopicAnalyzer()
        self.ranker = ranker or KnowledgeRanker()

    def retrieve(
        self,
        topic_or_analysis: str | TopicAnalysis,
        top_k: int = 5,
    ) -> list[KnowledgeResult]:
        return self.relevant_results(topic_or_analysis, top_k=top_k)

    def scored_candidates(
        self,
        topic_or_analysis: str | TopicAnalysis,
    ) -> list[KnowledgeResult]:
        analysis = self._analysis(topic_or_analysis)

        query = analysis.search_query or analysis.original_topic
        if not query:
            return []

        candidates = self.repository.list_packages()
        if not candidates:
            return []

        ranked = [
            result
            for result in self.ranker.rank(analysis, candidates)
            if result.score > 0
        ]

        return ranked

    def relevant_results(
        self,
        topic_or_analysis: str | TopicAnalysis,
        top_k: int = 5,
    ) -> list[KnowledgeResult]:
        ranked = [
            result
            for result in self.scored_candidates(topic_or_analysis)
            if result.score >= KNOWLEDGE_THRESHOLD
        ]

        if top_k <= 0:
            return ranked

        return ranked[:top_k]

    def _analysis(self, topic_or_analysis: str | TopicAnalysis) -> TopicAnalysis:
        if isinstance(topic_or_analysis, TopicAnalysis):
            return topic_or_analysis

        return self.analyzer.analyze(topic_or_analysis)
