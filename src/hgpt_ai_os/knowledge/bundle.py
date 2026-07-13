from dataclasses import dataclass
import re
from typing import List

from hgpt_ai_os.diagnostics import instrument_runtime_tracing
from hgpt_ai_os.knowledge.models import KnowledgePackage, KnowledgeResult


_MAX_REFERENCE_LINES = 12
_MAX_REFERENCE_CHARS = 1200


@dataclass
class KnowledgeBundle:

    query: str
    items: List[KnowledgePackage | KnowledgeResult]

    def context(self):

        chunks = []

        for bundle_item in self.items:

            item = self._knowledge_package(bundle_item)

            reference = self._reference_excerpt(item.content)

            if not reference:
                continue

            chunks.append(
                f"""
ID: {item.id}
TITLE: {item.title}
CATEGORY: {item.category}
TAGS: {", ".join(item.tags)}

REFERENCE NOTES:
{reference}
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

    def _reference_excerpt(self, content: str) -> str:
        lines = []

        for raw_line in content.splitlines():
            line = raw_line.strip()

            if not line:
                continue

            line = re.sub(r"^#{1,6}\s*", "", line)
            lines.append(line)

            if len(lines) >= _MAX_REFERENCE_LINES:
                break

        excerpt = "\n".join(lines)
        return excerpt[:_MAX_REFERENCE_CHARS].strip()


instrument_runtime_tracing(globals())
