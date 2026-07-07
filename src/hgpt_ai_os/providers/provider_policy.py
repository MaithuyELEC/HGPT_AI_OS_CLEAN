"""Provider selection policy for free, paid, offline, enterprise, and privacy modes."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from hgpt_ai_os.contracts.provider_contract import ProviderCapability


class ProviderPolicyMode(str, Enum):
    FREE = "free"
    PAID = "paid"
    OFFLINE = "offline"
    ENTERPRISE = "enterprise"
    PRIVACY = "privacy"


@dataclass(frozen=True)
class ProviderSelectionPolicy:
    mode: ProviderPolicyMode = ProviderPolicyMode.FREE
    required_capability: ProviderCapability = ProviderCapability.TEXT_GENERATION
    preferred_model: str | None = None
    free_first: bool = True
    offline_preference: bool = False
    latency_preference: bool = False
    cost_preference: bool = False
    allowed_providers: tuple[str, ...] = ()
    disabled_providers: tuple[str, ...] = ()
    enterprise_providers: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def allows_provider(self, provider_id: str) -> bool:
        if provider_id in self.disabled_providers:
            return False
        if self.allowed_providers and provider_id not in self.allowed_providers:
            return False
        if self.mode is ProviderPolicyMode.ENTERPRISE and self.enterprise_providers:
            return provider_id in self.enterprise_providers
        return True

    @classmethod
    def free(cls, **kwargs: Any) -> "ProviderSelectionPolicy":
        return cls(mode=ProviderPolicyMode.FREE, free_first=True, cost_preference=True, **kwargs)

    @classmethod
    def paid(cls, **kwargs: Any) -> "ProviderSelectionPolicy":
        return cls(mode=ProviderPolicyMode.PAID, free_first=False, **kwargs)

    @classmethod
    def offline(cls, **kwargs: Any) -> "ProviderSelectionPolicy":
        return cls(mode=ProviderPolicyMode.OFFLINE, offline_preference=True, **kwargs)

    @classmethod
    def enterprise(cls, **kwargs: Any) -> "ProviderSelectionPolicy":
        return cls(mode=ProviderPolicyMode.ENTERPRISE, **kwargs)

    @classmethod
    def privacy(cls, **kwargs: Any) -> "ProviderSelectionPolicy":
        return cls(mode=ProviderPolicyMode.PRIVACY, offline_preference=True, **kwargs)
