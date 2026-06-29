from dataclasses import dataclass
from typing import List

from hgpt_ai_os.knowledge.models import KnowledgePackage


@dataclass
class KnowledgeBundle:

    query: str
    items: List[KnowledgePackage]

    def context(self):

        chunks = []

        for item in self.items:

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
