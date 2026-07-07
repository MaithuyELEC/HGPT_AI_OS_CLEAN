"""Built-in domain catalog for the Universal Knowledge Engine."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class KnowledgeDomain(str, Enum):
    ENGINEERING = "Engineering"
    STEEL = "Steel"
    MECHANICAL = "Mechanical"
    ELECTRICAL = "Electrical"
    MAINTENANCE = "Maintenance"
    QAQC = "QAQC"
    LEAN = "Lean"
    FIVE_S = "5S"
    OFFICE = "Office"
    MARKETING = "Marketing"
    FINANCE = "Finance"
    EDUCATION = "Education"
    HEALTH = "Health"
    LEGAL = "Legal"
    PROGRAMMING = "Programming"
    TRAVEL = "Travel"
    COOKING = "Cooking"
    FAMILY = "Family"
    BUSINESS = "Business"
    DIGITAL_FACTORY = "DigitalFactory"
    GENERAL = "General"


@dataclass(frozen=True)
class KnowledgeCatalog:
    domains: tuple[KnowledgeDomain, ...] = tuple(KnowledgeDomain)

    def contains(self, domain: KnowledgeDomain | str) -> bool:
        return self.normalize(domain) in self.domains

    def normalize(self, domain: KnowledgeDomain | str) -> KnowledgeDomain:
        if isinstance(domain, KnowledgeDomain):
            return domain
        for candidate in KnowledgeDomain:
            if candidate.value.lower() == domain.strip().lower():
                return candidate
        raise ValueError(f"unknown knowledge domain: {domain}")

    def names(self) -> tuple[str, ...]:
        return tuple(domain.value for domain in self.domains)
