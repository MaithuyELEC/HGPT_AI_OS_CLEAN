from hgpt_ai_os.knowledge.retrieval_pipeline import KnowledgeRetrievalPipeline


class KnowledgeRetriever:

    def __init__(self, knowledge_root="knowledge"):
        self.pipeline = KnowledgeRetrievalPipeline(knowledge_root)

    def retrieve(self, query: str, top_k: int = 5):
        results = self.pipeline.retrieve(query, top_k=top_k)

        return [result.item for result in results]
