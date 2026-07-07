"""Search abstraction for the Universal Knowledge Engine."""

from __future__ import annotations

from .knowledge_index import KnowledgeIndex, KnowledgeSearchQuery, KnowledgeSearchResult
from .knowledge_metrics import KnowledgeMetrics
from .knowledge_registry import KnowledgeRegistry


class KnowledgeSearch:
    def __init__(
        self,
        registry: KnowledgeRegistry,
        index: KnowledgeIndex,
        metrics: KnowledgeMetrics | None = None,
    ) -> None:
        self.registry = registry
        self.index = index
        self.metrics = metrics

    def search(self, query: KnowledgeSearchQuery) -> tuple[KnowledgeSearchResult, ...]:
        errors = query.validate()
        if errors:
            raise ValueError(errors[0])
        for package_id in query.package_ids:
            registration = self.registry.get(package_id)
            if not registration.enabled:
                raise ValueError(f"knowledge package is disabled: {package_id}")
        if query.mode not in self.index.modes():
            raise ValueError(f"search mode is not supported: {query.mode.value}")
        results = self.index.search(query)
        if self.metrics is not None:
            self.metrics.record_search(len(results))
        return results
