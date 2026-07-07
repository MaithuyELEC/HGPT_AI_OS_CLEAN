"""Provider registration, discovery, and metadata lookup."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from hgpt_ai_os.contracts.provider_contract import Provider, ProviderCapability, ProviderMetadata


@dataclass(frozen=True)
class ProviderRegistration:
    provider_id: str
    provider: Provider

    @property
    def metadata(self) -> ProviderMetadata:
        return self.provider.metadata


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, Provider] = {}

    def register(self, provider: Provider) -> None:
        metadata = provider.metadata
        errors = metadata.validate()
        if errors:
            raise ValueError(errors[0].message)
        provider_id = metadata.provider_id
        if provider_id in self._providers:
            raise KeyError(f"provider already registered: {provider_id}")
        self._providers[provider_id] = provider

    def unregister(self, provider_id: str) -> Provider:
        if provider_id not in self._providers:
            raise KeyError(f"provider not registered: {provider_id}")
        return self._providers.pop(provider_id)

    def get(self, provider_id: str) -> Provider:
        if provider_id not in self._providers:
            raise KeyError(f"provider not registered: {provider_id}")
        return self._providers[provider_id]

    def contains(self, provider_id: str) -> bool:
        return provider_id in self._providers

    def provider_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._providers))

    def registrations(self) -> tuple[ProviderRegistration, ...]:
        return tuple(
            ProviderRegistration(provider_id, self._providers[provider_id])
            for provider_id in self.provider_ids()
        )

    def metadata(self, provider_id: str | None = None) -> ProviderMetadata | tuple[ProviderMetadata, ...]:
        if provider_id is not None:
            return self.get(provider_id).metadata
        return tuple(registration.metadata for registration in self.registrations())

    def discover(
        self,
        capability: ProviderCapability | None = None,
        *,
        include_disabled: bool = True,
    ) -> tuple[ProviderMetadata, ...]:
        candidates: Iterable[ProviderRegistration] = self.registrations()
        discovered: list[ProviderMetadata] = []
        for registration in candidates:
            metadata = registration.metadata
            if capability is not None and capability not in metadata.capabilities:
                continue
            if not include_disabled and not metadata.metadata.get("enabled", False):
                continue
            discovered.append(metadata)
        return tuple(discovered)
