from __future__ import annotations

import unittest

from hgpt_ai_os.marketplace import (
    CertificateMetadata,
    ChannelPolicy,
    CompatibilityStatus,
    DependencyKind,
    InstallAction,
    MarketplaceCatalog,
    MarketplaceChannel,
    MarketplaceInstaller,
    MarketplaceManager,
    MarketplaceManifest,
    MarketplaceMetrics,
    MarketplaceRepository,
    MarketplaceSecurity,
    MarketplaceSigning,
    MarketplaceUpdates,
    MarketplaceValidator,
    PackageCompatibility,
    PackageDependency,
    PackageType,
    PublisherProfile,
    PublisherTrustLevel,
    RepositoryRegistry,
    RepositoryType,
    ReviewRecord,
    ReviewState,
    SignatureMetadata,
    SigningStatus,
    TrustDecision,
    VerificationStatus,
)


def manifest(package_id: str = "engineering-pack", version: str = "1.0.0") -> MarketplaceManifest:
    return MarketplaceManifest.from_dict(
        {
            "package_id": package_id,
            "package_type": "digital_factory_pack",
            "publisher": {
                "publisher_id": "lucid",
                "organization": "LUCID",
                "trust_level": "official",
                "verification_status": "verified",
                "signing_status": "signed",
            },
            "version": version,
            "license": "Commercial",
            "checksum": "sha256:abc123",
            "signature_reference": "sig://engineering-pack",
            "dependencies": {"required": [], "optional": [], "conflicts": [], "replaces": []},
            "capabilities": ["engineering", "steel"],
            "compatibility": {
                "platform_version": "1.0.0",
                "contract_version": "1.0.0",
                "provider_version": "1.0.0",
                "plugin_sdk_version": "1.0.0",
                "supported_platforms": ["universal"],
            },
            "minimum_platform_version": "1.0.0",
            "metadata": {"permissions": ["filesystem"]},
        }
    )


class MarketplaceManifestTests(unittest.TestCase):
    def test_manifest_metadata_and_validation(self):
        metadata = manifest()

        self.assertEqual(metadata.package_id, "engineering-pack")
        self.assertEqual(metadata.package_type, PackageType.DIGITAL_FACTORY_PACK)
        self.assertTrue(metadata.supports("steel"))
        self.assertEqual(metadata.publisher_metadata()["publisher_id"], "lucid")
        self.assertEqual(metadata.version_metadata()["version"], "1.0.0")
        self.assertEqual(metadata.compatibility_metadata()["platform_version"], "1.0.0")
        self.assertEqual(metadata.validate(), ())

    def test_manifest_rejects_required_metadata_gaps(self):
        metadata = MarketplaceManifest.from_dict(
            {
                "package_id": "",
                "package_type": "plugin",
                "publisher": {"publisher_id": ""},
                "version": "",
                "license": "",
                "checksum": "",
                "capabilities": [],
            }
        )

        self.assertIn("package_id is required", metadata.validate())
        self.assertIn("publisher_id is required", metadata.validate())
        self.assertIn("checksum is required", metadata.validate())


class MarketplaceRegistryCatalogRepositoryTests(unittest.TestCase):
    def test_registry_register_remove_discover_and_metadata(self):
        manager = MarketplaceManager()
        metadata = manifest()

        manager.register_package(metadata, repository_id="official")

        self.assertTrue(manager.registry.contains("engineering-pack"))
        self.assertEqual(manager.registry.publisher_metadata("engineering-pack")["trust_level"], "official")
        self.assertEqual(manager.registry.version_metadata("engineering-pack")["version"], "1.0.0")
        self.assertEqual(manager.registry.compatibility_metadata("engineering-pack")["plugin_sdk_version"], "1.0.0")
        self.assertEqual(manager.registry.discover_package("steel"), (metadata,))
        self.assertEqual(manager.catalog.by_type(PackageType.DIGITAL_FACTORY_PACK), (metadata,))
        self.assertEqual(manager.remove_package("engineering-pack"), metadata)

    def test_catalog_supports_all_required_package_types(self):
        catalog = MarketplaceCatalog()

        self.assertEqual(
            set(catalog.supported_package_types()),
            {
                PackageType.PLUGIN,
                PackageType.SKILL,
                PackageType.KNOWLEDGE_PACK,
                PackageType.AGENT_PACK,
                PackageType.WORKFLOW_PACK,
                PackageType.TEMPLATE,
                PackageType.ENTERPRISE_PACK,
                PackageType.DIGITAL_FACTORY_PACK,
            },
        )

    def test_repository_registry_architecture_types(self):
        registry = RepositoryRegistry()
        repository = MarketplaceRepository("official", RepositoryType.OFFICIAL, "Official Marketplace", priority=1)

        registry.register(repository)

        self.assertEqual(registry.list(enabled_only=True), (repository,))
        self.assertEqual(registry.remove("official"), repository)


