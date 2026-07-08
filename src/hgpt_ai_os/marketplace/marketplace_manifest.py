"""Marketplace package manifest metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from .package_compatibility import PackageCompatibility, SemanticVersion
from .package_dependencies import DependencySet
from .publisher_profile import PublisherProfile


class PackageType(str, Enum):
    PLUGIN = "plugin"
    SKILL = "skill"
    KNOWLEDGE_PACK = "knowledge_pack"
    AGENT_PACK = "agent_pack"
    WORKFLOW_PACK = "workflow_pack"
    TEMPLATE = "template"
    ENTERPRISE_PACK = "enterprise_pack"
    DIGITAL_FACTORY_PACK = "digital_factory_pack"


@dataclass(frozen=True)
class MarketplaceManifest:
    package_id: str
    package_type: PackageType
    publisher: PublisherProfile
    version: str
    license: str
    checksum: str
    signature_reference: str = ""
    dependencies: DependencySet = field(default_factory=DependencySet)
    capabilities: tuple[str, ...] = ()
    compatibility: PackageCompatibility = field(default_factory=PackageCompatibility)
    minimum_platform_version: str = "1.0.0"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "MarketplaceManifest":
        return cls(
            package_id=str(data.get("package_id", "")).strip(),
            package_type=PackageType(str(data.get("package_type", "plugin")).strip().lower()),
            publisher=PublisherProfile.from_dict(data.get("publisher", {})),
            version=str(data.get("version", "")).strip(),
            license=str(data.get("license", "")).strip(),
            checksum=str(data.get("checksum", "")).strip(),
            signature_reference=str(data.get("signature_reference", "")).strip(),
            dependencies=DependencySet.from_dict(data.get("dependencies", {})),
            capabilities=tuple(str(value).strip().lower() for value in data.get("capabilities", ())),
            compatibility=PackageCompatibility.from_dict(data.get("compatibility", {})),
            minimum_platform_version=str(data.get("minimum_platform_version", "1.0.0")).strip(),
            metadata=dict(data.get("metadata", {})),
        )

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.package_id:
            errors.append("package_id is required")
        if not self.version:
            errors.append("version is required")
        else:
            try:
                SemanticVersion.parse(self.version)
            except ValueError:
                errors.append("version must be semantic version")
        if not self.license:
            errors.append("license is required")
        if not self.checksum:
            errors.append("checksum is required")
        try:
            SemanticVersion.parse(self.minimum_platform_version)
        except ValueError:
            errors.append("minimum_platform_version must be semantic version")
        if not self.capabilities:
            errors.append("at least one capability is required")
        if len(set(self.capabilities)) != len(self.capabilities):
            errors.append("capabilities must be unique")
        errors.extend(self.publisher.validate())
        errors.extend(self.dependencies.validate())
        errors.extend(self.compatibility.validate())
        return tuple(errors)

    def supports(self, capability: str) -> bool:
        return capability.strip().lower() in self.capabilities

    def publisher_metadata(self) -> Mapping[str, object]:
        return self.publisher.as_dict()

    def version_metadata(self) -> Mapping[str, object]:
        return {"package_id": self.package_id, "version": self.version}

    def compatibility_metadata(self) -> Mapping[str, object]:
        return self.compatibility.as_dict()

    def as_dict(self) -> Mapping[str, object]:
        return {
            "package_id": self.package_id,
            "package_type": self.package_type.value,
            "publisher": self.publisher.as_dict(),
            "version": self.version,
            "license": self.license,
            "checksum": self.checksum,
            "signature_reference": self.signature_reference,
            "dependencies": self.dependencies.as_dict(),
            "capabilities": self.capabilities,
            "compatibility": self.compatibility.as_dict(),
            "minimum_platform_version": self.minimum_platform_version,
            "metadata": dict(self.metadata),
        }
