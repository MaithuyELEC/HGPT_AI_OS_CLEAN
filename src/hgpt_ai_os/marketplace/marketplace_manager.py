"""Marketplace foundation facade."""

from __future__ import annotations

from dataclasses import dataclass, field

from .marketplace_catalog import MarketplaceCatalog
from .marketplace_installer import MarketplaceInstaller
from .marketplace_manifest import MarketplaceManifest
from .marketplace_metrics import MarketplaceMetrics
from .marketplace_registry import MarketplaceRegistry
from .marketplace_repository import MarketplaceRepository, RepositoryRegistry
from .marketplace_validator import MarketplaceValidator


@dataclass
class MarketplaceManager:
    registry: MarketplaceRegistry = field(default_factory=MarketplaceRegistry)
    catalog: MarketplaceCatalog = field(default_factory=MarketplaceCatalog)
    repositories: RepositoryRegistry = field(default_factory=RepositoryRegistry)
    validator: MarketplaceValidator = field(default_factory=MarketplaceValidator)
    metrics: MarketplaceMetrics = field(default_factory=MarketplaceMetrics)

    def __post_init__(self) -> None:
        self.installer = MarketplaceInstaller(self.registry, self.validator)

    def register_repository(self, repository: MarketplaceRepository) -> MarketplaceRepository:
        return self.repositories.register(repository)

    def register_package(self, manifest: MarketplaceManifest, *, repository_id: str = "local") -> None:
        self.registry.register_package(manifest, repository_id=repository_id)
        self.catalog.add(manifest)
        self.metrics.set_package_count(len(self.registry.package_ids()))

    def remove_package(self, package_id: str) -> MarketplaceManifest:
        registration = self.registry.remove_package(package_id)
        if package_id in self.catalog.entries:
            self.catalog.remove(package_id)
        self.metrics.set_package_count(len(self.registry.package_ids()))
        return registration.manifest

    def install(self, manifest: MarketplaceManifest):
        plan = self.installer.install(manifest)
        self.catalog.add(manifest)
        self.metrics.record_install()
        self.metrics.set_package_count(len(self.registry.package_ids()))
        return plan
