from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from .loader import load_markdown, load_metadata
from .models import KnowledgeMetadata, KnowledgePackage


class KnowledgeRepository(ABC):

    @abstractmethod
    def list_metadata(self) -> list[KnowledgeMetadata]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, knowledge_id: str) -> KnowledgePackage | None:
        raise NotImplementedError

    @abstractmethod
    def find_by_category(self, category: str) -> list[KnowledgePackage]:
        raise NotImplementedError

    @abstractmethod
    def find_by_tag(self, tag: str) -> list[KnowledgePackage]:
        raise NotImplementedError

    @abstractmethod
    def search(self, query: str) -> list[KnowledgePackage]:
        raise NotImplementedError


class FileKnowledgeRepository(KnowledgeRepository):

    def __init__(self, knowledge_root: Path):
        self.knowledge_root = Path(knowledge_root)
        self.metadata_root = self.knowledge_root / "metadata"

    def list_metadata(self) -> list[KnowledgeMetadata]:
        items = []

        if not self.metadata_root.exists():
            return items

        for file in sorted(self.metadata_root.glob("*.json")):
            items.append(load_metadata(file))

        return items

    def get_by_id(self, knowledge_id: str) -> KnowledgePackage | None:

        for meta in self.list_metadata():

            if meta.id != knowledge_id:
                continue

            if meta.source_path is None:
                return None

            md = self.knowledge_root / meta.source_path

            if not md.exists():
                return None

            return KnowledgePackage(
                metadata=meta,
                content=load_markdown(md),
            )

        return None

    def find_by_category(self, category: str) -> list[KnowledgePackage]:

        result = []

        for meta in self.list_metadata():

            if meta.category.lower() == category.lower():

                doc = self.get_by_id(meta.id)

                if doc:
                    result.append(doc)

        return result

    def find_by_tag(self, tag: str) -> list[KnowledgePackage]:

        result = []

        for meta in self.list_metadata():

            tags = [t.lower() for t in meta.tags]

            if tag.lower() in tags:

                doc = self.get_by_id(meta.id)

                if doc:
                    result.append(doc)

        return result

    def search(self, query: str) -> list[KnowledgePackage]:

        keywords = query.lower().replace("-", " ").split()

        result = []

        for meta in self.list_metadata():

            text = " ".join([
                meta.title,
                meta.category,
                *meta.tags,
            ]).lower().replace("-", " ")

            score = sum(1 for keyword in keywords if keyword in text)

            if score == 0:
                continue

            doc = self.get_by_id(meta.id)

            if doc:
                result.append((score, doc))

        result.sort(key=lambda item: item[0], reverse=True)

        return [doc for _, doc in result]