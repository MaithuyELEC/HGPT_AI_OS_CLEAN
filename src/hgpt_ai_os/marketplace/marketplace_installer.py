"""Architecture-only marketplace installer state model."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .marketplace_manifest import MarketplaceManifest
from .marketplace_registry import MarketplaceRegistry
from .marketplace_validator import MarketplaceValidator


class InstallAction(str, Enum):
    INSTALL = "install"
    UNINSTALL = "uninstall"
    UPGRADE = "upgrade"
    DOWNGRADE = "downgrade"
    ROLLBACK = "rollback"


@dataclass(frozen=True)
class InstallPlan:
    action: InstallAction
    package_id: str
    version: str
    dependency_validation: bool
    compatibility_validation: bool


class MarketplaceInstaller:
    def __init__(self, registry: MarketplaceRegistry | None = None, validator: MarketplaceValidator | None = None) -> None:
        self.registry = registry or MarketplaceRegistry()
        self.validator = validator or MarketplaceValidator()
        self._history: dict[str, list[MarketplaceManifest]] = {}

    def install(self, manifest: MarketplaceManifest) -> InstallPlan:
        validation = self.validator.validate_package(manifest, self.registry)
        if not validation.valid:
            raise ValueError(validation.errors[0])
        self.registry.register_package(manifest, installed=True)
        self._history.setdefault(manifest.package_id, []).append(manifest)
        return self._plan(InstallAction.INSTALL, manifest, True, True)

    def uninstall(self, package_id: str) -> InstallPlan:
        registration = self.registry.remove_package(package_id)
        return self._plan(InstallAction.UNINSTALL, registration.manifest, True, True)

    def upgrade(self, manifest: MarketplaceManifest) -> InstallPlan:
        validation = self.validator.validate_package(manifest, self.registry)
        if not validation.valid:
            raise ValueError(validation.errors[0])
        if self.registry.contains(manifest.package_id):
            self.registry.remove_package(manifest.package_id)
        return self._replace(InstallAction.UPGRADE, manifest, validate=False)

    def downgrade(self, manifest: MarketplaceManifest) -> InstallPlan:
        validation = self.validator.validate_package(manifest, self.registry)
        if not validation.valid:
            raise ValueError(validation.errors[0])
        if self.registry.contains(manifest.package_id):
            self.registry.remove_package(manifest.package_id)
        return self._replace(InstallAction.DOWNGRADE, manifest, validate=False)

    def rollback(self, package_id: str) -> InstallPlan:
        history = self._history.get(package_id, ())
        if len(history) < 2:
            raise ValueError(f"rollback metadata is unavailable for package: {package_id}")
        previous = history[-2]
        if self.registry.contains(package_id):
            self.registry.remove_package(package_id)
        self.registry.register_package(previous, installed=True)
        self._history[package_id].append(previous)
        return self._plan(InstallAction.ROLLBACK, previous, True, True)

    def history(self, package_id: str) -> tuple[MarketplaceManifest, ...]:
        return tuple(self._history.get(package_id, ()))

    def _replace(self, action: InstallAction, manifest: MarketplaceManifest, *, validate: bool = True) -> InstallPlan:
        if validate:
            validation = self.validator.validate_package(manifest, self.registry)
            if not validation.valid:
                raise ValueError(validation.errors[0])
        self.registry.register_package(manifest, installed=True)
        self._history.setdefault(manifest.package_id, []).append(manifest)
        return self._plan(action, manifest, True, True)

    def _plan(
        self,
        action: InstallAction,
        manifest: MarketplaceManifest,
        dependency_validation: bool,
        compatibility_validation: bool,
    ) -> InstallPlan:
        return InstallPlan(
            action=action,
            package_id=manifest.package_id,
            version=manifest.version,
            dependency_validation=dependency_validation,
            compatibility_validation=compatibility_validation,
        )
