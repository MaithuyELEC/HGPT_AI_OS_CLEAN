from pathlib import Path

from .repository import FileKnowledgeRepository


class KnowledgeEngine:

    def __init__(self, knowledge_root: str = "knowledge"):
        self.repository = FileKnowledgeRepository(Path(knowledge_root))

    def get(self, knowledge_id: str):
        return self.repository.get_by_id(knowledge_id)

    def search(self, query: str):
        return self.repository.search(query)

    def by_category(self, category: str):
        return self.repository.find_by_category(category)

    def by_tag(self, tag: str):
        return self.repository.find_by_tag(tag)
