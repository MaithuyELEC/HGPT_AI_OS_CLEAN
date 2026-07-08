"""Marketplace publisher profile metadata."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class PublisherTrustLevel(str, Enum):
    UNKNOWN = "unknown"
    COMMUNITY = "community"
    VERIFIED = "verified"
    OFFICIAL = "official"
    ENTERPRISE = "enterprise"


class VerificationStatus(str, Enum):
    UNVERIFIED = "unverified"
    SUBMITTED = "submitted"
    VERIFIED = "verified"
    REVOKED = "revoked"


class SigningStatus(str, Enum):
    UNSIGNED = "unsigned"
    SIGNED = "signed"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass(frozen=True)
class PublisherProfile:
    publisher_id: str
    organization: str = ""
    trust_level: PublisherTrustLevel = PublisherTrustLevel.UNKNOWN
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    signing_status: SigningStatus = SigningStatus.UNSIGNED

    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | None) -> "PublisherProfile":
        values = data or {}
        return cls(
            publisher_id=str(values.get("publisher_id", "")).strip(),
            organization=str(values.get("organization", "")).strip(),
            trust_level=PublisherTrustLevel(str(values.get("trust_level", "unknown")).strip().lower()),
            verification_status=VerificationStatus(str(values.get("verification_status", "unverified")).strip().lower()),
            signing_status=SigningStatus(str(values.get("signing_status", "unsigned")).strip().lower()),
        )

    def validate(self) -> tuple[str, ...]:
        if not self.publisher_id:
            return ("publisher_id is required",)
        return ()

    def as_dict(self) -> Mapping[str, object]:
        return {
            "publisher_id": self.publisher_id,
            "organization": self.organization,
            "trust_level": self.trust_level.value,
            "verification_status": self.verification_status.value,
            "signing_status": self.signing_status.value,
        }
