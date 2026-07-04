from __future__ import annotations

from hgpt_ai_os.intelligence.topic_analyzer import TopicAnalysis
from hgpt_ai_os.knowledge.retrieval_pipeline import KnowledgeRetrievalPipeline


class KnowledgeSearch:
    def __init__(self, knowledge_root="knowledge"):
        self.pipeline = KnowledgeRetrievalPipeline(knowledge_root)

    def search(self, analysis: TopicAnalysis, top_k: int = 5):
        results = self.pipeline.retrieve(analysis, top_k=top_k)
        self._print_ranking(results)
        return results

    def search_text(self, query: str, top_k: int = 5):
        results = self.pipeline.retrieve(query, top_k=top_k)
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