class MarketplaceInstallerValidatorTests(unittest.TestCase):
    def test_install_upgrade_downgrade_uninstall_and_rollback(self):
        installer = MarketplaceInstaller()
        first = manifest(version="1.0.0")
        second = manifest(version="1.1.0")

        self.assertEqual(installer.install(first).action, InstallAction.INSTALL)
        self.assertEqual(installer.upgrade(second).action, InstallAction.UPGRADE)
        self.assertEqual(installer.rollback("engineering-pack").version, "1.0.0")
        self.assertEqual(installer.downgrade(first).action, InstallAction.DOWNGRADE)
        self.assertEqual(installer.uninstall("engineering-pack").action, InstallAction.UNINSTALL)

    def test_validator_reports_dependency_and_compatibility_errors(self):
        data = dict(manifest("dependent-pack").as_dict())
        data["dependencies"] = {"required": [{"package_id": "base-pack", "min_version": "1.0.0"}]}
        data["compatibility"] = {"platform_version": "2.0.0", "supported_platforms": ["windows"]}
        metadata = MarketplaceManifest.from_dict(data)
        validator = MarketplaceValidator(platform_version="1.0.0", platform="linux")

        result = validator.validate_package(metadata, MarketplaceManager().registry)

        self.assertFalse(result.valid)
        self.assertIn("package is incompatible with this platform", result.errors)
        self.assertIn("missing package dependency: base-pack", result.errors)


class MarketplaceCompatibilityDependenciesTests(unittest.TestCase):
    def test_compatibility_and_dependency_metadata(self):
        compatibility = PackageCompatibility.from_dict(
            {
                "platform_version": "1.0.0",
                "contract_version": "1.0.0",
                "provider_version": "1.0.0",
                "plugin_sdk_version": "1.0.0",
                "supported_platforms": ["windows"],
            }
        )
        dependency = PackageDependency.from_value(
            {"package_id": "office-pack", "min_version": "1.2.0"}, default_kind=DependencyKind.REQUIRED
        )

        self.assertEqual(
            compatibility.evaluate(
                platform_version="1.1.0",
                contract_version="1.0.0",
                provider_version="1.0.0",
                plugin_sdk_version="1.0.0",
                platform="windows",
            ),
            CompatibilityStatus.COMPATIBLE,
        )
        self.assertEqual(dependency.package_id, "office-pack")
        self.assertEqual(dependency.validate(), ())


class MarketplaceSecuritySigningReviewUpdatesMetricsTests(unittest.TestCase):
    def test_security_signing_review_channels_updates_publisher_and_metrics(self):
        metadata = manifest()
        security = MarketplaceSecurity().review(metadata)
        certificate = CertificateMetadata("LUCID", "LUCID CA", "123", "2026-01-01", "2027-01-01")
        signature = SignatureMetadata("sig://engineering-pack", certificate=certificate)
        review = ReviewRecord("engineering-pack")
        updates = MarketplaceUpdates()
        metrics = MarketplaceMetrics()
        publisher = PublisherProfile.from_dict(
            {
                "publisher_id": "lucid",
                "organization": "LUCID",
                "trust_level": "official",
                "verification_status": "verified",
                "signing_status": "signed",
            }
        )

        review.transition(ReviewState.SUBMITTED)
        review.transition(ReviewState.VERIFIED)
        review.transition(ReviewState.APPROVED)
        metrics.set_package_count(1)
        metrics.record_install()
        metrics.record_review()
        metrics.record_channel("stable")

        self.assertEqual(security.publisher_trust, TrustDecision.TRUSTED)
        self.assertTrue(security.sandbox_required)
        self.assertTrue(MarketplaceSigning().verify_metadata(signature))
        self.assertEqual(review.state, ReviewState.APPROVED)
        self.assertTrue(ChannelPolicy.default(MarketplaceChannel.STABLE).requires_verified_publisher)
        self.assertTrue(ChannelPolicy.default(MarketplaceChannel.BETA).allows_prerelease)
        self.assertTrue(updates.evaluate("engineering-pack", "1.0.0", "1.1.0").actionable)
        self.assertEqual(publisher.trust_level, PublisherTrustLevel.OFFICIAL)
        self.assertEqual(publisher.verification_status, VerificationStatus.VERIFIED)
        self.assertEqual(publisher.signing_status, SigningStatus.SIGNED)
        self.assertEqual(metrics.snapshot()["install_count"], 1)


if __name__ == "__main__":
    unittest.main()
