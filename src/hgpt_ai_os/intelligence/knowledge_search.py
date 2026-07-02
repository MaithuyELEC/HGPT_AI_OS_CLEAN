from __future__ import annotations

from hgpt_ai_os.intelligence.knowledge_ranker import KnowledgeRanker
from hgpt_ai_os.intelligence.topic_analyzer import TopicAnalysis
from hgpt_ai_os.knowledge.retriever import KnowledgeRetriever


class KnowledgeSearch:
    def __init__(self, knowledge_root="knowledge"):
        self.retriever = KnowledgeRetriever(knowledge_root)
        self.ranker = KnowledgeRanker()

    def search(self, analysis: TopicAnalysis, top_k: int = 5):
        query = analysis.search_query or analysis.original_topic
        if not query:
            return []

        items = self.retriever.retrieve(query, top_k=top_k)
        results = self.ranker.rank(analysis, items)
        self._print_ranking(results)
        return results

    def _print_ranking(self, results):
        if not results:
            return

        print("Knowledge Ranking")
        for index, result in enumerate(results, start=1):
            print("")
            print(f"{index}.")
            print(result.item.id)
            print(f"Score : {result.score:.2f}")
