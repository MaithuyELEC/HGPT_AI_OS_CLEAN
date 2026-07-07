"""Provider layer result values."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from hgpt_ai_os.contracts.provider_contract import ProviderError, ProviderMetadata, ProviderResponse


@dataclass(frozen=True)
class ProviderSelectionResult:
    provider_id: str
    model: str | None
    metadata: ProviderMetadata
    fallback_chain: tuple[str, ...] = ()
    policy_metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderExecutionResult:
    provider_id: str
    response: ProviderResponse | None = None
    error: ProviderError | None = None
    attempts: int = 1

    @property
    def ok(self) -> bool:
        return self.response is not None and self.error is None
