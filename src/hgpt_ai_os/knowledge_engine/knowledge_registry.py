"""Knowledge package registration, discovery, and metadata lookup."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .knowledge_catalog import KnowledgeDomain
from .knowledge_package import KnowledgeCapability, KnowledgePackageMetadata


@dataclass
class KnowledgeRegistration:
    metadata: KnowledgePackageMetadata
    enabled: bool = False


class KnowledgeRegistry:
    def __init__(self) -> None:
        self._packages: dict[str, KnowledgeRegistration] = {}

    def register_package(self, metadata: KnowledgePackageMetadata) -> None:
        errors = metadata.validate()
        if errors:
            raise ValueError(errors[0])
        if metadata.package_id in self._packages:
            raise KeyError(f"knowledge package already registered: {metadata.package_id}")
        self._packages[metadata.package_id] = KnowledgeRegistration(metadata=metadata)

    def unregister_package(self, package_id: str) -> KnowledgeRegistration:
        if package_id not in self._packages:
            raise KeyError(f"knowledge package not registered: {package_id}")
        return self._packages.pop(package_id)

    def contains(self, package_id: str) -> bool:
        return package_id in self._packages

    def get(self, package_id: str) -> KnowledgeRegistration:
        if package_id not in self._packages:
            raise KeyError(f"knowledge package not registered: {package_id}")
        return self._packages[package_id]

    def metadata(self, package_id: str) -> KnowledgePackageMetadata:
        return self.get(package_id).metadata

    def package_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._packages))

    def discover_package(
        self,
        capability: KnowledgeCapability | None = None,
        domain: KnowledgeDomain | None = None,
        *,
        enabled_only: bool = False,
    ) -> tuple[KnowledgePackageMetadata, ...]:
        discovered: list[KnowledgePackageMetadata] = []
        for package_id in self.package_ids():
            registration = self._packages[package_id]
            metadata = registration.metadata
            if enabled_only and not registration.enabled:
                continue
            if capability is not None and not metadata.supports(capability):
                continue
            if domain is not None and metadata.domain is not domain:
                continue
            discovered.append(metadata)
        return tuple(discovered)

    def version_metadata(self, package_id: str) -> Mapping[str, object]:
        metadata = self.metadata(package_id)
        return {"package_id": metadata.package_id, **metadata.version_metadata()}

    def capability_metadata(self, package_id: str) -> tuple[KnowledgeCapability, ...]:
        return self.metadata(package_id).capability_metadata()

    def set_enabled(self, package_id: str, enabled: bool) -> KnowledgeRegistration:
        registration = self.get(package_id)
        registration.enabled = enabled
        return registration
