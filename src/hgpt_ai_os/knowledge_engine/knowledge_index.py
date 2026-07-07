"""Abstract index layer for keyword, semantic, and hybrid search modes."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, runtime_checkable

from .knowledge_citation import KnowledgeCitation


class SearchMode(str, Enum):
    KEYWORD = "keyword"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


@dataclass(frozen=True)
class KnowledgeIndexEntry:
    entry_id: str
    package_id: str
    text: str
    citations: tuple[KnowledgeCitation, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class KnowledgeSearchQuery:
    text: str
    package_ids: tuple[str, ...] = ()
    mode: SearchMode = SearchMode.KEYWORD
    limit: int = 10

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.text.strip():
            errors.append("search text is required")
        if self.limit < 1:
            errors.append("limit must be greater than zero")
        return tuple(errors)


@dataclass(frozen=True)
class KnowledgeSearchResult:
    entry_id: str
    package_id: str
    text: str
    score: float
    citations: tuple[KnowledgeCitation, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@runtime_checkable
class KnowledgeIndex(Protocol):
    def modes(self) -> tuple[SearchMode, ...]:
        """Return search modes supported by this index."""

    def search(self, query: KnowledgeSearchQuery) -> tuple[KnowledgeSearchResult, ...]:
        """Return ranked search results for a validated query."""


class MemoryKnowledgeIndex:
    def __init__(self, entries: tuple[KnowledgeIndexEntry, ...] = ()) -> None:
        self._entries: dict[str, KnowledgeIndexEntry] = {entry.entry_id: entry for entry in entries}

    def modes(self) -> tuple[SearchMode, ...]:
        return (SearchMode.KEYWORD, SearchMode.SEMANTIC, SearchMode.HYBRID)

    def add(self, entry: KnowledgeIndexEntry) -> None:
        if not entry.entry_id.strip():
            raise ValueError("entry_id is required")
        if not entry.package_id.strip():
            raise ValueError("package_id is required")
        self._entries[entry.entry_id] = entry

    def search(self, query: KnowledgeSearchQuery) -> tuple[KnowledgeSearchResult, ...]:
        errors = query.validate()
        if errors:
            raise ValueError(errors[0])
        if query.mode is not SearchMode.KEYWORD:
            return ()
        terms = tuple(term.lower() for term in query.text.split() if term.strip())
        package_filter = set(query.package_ids)
        results: list[KnowledgeSearchResult] = []
        for entry in self._entries.values():
            if package_filter and entry.package_id not in package_filter:
                continue
            text = entry.text.lower()
            score = sum(1 for term in terms if term in text) / max(1, len(terms))
            if score > 0:
                results.append(
                    KnowledgeSearchResult(
                        entry_id=entry.entry_id,
                        package_id=entry.package_id,
                        text=entry.text,
                        score=score,
                        citations=entry.citations,
                        metadata=entry.metadata,
                    )
                )
        return tuple(sorted(results, key=lambda result: (-result.score, result.entry_id))[: query.limit])
