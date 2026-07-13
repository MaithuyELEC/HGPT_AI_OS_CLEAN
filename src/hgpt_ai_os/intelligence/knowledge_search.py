from __future__ import annotations

from hgpt_ai_os.diagnostics import instrument_runtime_tracing
from hgpt_ai_os.intelligence.topic_analyzer import TopicAnalysis
from hgpt_ai_os.knowledge.retrieval_pipeline import (
    KNOWLEDGE_THRESHOLD,
    KnowledgeRetrievalPipeline,
)


class KnowledgeSearch:
    def __init__(self, knowledge_root="knowledge"):
        self.pipeline = KnowledgeRetrievalPipeline(knowledge_root)

    def search(self, analysis: TopicAnalysis, top_k: int = 5):
        candidates = self.pipeline.scored_candidates(analysis)
        results = [
            result
            for result in candidates
            if result.score >= KNOWLEDGE_THRESHOLD
        ]
        if top_k > 0:
            results = results[:top_k]
        self._print_decision(analysis.original_topic, candidates, results)
        return results

    def search_text(self, query: str, top_k: int = 5):
        candidates = self.pipeline.scored_candidates(query)
        results = [
            result
            for result in candidates
            if result.score >= KNOWLEDGE_THRESHOLD
        ]
        if top_k > 0:
            results = results[:top_k]
        self._print_decision(query, candidates, results)
        return results

    def _print_decision(self, topic, candidates, injected):
        print("Topic:")
        print(f'"{topic}"')
        print("")
        print("Knowledge Candidates:")
        print(len(injected))
        print("")
        print("Candidate Scores:")
        for result in injected:
            print(result.item.id)
            print(f"{result.score:.2f}")
        print("")
        print("Knowledge Enabled:")
        print(bool(injected))
        print("")
        print("Knowledge Disabled:")
        print(not bool(injected))
        print("")

        if injected:
            print("Injected IDs:")
            for result in injected:
                print(result.item.id)
            print("")
            print("Reason:")
            print(f"Relevant knowledge score >= {KNOWLEDGE_THRESHOLD:.2f}.")
            return

        print("Injected IDs:")
        print("None")
        print("")
        print("Reason:")
        if candidates:
            print(f"No candidate reached threshold {KNOWLEDGE_THRESHOLD:.2f}.")
            print("")
            print("Rejected Candidate Scores:")
            for result in candidates:
                print(result.item.id)
                print(f"{result.score:.2f}")
            return

        print("No relevant knowledge found.")


instrument_runtime_tracing(globals())
