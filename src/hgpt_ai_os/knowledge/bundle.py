from dataclasses import dataclass
from typing import List

from hgpt_ai_os.knowledge.models import KnowledgePackage, KnowledgeResult


@dataclass
class KnowledgeBundle:

    query: str
    items: List[KnowledgePackage | KnowledgeResult]

    def context(self):

        chunks = []

        for bundle_item in self.items:

            item = self._knowledge_package(bundle_item)

            chunks.append(
                f"""
ID: {item.id}
TITLE: {item.title}
CATEGORY: {item.category}
TAGS: {", ".join(item.tags)}

{item.content}
"""
            )

        return "\n".join(chunks)

    def _knowledge_package(
        self,
        item: KnowledgePackage | KnowledgeResult,
    ) -> KnowledgePackage:
        if isinstance(item, KnowledgeResult):
            return item.item

        return item
