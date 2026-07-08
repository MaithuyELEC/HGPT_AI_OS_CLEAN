"""Marketplace package compatibility metadata."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class CompatibilityStatus(str, Enum):
    COMPATIBLE = "compatible"
    UPGRADE_REQUIRED = "upgrade_required"
    INCOMPATIBLE = "incompatible"


@dataclass(frozen=True, order=True)
class SemanticVersion:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, value: str) -> "SemanticVersion":
        parts = value.strip().split(".")
        if len(parts) != 3 or not all(part.isdigit() for part in parts):
            raise ValueError(f"invalid semantic version: {value}")
        return cls(*(int(part) for part in parts))

    def supports_minimum(self, minimum: str) -> bool:
        return self >= SemanticVersion.parse(minimum)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


@dataclass(frozen=True)
class PackageCompatibility:
    platform_version: str = "1.0.0"
    contract_version: str = "1.0.0"
    provider_version: str = "1.0.0"
    plugin_sdk_version: str = "1.0.0"
    supported_platforms: tuple[str, ...] = ("universal",)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | None) -> "PackageCompatibility":
        values = data or {}
        return cls(
            platform_version=str(values.get("platform_version", "1.0.0")).strip(),
            contract_version=str(values.get("contract_version", "1.0.0")).strip(),
            provider_version=str(values.get("provider_version", "1.0.0")).strip(),
            plugin_sdk_version=str(values.get("plugin_sdk_version", "1.0.0")).strip(),
            supported_platforms=tuple(
                str(value).strip().lower() for value in values.get("supported_platforms", ("universal",))
            ),
        )

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        for label, value in (
            ("platform_version", self.platform_version),
            ("contract_version", self.contract_version),
            ("provider_version", self.provider_version),
            ("plugin_sdk_version", self.plugin_sdk_version),
        ):
            try:
                SemanticVersion.parse(value)
            except ValueError:
                errors.append(f"{label} must be semantic version")
        if not self.supported_platforms:
            errors.append("at least one supported platform is required")
        if len(set(self.supported_platforms)) != len(self.supported_platforms):
            errors.append("supported platforms must be unique")
        return tuple(errors)

    def supports_platform(self, platform: str) -> bool:
        normalized = platform.strip().lower()
        return "universal" in self.supported_platforms or normalized in self.supported_platforms

    def evaluate(
        self,
        *,
        platform_version: str,
        contract_version: str,
        provider_version: str,
        plugin_sdk_version: str,
        platform: str = "universal",
    ) -> CompatibilityStatus:
        if not self.supports_platform(platform):
            return CompatibilityStatus.INCOMPATIBLE
        checks = (
            SemanticVersion.parse(platform_version).supports_minimum(self.platform_version),
            SemanticVersion.parse(contract_version).supports_minimum(self.contract_version),
            SemanticVersion.parse(provider_version).supports_minimum(self.provider_version),
            SemanticVersion.parse(plugin_sdk_version).supports_minimum(self.plugin_sdk_version),
        )
        return CompatibilityStatus.COMPATIBLE if all(checks) else CompatibilityStatus.UPGRADE_REQUIRED

    def as_dict(self) -> Mapping[str, object]:
        return {
            "platform_version": self.platform_version,
            "contract_version": self.contract_version,
            "provider_version": self.provider_version,
            "plugin_sdk_version": self.plugin_sdk_version,
            "supported_platforms": self.supported_platforms,
        }
