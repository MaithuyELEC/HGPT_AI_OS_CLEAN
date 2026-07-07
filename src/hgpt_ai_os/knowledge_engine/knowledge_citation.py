"""Citation model for knowledge search results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class KnowledgeCitation:
    source_id: str
    package_id: str
    version: str
    reference: str
    confidence: float = 1.0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.source_id.strip():
            errors.append("source_id is required")
        if not self.package_id.strip():
            errors.append("package_id is required")
        if not self.version.strip():
            errors.append("version is required")
        if not self.reference.strip():
            errors.append("reference is required")
        if not 0.0 <= self.confidence <= 1.0:
            errors.append("confidence must be between 0 and 1")
        return tuple(errors)

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "package_id": self.package_id,
            "version": self.version,
            "reference": self.reference,
            "confidence": self.confidence,
            "metadata": dict(self.metadata),
        }
