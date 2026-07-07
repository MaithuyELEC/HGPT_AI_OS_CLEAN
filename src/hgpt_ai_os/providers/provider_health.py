"""Provider health states and contract report helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from hgpt_ai_os.contracts.diagnostics_contract import (
    ContractError,
    ErrorSeverity,
    HealthReport,
    PlatformErrorCode,
)
from hgpt_ai_os.contracts.provider_contract import ProviderHealth, ProviderMetadata


class ProviderHealthStatus(str, Enum):
    READY = "ready"
    UNAVAILABLE = "unavailable"
    QUOTA_EXCEEDED = "quota_exceeded"
    OFFLINE = "offline"
    DISABLED = "disabled"


_STATUS_TO_ERROR = {
    ProviderHealthStatus.UNAVAILABLE: PlatformErrorCode.PROVIDER_UNAVAILABLE,
    ProviderHealthStatus.QUOTA_EXCEEDED: PlatformErrorCode.PROVIDER_UNAVAILABLE,
    ProviderHealthStatus.OFFLINE: PlatformErrorCode.PROVIDER_UNAVAILABLE,
    ProviderHealthStatus.DISABLED: PlatformErrorCode.PROVIDER_POLICY_VIOLATION,
}


@dataclass(frozen=True)
class ProviderHealthSnapshot:
    provider_id: str
    status: ProviderHealthStatus
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def available(self) -> bool:
        return self.status is ProviderHealthStatus.READY


def build_provider_health(
    provider_metadata: ProviderMetadata,
    status: ProviderHealthStatus,
    message: str = "",
    metadata: Mapping[str, Any] | None = None,
) -> ProviderHealth:
    errors: tuple[ContractError, ...] = ()
    if status is not ProviderHealthStatus.READY:
        errors = (
            ContractError(
                code=_STATUS_TO_ERROR[status],
                message=message or f"{provider_metadata.provider_id} is {status.value}",
                severity=ErrorSeverity.RECOVERABLE,
                source="provider_layer",
            ),
        )
    return ProviderHealth(
        metadata=provider_metadata,
        report=HealthReport(
            component=provider_metadata.provider_id,
            status=status.value,
            errors=errors,
            metadata=dict(metadata or {}),
        ),
    )
