"""Semantic versioning and compatibility support for plugins."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping


class PluginCompatibility(str, Enum):
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
class PluginVersion:
    version: SemanticVersion
    min_sdk_version: SemanticVersion = field(default_factory=lambda: SemanticVersion(1, 0, 0))
    migration_targets: tuple[SemanticVersion, ...] = ()

    @classmethod
    def from_strings(
        cls,
        version: str,
        *,
        min_sdk_version: str = "1.0.0",
        migration_targets: tuple[str, ...] = (),
    ) -> "PluginVersion":
        return cls(
            version=SemanticVersion.parse(version),
            min_sdk_version=SemanticVersion.parse(min_sdk_version),
            migration_targets=tuple(SemanticVersion.parse(target) for target in migration_targets),
        )

    def compatibility_with_sdk(self, sdk_version: str | SemanticVersion) -> PluginCompatibility:
        current_sdk = SemanticVersion.parse(sdk_version)
        if current_sdk.is_compatible_with(self.min_sdk_version):
            return PluginCompatibility.COMPATIBLE
        if any(current_sdk.is_compatible_with(target) for target in self.migration_targets):
            return PluginCompatibility.MIGRATION_AVAILABLE
        return PluginCompatibility.INCOMPATIBLE

    def migration_supported(self, target_version: str | SemanticVersion) -> bool:
        target = SemanticVersion.parse(target_version)
        return target in self.migration_targets

    def as_metadata(self) -> Mapping[str, object]:
        return {
            "version": str(self.version),
            "min_sdk_version": str(self.min_sdk_version),
            "migration_targets": tuple(str(target) for target in self.migration_targets),
        }
