"""Marketplace validation services."""

from __future__ import annotations

from dataclasses import dataclass

from .marketplace_manifest import MarketplaceManifest
from .marketplace_registry import MarketplaceRegistry
from .package_compatibility import CompatibilityStatus


@dataclass(frozen=True)
class MarketplaceValidationResult:
    valid: bool
    errors: tuple[str, ...] = ()


class MarketplaceValidator:
    def __init__(
        self,
        *,
        platform_version: str = "1.0.0",
        contract_version: str = "1.0.0",
        provider_version: str = "1.0.0",
        plugin_sdk_version: str = "1.0.0",
        platform: str = "universal",
    ) -> None:
        self.platform_version = platform_version
        self.contract_version = contract_version
        self.provider_version = provider_version
        self.plugin_sdk_version = plugin_sdk_version
        self.platform = platform

    def validate_manifest(self, manifest: MarketplaceManifest) -> MarketplaceValidationResult:
        return self._result(manifest.validate())

    def validate_compatibility(self, manifest: MarketplaceManifest) -> MarketplaceValidationResult:
        status = manifest.compatibility.evaluate(
            platform_version=self.platform_version,
            contract_version=self.contract_version,
            provider_version=self.provider_version,
            plugin_sdk_version=self.plugin_sdk_version,
            platform=self.platform,
        )
        if status is CompatibilityStatus.INCOMPATIBLE:
            return MarketplaceValidationResult(False, ("package is incompatible with this platform",))
        if status is CompatibilityStatus.UPGRADE_REQUIRED:
            return MarketplaceValidationResult(False, ("platform upgrade is required for this package",))
        return MarketplaceValidationResult(True)

    def validate_dependencies(
        self, manifest: MarketplaceManifest, installed_registry: MarketplaceRegistry
    ) -> MarketplaceValidationResult:
        installed = installed_registry.package_ids()
        errors = [
            *(f"missing package dependency: {package_id}" for package_id in manifest.dependencies.missing_required(installed)),
            *(f"conflicting package installed: {package_id}" for package_id in manifest.dependencies.conflict_hits(installed)),
        ]
        return self._result(errors)

    def validate_integrity(self, manifest: MarketplaceManifest) -> MarketplaceValidationResult:
        if not manifest.checksum:
            return MarketplaceValidationResult(False, ("checksum is required",))
        return MarketplaceValidationResult(True)

    def validate_package(
        self, manifest: MarketplaceManifest, installed_registry: MarketplaceRegistry
    ) -> MarketplaceValidationResult:
        errors: list[str] = []
        for result in (
            self.validate_manifest(manifest),
            self.validate_compatibility(manifest),
            self.validate_dependencies(manifest, installed_registry),
            self.validate_integrity(manifest),
        ):
            errors.extend(result.errors)
        return self._result(errors)

    def _result(self, errors: tuple[str, ...] | list[str]) -> MarketplaceValidationResult:
        values = tuple(errors)
        return MarketplaceValidationResult(valid=not values, errors=values)
