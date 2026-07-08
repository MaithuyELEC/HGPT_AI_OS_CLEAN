"""Marketplace security metadata and trust decisions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping

from .marketplace_manifest import MarketplaceManifest
from .publisher_profile import PublisherTrustLevel, SigningStatus, VerificationStatus


class TrustDecision(str, Enum):
    TRUSTED = "trusted"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class SecurityReview:
    publisher_trust: TrustDecision
    package_trust: TrustDecision
    permissions: tuple[str, ...]
    sandbox_required: bool
    audit_metadata: Mapping[str, object]

    @property
    def approved(self) -> bool:
        return self.publisher_trust is TrustDecision.TRUSTED and self.package_trust is TrustDecision.TRUSTED


class MarketplaceSecurity:
    def review(self, manifest: MarketplaceManifest) -> SecurityReview:
        publisher_trust = self.publisher_trust(manifest)
        package_trust = self.package_trust(manifest)
        permissions = tuple(str(value).strip().lower() for value in manifest.metadata.get("permissions", ()))
        sandbox_required = bool(permissions)
        return SecurityReview(
            publisher_trust=publisher_trust,
            package_trust=package_trust,
            permissions=permissions,
            sandbox_required=sandbox_required,
            audit_metadata={
                "package_id": manifest.package_id,
                "publisher_id": manifest.publisher.publisher_id,
                "checksum_present": bool(manifest.checksum),
                "signature_reference_present": bool(manifest.signature_reference),
            },
        )

    def publisher_trust(self, manifest: MarketplaceManifest) -> TrustDecision:
        profile = manifest.publisher
        if profile.trust_level in {PublisherTrustLevel.OFFICIAL, PublisherTrustLevel.ENTERPRISE}:
            return TrustDecision.TRUSTED
        if profile.verification_status is VerificationStatus.REVOKED:
            return TrustDecision.BLOCKED
        if profile.verification_status is VerificationStatus.VERIFIED:
            return TrustDecision.TRUSTED
        return TrustDecision.REVIEW_REQUIRED

    def package_trust(self, manifest: MarketplaceManifest) -> TrustDecision:
        if not manifest.checksum:
            return TrustDecision.BLOCKED
        if manifest.signature_reference and manifest.publisher.signing_status is SigningStatus.SIGNED:
            return TrustDecision.TRUSTED
        return TrustDecision.REVIEW_REQUIRED
