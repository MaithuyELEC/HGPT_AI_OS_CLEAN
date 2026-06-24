from hgpt_ai_os.knowledge.engine import KnowledgeEngine


class KnowledgeRetriever:

    def __init__(self, knowledge_root="knowledge"):
        self.engine = KnowledgeEngine(knowledge_root)

    def retrieve(self, query: str, top_k: int = 5):

        results = self.engine.search(query)

        if not results:
            return []

        return results[:top_k]
