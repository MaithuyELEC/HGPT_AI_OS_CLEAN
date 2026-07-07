"""Base adapter for provider skeletons."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from hgpt_ai_os.contracts.provider_contract import (
    Provider,
    ProviderCapability,
    ProviderHealth,
    ProviderMetadata,
    ProviderRequest,
    ProviderResponse,
)
from hgpt_ai_os.providers.provider_health import ProviderHealthStatus, build_provider_health


class ProviderAdapterUnavailable(RuntimeError):
    """Raised when a skeleton adapter is asked to generate content."""


@dataclass(frozen=True)
class ProviderAdapterProfile:
    provider_id: str
    display_name: str
    default_model: str
    models: tuple[str, ...]
    capabilities: tuple[ProviderCapability, ...]
    cost_rank: int
    latency_rank: int
    offline: bool = False
    free: bool = False
    enterprise: bool = False
    privacy_preserving: bool = False
    version: str = "0.1.0"
    enabled: bool = False

    def metadata(self) -> ProviderMetadata:
        return ProviderMetadata(
            provider_id=self.provider_id,
            display_name=self.display_name,
            version=self.version,
            capabilities=self.capabilities,
            metadata={
                "default_model": self.default_model,
                "models": self.models,
                "cost_rank": self.cost_rank,
                "latency_rank": self.latency_rank,
                "offline": self.offline,
                "free": self.free,
                "enterprise": self.enterprise,
                "privacy_preserving": self.privacy_preserving,
                "enabled": self.enabled,
            },
        )


class BaseProviderAdapter(Provider):
    """Contract-only provider adapter with no transport implementation."""

    profile: ProviderAdapterProfile

    def __init__(self, config: Mapping[str, Any] | None = None) -> None:
        self.config = dict(config or {})

    @property
    def metadata(self) -> ProviderMetadata:
        return self.profile.metadata()

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        raise ProviderAdapterUnavailable(
            f"{self.metadata.provider_id} adapter is registered but has no API implementation"
        )

    def health(self) -> ProviderHealth:
        status = (
            ProviderHealthStatus.READY
            if self.profile.enabled
            else ProviderHealthStatus.DISABLED
        )
        return build_provider_health(
            self.metadata,
            status,
            metadata={"adapter": type(self).__name__},
        )

    def models(self) -> tuple[str, ...]:
        return self.profile.models

    def default_model(self) -> str:
        return self.profile.default_model
