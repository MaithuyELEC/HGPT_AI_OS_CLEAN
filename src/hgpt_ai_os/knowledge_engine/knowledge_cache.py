"""Scoped in-memory cache for Universal Knowledge Engine sessions."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .knowledge_metrics import KnowledgeMetrics


class CacheScope(str, Enum):
    SESSION = "session"
    PROJECT = "project"
    PACKAGE = "package"


@dataclass
class KnowledgeCache:
    metrics: KnowledgeMetrics | None = None
    _values: dict[CacheScope, dict[str, dict[str, Any]]] = field(default_factory=dict)

    def set(self, scope: CacheScope, namespace: str, key: str, value: Any) -> None:
        self._values.setdefault(scope, {}).setdefault(namespace, {})[key] = value

    def get(self, scope: CacheScope, namespace: str, key: str, default: Any = None) -> Any:
        namespace_values = self._values.get(scope, {}).get(namespace, {})
        if key in namespace_values:
            if self.metrics is not None:
                self.metrics.record_cache_hit()
            return namespace_values[key]
        if self.metrics is not None:
            self.metrics.record_cache_miss()
        return default

    def clear(self, scope: CacheScope | None = None, namespace: str | None = None) -> None:
        if scope is None:
            self._values.clear()
            return
        if namespace is None:
            self._values.pop(scope, None)
            return
        self._values.get(scope, {}).pop(namespace, None)

    def scopes(self) -> tuple[CacheScope, ...]:
        return tuple(scope for scope in CacheScope if scope in self._values)
