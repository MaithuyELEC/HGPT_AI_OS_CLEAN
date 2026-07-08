"""Marketplace signing and verification metadata."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class VerificationModel(str, Enum):
    METADATA_ONLY = "metadata_only"
    CERTIFICATE_CHAIN = "certificate_chain"
    FUTURE_PKI = "future_pki"


class SignatureStatus(str, Enum):
    PRESENT = "present"
    MISSING = "missing"
    REVOKED = "revoked"


@dataclass(frozen=True)
class CertificateMetadata:
    subject: str
    issuer: str
    serial_number: str
    valid_from: str
    valid_until: str

    def validate(self) -> tuple[str, ...]:
        required = {
            "subject": self.subject,
            "issuer": self.issuer,
            "serial_number": self.serial_number,
            "valid_from": self.valid_from,
            "valid_until": self.valid_until,
        }
        return tuple(f"{name} is required" for name, value in required.items() if not value)


@dataclass(frozen=True)
class SignatureMetadata:
    signature_reference: str
    algorithm: str = "sha256-rsa"
    certificate: CertificateMetadata | None = None
    status: SignatureStatus = SignatureStatus.PRESENT

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.signature_reference:
            errors.append("signature_reference is required")
        if not self.algorithm:
            errors.append("signature algorithm is required")
        if self.certificate is not None:
            errors.extend(self.certificate.validate())
        return tuple(errors)

    def as_dict(self) -> Mapping[str, object]:
        certificate = None
        if self.certificate is not None:
            certificate = {
                "subject": self.certificate.subject,
                "issuer": self.certificate.issuer,
                "serial_number": self.certificate.serial_number,
                "valid_from": self.certificate.valid_from,
                "valid_until": self.certificate.valid_until,
            }
        return {
            "signature_reference": self.signature_reference,
            "algorithm": self.algorithm,
            "certificate": certificate,
            "status": self.status.value,
        }


class MarketplaceSigning:
    def verification_model(self) -> VerificationModel:
        return VerificationModel.FUTURE_PKI

    def verify_metadata(self, signature: SignatureMetadata) -> bool:
        return signature.status is SignatureStatus.PRESENT and not signature.validate()
