from __future__ import annotations

from abc import ABC, abstractmethod
import re
from pathlib import Path

from .loader import load_markdown, load_metadata
from .models import KnowledgeMetadata, KnowledgePackage


_STOPWORDS = {
    "and",
    "are",
    "the",
    "for",
    "with",
    "from",
    "cua",
    "cho",
    "tai",
    "voi",
    "trong",
    "ngoai",
    "hien",
    "nay",
    "truong",
    "sai",
    "loi",
    "lỗi",
    "khong",
    "bảo",
    "bao",
    "đạt",
    "dat",
    "không",
    "đúng",
    "dung",
    "các",
    "cac",
    "tại",
    "với",
    "của",
    "khi",
    "can",
    "cần",
    "lam",
    "làm",
    "quy",
    "trinh",
    "trình",
    "kiem",
    "kiểm",
    "tra",
    "nhu",
    "nào",
    "nao",
}


def retrieval_terms(query: str) -> list[str]:
    terms = []

    for raw_term in re.split(r"\s+", query.lower().replace("-", " ")):
        term = raw_term.strip("!?()[]{}\"'.,:;")

        if len(term) < 3:
            continue

        if term in _STOPWORDS:
            continue

        if term not in terms:
            terms.append(term)

    return terms


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

    @abstractmethod
    def list_packages(self) -> list[KnowledgePackage]:
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

    def list_packages(self) -> list[KnowledgePackage]:
        packages = []

        for meta in self.list_metadata():
            doc = self.get_by_id(meta.id)

            if doc:
                packages.append(doc)

        return packages

    def search(self, query: str) -> list[KnowledgePackage]:
        terms = retrieval_terms(query)

        if not terms:
            return []

        from hgpt_ai_os.knowledge.retrieval_pipeline import KnowledgeRetrievalPipeline

        results = KnowledgeRetrievalPipeline(repository=self).retrieve(query)
        return [result.item for result in results]
