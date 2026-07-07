"""Provider request envelope layered on top of the Sprint 02 contract."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from hgpt_ai_os.contracts.provider_contract import ProviderRequest
from hgpt_ai_os.providers.provider_policy import ProviderSelectionPolicy


@dataclass(frozen=True)
class ProviderRequestEnvelope:
    request: ProviderRequest
    selection_policy: ProviderSelectionPolicy = field(default_factory=ProviderSelectionPolicy)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self):
        return self.request.validate()
