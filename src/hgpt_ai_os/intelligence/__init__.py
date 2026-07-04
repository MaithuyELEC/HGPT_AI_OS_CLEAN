__all__ = [
    "KnowledgeSearch",
    "KnowledgeRanker",
    "TopicAnalysis",
    "TopicAnalyzer",
]


def __getattr__(name):
    if name == "KnowledgeSearch":
        from .knowledge_search import KnowledgeSearch

        return KnowledgeSearch

    if name == "KnowledgeRanker":
        from .knowledge_ranker import KnowledgeRanker

        return KnowledgeRanker

    if name in {"TopicAnalysis", "TopicAnalyzer"}:
        from .topic_analyzer import TopicAnalysis, TopicAnalyzer

        return {
            "TopicAnalysis": TopicAnalysis,
            "TopicAnalyzer": TopicAnalyzer,
        }[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
