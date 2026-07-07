"""Lifecycle manager for Universal Knowledge Engine packages."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from time import perf_counter
from typing import Any, Mapping

from .knowledge_loader import KnowledgeLoader
from .knowledge_metrics import KnowledgeMetrics
from .knowledge_package import KnowledgePackageMetadata
from .knowledge_registry import KnowledgeRegistry


class KnowledgeHealthStatus(str, Enum):
    EMPTY = "empty"
    READY = "ready"
    DEGRADED = "degraded"


@dataclass(frozen=True)
class KnowledgeHealth:
    status: KnowledgeHealthStatus
    package_count: int
    enabled_count: int
    errors: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


class KnowledgeManager:
    def __init__(
        self,
        registry: KnowledgeRegistry | None = None,
        loader: KnowledgeLoader | None = None,
        metrics: KnowledgeMetrics | None = None,
    ) -> None:
        self.registry = registry or KnowledgeRegistry()
        self.loader = loader or KnowledgeLoader()
        self.metrics = metrics or KnowledgeMetrics()

    def load_package(self, metadata: KnowledgePackageMetadata) -> KnowledgePackageMetadata:
        start = perf_counter()
        self.registry.register_package(metadata)
        self.metrics.record_packages(len(self.registry.package_ids()))
        self.metrics.record_load_time(perf_counter() - start)
        return metadata

    def load_manifest(self, manifest: Mapping[str, Any]) -> KnowledgePackageMetadata:
        metadata = self.loader.load_manifest(manifest)
        dependency_errors = self.loader.validate_dependencies(metadata, self.registry)
        if dependency_errors:
            raise ValueError(dependency_errors[0])
        return self.load_package(metadata)

    def load_directory(self, root: str | Path) -> tuple[KnowledgePackageMetadata, ...]:
        start = perf_counter()
        loaded = self.loader.load_directory(root, self.registry)
        self.metrics.record_packages(len(self.registry.package_ids()))
        self.metrics.record_load_time(perf_counter() - start)
        return loaded

    def enable(self, package_id: str) -> KnowledgePackageMetadata:
        return self.registry.set_enabled(package_id, True).metadata

    def disable(self, package_id: str) -> KnowledgePackageMetadata:
        return self.registry.set_enabled(package_id, False).metadata

    def refresh(self, package_id: str) -> KnowledgePackageMetadata:
        metadata = self.registry.metadata(package_id)
        errors = self.validate(package_id)
        if errors:
            raise ValueError(errors[0])
        return metadata

    def validate(self, package_id: str) -> tuple[str, ...]:
        metadata = self.registry.metadata(package_id)
        errors = list(self.loader.validate_manifest(metadata))
        errors.extend(self.loader.validate_dependencies(metadata, self.registry))
        return tuple(errors)

    def health(self) -> KnowledgeHealth:
        package_ids = self.registry.package_ids()
        errors = tuple(
            error
            for package_id in package_ids
            for error in self.validate(package_id)
        )
        enabled_count = sum(1 for package_id in package_ids if self.registry.get(package_id).enabled)
        if not package_ids:
            status = KnowledgeHealthStatus.EMPTY
        elif errors:
            status = KnowledgeHealthStatus.DEGRADED
        else:
            status = KnowledgeHealthStatus.READY
        return KnowledgeHealth(
            status=status,
            package_count=len(package_ids),
            enabled_count=enabled_count,
            errors=errors,
            metadata=self.metrics.snapshot(),
        )
