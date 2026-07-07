"""Semantic version and compatibility support for knowledge packages."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class VersionCompatibility(str, Enum):
    COMPATIBLE = "compatible"
    MIGRATION_AVAILABLE = "migration_available"
    INCOMPATIBLE = "incompatible"


@dataclass(frozen=True, order=True)
class SemanticVersion:
    major: int
    minor: int = 0
    patch: int = 0

    @classmethod
    def parse(cls, value: str | "SemanticVersion") -> "SemanticVersion":
        if isinstance(value, SemanticVersion):
            return value
        parts = value.strip().split(".")
        if len(parts) not in (2, 3) or any(not part.isdigit() for part in parts):
            raise ValueError(f"invalid semantic version: {value}")
        numbers = [int(part) for part in parts]
        if len(numbers) == 2:
            numbers.append(0)
        return cls(*numbers)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def is_compatible_with(self, required: str | "SemanticVersion") -> bool:
        required_version = SemanticVersion.parse(required)
        return self.major == required_version.major and self >= required_version


@dataclass(frozen=True)
class KnowledgeVersion:
    version: SemanticVersion
    min_engine_version: SemanticVersion = field(default_factory=lambda: SemanticVersion(1, 0, 0))
    migration_targets: tuple[SemanticVersion, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_strings(
        cls,
        version: str,
        *,
        min_engine_version: str = "1.0.0",
        migration_targets: tuple[str, ...] = (),
        metadata: Mapping[str, Any] | None = None,
    ) -> "KnowledgeVersion":
        return cls(
            version=SemanticVersion.parse(version),
            min_engine_version=SemanticVersion.parse(min_engine_version),
            migration_targets=tuple(SemanticVersion.parse(target) for target in migration_targets),
            metadata=metadata or {},
        )

    def compatibility_with_engine(self, engine_version: str | SemanticVersion) -> VersionCompatibility:
        current_engine = SemanticVersion.parse(engine_version)
        if current_engine.is_compatible_with(self.min_engine_version):
            return VersionCompatibility.COMPATIBLE
        if any(current_engine.is_compatible_with(target) for target in self.migration_targets):
            return VersionCompatibility.MIGRATION_AVAILABLE
        return VersionCompatibility.INCOMPATIBLE

    def migration_supported(self, target_version: str | SemanticVersion) -> bool:
        target = SemanticVersion.parse(target_version)
        return target in self.migration_targets

    def as_metadata(self) -> Mapping[str, Any]:
        return {
            "version": str(self.version),
            "min_engine_version": str(self.min_engine_version),
            "migration_targets": tuple(str(target) for target in self.migration_targets),
            "metadata": dict(self.metadata),
        }
