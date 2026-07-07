"""Knowledge package and retrieval contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, runtime_checkable

from .diagnostics_contract import ContractError, PlatformErrorCode

CONTRACT_VERSION = "2.0.0"
CONTRACT_LIFECYCLE = ("indexed", "validated", "published", "queried", "deprecated")
EXTENSION_RULES = (
    "Knowledge sources must include stable source identifiers.",
    "Citations must preserve source and locator fields.",
    "Version upgrades must be represented by KnowledgeVersion.",
)
BACKWARD_COMPATIBILITY_NOTES = (
    "Knowledge contracts are separate from current retrieval implementation details.",
    "Older hosts may ignore ranking metadata while preserving citation identity.",
)


class KnowledgeSourceType(str, Enum):
    DOCUMENT = "document"
    DATABASE = "database"
    WEB = "web"
    PACKAGE = "package"
    MANUAL = "manual"


@dataclass(frozen=True)
class KnowledgeVersion:
    version: str
    checksum: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(("KnowledgeVersion.version", self.version))


@dataclass(frozen=True)
class KnowledgeSource:
    source_id: str
    source_type: KnowledgeSourceType
    locator: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(("KnowledgeSource.source_id", self.source_id), ("KnowledgeSource.locator", self.locator))


@dataclass(frozen=True)
class KnowledgeCitation:
    source_id: str
    locator: str
    excerpt: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(("KnowledgeCitation.source_id", self.source_id), ("KnowledgeCitation.locator", self.locator))


@dataclass(frozen=True)
class KnowledgePackage:
    package_id: str
    version: KnowledgeVersion
    sources: tuple[KnowledgeSource, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        errors = list(_require_text(("KnowledgePackage.package_id", self.package_id)))
        errors.extend(self.version.validate())
        for source in self.sources:
            errors.extend(source.validate())
        return tuple(errors)


@dataclass(frozen=True)
class KnowledgeQuery:
    query_id: str
    text: str
    package_ids: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(("KnowledgeQuery.query_id", self.query_id), ("KnowledgeQuery.text", self.text))


@dataclass(frozen=True)
class KnowledgeResult:
    query_id: str
    content: str
    citations: tuple[KnowledgeCitation, ...] = ()
    score: float | None = None
    errors: tuple[ContractError, ...] = ()

    def validate(self) -> tuple[ContractError, ...]:
        errors = list(_require_text(("KnowledgeResult.query_id", self.query_id)))
        if self.score is not None and not 0 <= self.score <= 1:
            errors.append(_validation_error("KnowledgeResult.score must be between 0 and 1"))
        for citation in self.citations:
            errors.extend(citation.validate())
        return tuple(errors)


@runtime_checkable
class KnowledgeIndex(Protocol):
    def query(self, query: KnowledgeQuery) -> tuple[KnowledgeResult, ...]:
        """Return knowledge results for a validated query."""


class KnowledgeRepository(ABC):
    @abstractmethod
    def packages(self) -> tuple[KnowledgePackage, ...]:
        """Return available knowledge packages."""

    @abstractmethod
    def search(self, query: KnowledgeQuery) -> tuple[KnowledgeResult, ...]:
        """Search knowledge through the stable query/result contract."""


def _require_text(*fields: tuple[str, str]) -> tuple[ContractError, ...]:
    return tuple(_validation_error(f"{name} is required") for name, value in fields if not value.strip())


def _validation_error(message: str) -> ContractError:
    return ContractError(PlatformErrorCode.CONTRACT_VALIDATION_FAILED, message, source="knowledge_contract")
