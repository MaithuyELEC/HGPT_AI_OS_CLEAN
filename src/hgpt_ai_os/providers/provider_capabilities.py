"""Provider capability metadata used by registry and selector."""

from __future__ import annotations

from dataclasses import dataclass

from hgpt_ai_os.contracts.provider_contract import ProviderCapability


@dataclass(frozen=True)
class ProviderCapabilitySet:
    capabilities: tuple[ProviderCapability, ...] = ()
    models: tuple[str, ...] = ()
    default_model: str | None = None

    def supports(self, capability: ProviderCapability) -> bool:
        return capability in self.capabilities

    def choose_model(self, preferred_model: str | None = None) -> str | None:
        if preferred_model and preferred_model in self.models:
            return preferred_model
        if self.default_model:
            return self.default_model
        if self.models:
            return self.models[0]
        return None
