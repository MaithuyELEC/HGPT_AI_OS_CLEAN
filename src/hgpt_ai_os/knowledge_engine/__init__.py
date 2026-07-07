"""Universal Knowledge Engine metadata, registry, search, and cache APIs."""

from .knowledge_cache import CacheScope, KnowledgeCache
from .knowledge_catalog import KnowledgeCatalog, KnowledgeDomain
from .knowledge_citation import KnowledgeCitation
from .knowledge_index import (
    KnowledgeIndex,
    KnowledgeIndexEntry,
    KnowledgeSearchQuery,
    KnowledgeSearchResult,
    MemoryKnowledgeIndex,
    SearchMode,
)
from .knowledge_loader import KnowledgeLoader
from .knowledge_manager import KnowledgeHealth, KnowledgeHealthStatus, KnowledgeManager
from .knowledge_metrics import KnowledgeMetrics
from .knowledge_package import KnowledgeCapability, KnowledgePackageMetadata
from .knowledge_policy import KnowledgePolicy, KnowledgeVisibility
from .knowledge_registry import KnowledgeRegistration, KnowledgeRegistry
from .knowledge_search import KnowledgeSearch
from .knowledge_version import KnowledgeVersion, SemanticVersion, VersionCompatibility

__all__ = [
    "CacheScope",
    "KnowledgeCache",
    "KnowledgeCatalog",
    "KnowledgeCapability",
    "KnowledgeCitation",
    "KnowledgeDomain",
    "KnowledgeHealth",
    "KnowledgeHealthStatus",
    "KnowledgeIndex",
    "KnowledgeIndexEntry",
    "KnowledgeLoader",
    "KnowledgeManager",
    "KnowledgeMetrics",
    "KnowledgePackageMetadata",
    "KnowledgePolicy",
    "KnowledgeRegistration",
    "KnowledgeRegistry",
    "KnowledgeSearch",
    "KnowledgeSearchQuery",
    "KnowledgeSearchResult",
    "KnowledgeVisibility",
    "MemoryKnowledgeIndex",
    "SearchMode",
    "SemanticVersion",
    "VersionCompatibility",
    "KnowledgeVersion",
]
