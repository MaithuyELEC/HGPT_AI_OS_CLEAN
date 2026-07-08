"""Marketplace catalog indexes package metadata by package type."""

from __future__ import annotations

from dataclasses import dataclass, field

from .marketplace_manifest import MarketplaceManifest, PackageType


@dataclass
class MarketplaceCatalog:
    entries: dict[str, MarketplaceManifest] = field(default_factory=dict)

    def add(self, manifest: MarketplaceManifest) -> None:
        errors = manifest.validate()
        if errors:
            raise ValueError(errors[0])
        self.entries[manifest.package_id] = manifest

    def remove(self, package_id: str) -> MarketplaceManifest:
        if package_id not in self.entries:
            raise KeyError(f"package not cataloged: {package_id}")
        return self.entries.pop(package_id)

    def by_type(self, package_type: PackageType | str) -> tuple[MarketplaceManifest, ...]:
        requested_type = PackageType(package_type) if isinstance(package_type, str) else package_type
        return tuple(
            self.entries[package_id]
            for package_id in sorted(self.entries)
            if self.entries[package_id].package_type is requested_type
        )

    def search(self, capability: str) -> tuple[MarketplaceManifest, ...]:
        return tuple(
            self.entries[package_id] for package_id in sorted(self.entries) if self.entries[package_id].supports(capability)
        )

    def supported_package_types(self) -> tuple[PackageType, ...]:
        return tuple(PackageType)
