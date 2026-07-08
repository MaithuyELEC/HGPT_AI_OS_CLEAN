"""Marketplace package registration and discovery."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .marketplace_manifest import MarketplaceManifest, PackageType


@dataclass(frozen=True)
class MarketplaceRegistration:
    manifest: MarketplaceManifest
    repository_id: str = "local"
    installed: bool = False


class MarketplaceRegistry:
    def __init__(self) -> None:
        self._packages: dict[str, MarketplaceRegistration] = {}

    def register_package(
        self, manifest: MarketplaceManifest, *, repository_id: str = "local", installed: bool = False
    ) -> MarketplaceRegistration:
        errors = manifest.validate()
        if errors:
            raise ValueError(errors[0])
        if manifest.package_id in self._packages:
            raise KeyError(f"package already registered: {manifest.package_id}")
        registration = MarketplaceRegistration(manifest=manifest, repository_id=repository_id, installed=installed)
        self._packages[manifest.package_id] = registration
        return registration

    def remove_package(self, package_id: str) -> MarketplaceRegistration:
        registration = self.get(package_id)
        del self._packages[package_id]
        return registration

    def get(self, package_id: str) -> MarketplaceRegistration:
        if package_id not in self._packages:
            raise KeyError(f"package not registered: {package_id}")
        return self._packages[package_id]

    def contains(self, package_id: str) -> bool:
        return package_id in self._packages

    def package_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._packages))

    def discover_package(
        self,
        capability: str | None = None,
        *,
        package_type: PackageType | str | None = None,
        publisher_id: str | None = None,
        platform: str | None = None,
    ) -> tuple[MarketplaceManifest, ...]:
        requested_type = PackageType(package_type) if isinstance(package_type, str) else package_type
        discovered: list[MarketplaceManifest] = []
        for package_id in self.package_ids():
            manifest = self._packages[package_id].manifest
            if capability is not None and not manifest.supports(capability):
                continue
            if requested_type is not None and manifest.package_type is not requested_type:
                continue
            if publisher_id is not None and manifest.publisher.publisher_id != publisher_id:
                continue
            if platform is not None and not manifest.compatibility.supports_platform(platform):
                continue
            discovered.append(manifest)
        return tuple(discovered)

    def publisher_metadata(self, package_id: str) -> Mapping[str, object]:
        return self.get(package_id).manifest.publisher_metadata()

    def version_metadata(self, package_id: str) -> Mapping[str, object]:
        return self.get(package_id).manifest.version_metadata()

    def compatibility_metadata(self, package_id: str) -> Mapping[str, object]:
        return self.get(package_id).manifest.compatibility_metadata()
