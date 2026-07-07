"""Metadata-only knowledge package model."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from .knowledge_catalog import KnowledgeCatalog, KnowledgeDomain
from .knowledge_policy import KnowledgePolicy
from .knowledge_version import KnowledgeVersion


class KnowledgeCapability(str, Enum):
    KEYWORD = "keyword"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


@dataclass(frozen=True)
class KnowledgePackageMetadata:
    package_id: str
    name: str
    version: KnowledgeVersion
    domain: KnowledgeDomain = KnowledgeDomain.GENERAL
    capabilities: tuple[KnowledgeCapability, ...] = (KnowledgeCapability.KEYWORD,)
    dependencies: tuple[str, ...] = ()
    policy: KnowledgePolicy = field(default_factory=KnowledgePolicy)
    description: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def supports(self, capability: KnowledgeCapability) -> bool:
        return capability in self.capabilities

    def validate(self, catalog: KnowledgeCatalog | None = None) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.package_id.strip():
            errors.append("package_id is required")
        if not self.name.strip():
            errors.append("name is required")
        if catalog is not None and not catalog.contains(self.domain):
            errors.append(f"domain is not registered: {self.domain.value}")
        if not self.capabilities:
            errors.append("at least one capability is required")
        if len(set(self.dependencies)) != len(self.dependencies):
            errors.append("dependencies must be unique")
        return tuple(errors)

    def version_metadata(self) -> Mapping[str, Any]:
        return self.version.as_metadata()

    def capability_metadata(self) -> tuple[KnowledgeCapability, ...]:
        return self.capabilities
