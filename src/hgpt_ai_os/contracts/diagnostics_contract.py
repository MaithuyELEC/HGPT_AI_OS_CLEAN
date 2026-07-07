"""Diagnostics and unified platform error contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, runtime_checkable

CONTRACT_VERSION = "2.0.0"
CONTRACT_LIFECYCLE = ("drafted", "approved", "versioned", "deprecated", "retired")
EXTENSION_RULES = (
    "Additive fields must provide defaults.",
    "Required method names and return shapes are stable for this major version.",
    "Implementations may add vendor-specific metadata only under metadata mappings.",
)
BACKWARD_COMPATIBILITY_NOTES = (
    "Version 2.x contracts are additive to the existing LUCID AUTO compatibility line.",
    "Consumers must ignore unknown metadata keys and preserve known error codes.",
)


class ErrorSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    RECOVERABLE = "recoverable"
    FATAL = "fatal"


class PlatformErrorCode(str, Enum):
    CONTRACT_VALIDATION_FAILED = "contract.validation_failed"
    LIFECYCLE_INVALID_STATE = "lifecycle.invalid_state"
    PERMISSION_DENIED = "permission.denied"
    CANCELLATION_REQUESTED = "execution.cancelled"
    TIMEOUT = "execution.timeout"
    RETRY_EXHAUSTED = "execution.retry_exhausted"
    PROVIDER_UNAVAILABLE = "provider.unavailable"
    PROVIDER_POLICY_VIOLATION = "provider.policy_violation"
    STRUCTURED_OUTPUT_INVALID = "provider.structured_output_invalid"
    STREAM_INTERRUPTED = "provider.stream_interrupted"
    KNOWLEDGE_UNAVAILABLE = "knowledge.unavailable"
    PLUGIN_SANDBOX_VIOLATION = "plugin.sandbox_violation"
    WORKFLOW_INVALID = "workflow.invalid"
    MEMORY_SCOPE_VIOLATION = "memory.scope_violation"
    DIAGNOSTIC_FAILED = "diagnostic.failed"
    UNKNOWN = "platform.unknown"


@dataclass(frozen=True)
class ContractError:
    code: PlatformErrorCode
    message: str
    severity: ErrorSeverity = ErrorSeverity.RECOVERABLE
    source: str = "contract"
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DiagnosticEvent:
    event_id: str
    component: str
    message: str
    severity: ErrorSeverity = ErrorSeverity.INFO
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        errors: list[ContractError] = []
        if not self.event_id.strip():
            errors.append(_validation_error("DiagnosticEvent.event_id is required"))
        if not self.component.strip():
            errors.append(_validation_error("DiagnosticEvent.component is required"))
        return tuple(errors)


@dataclass(frozen=True)
class DiagnosticResult:
    diagnostic_id: str
    passed: bool
    events: tuple[DiagnosticEvent, ...] = ()
    errors: tuple[ContractError, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        nested = [error for event in self.events for error in event.validate()]
        if not self.diagnostic_id.strip():
            return (_validation_error("DiagnosticResult.diagnostic_id is required"), *nested)
        return tuple(nested)


@dataclass(frozen=True)
class HealthReport:
    component: str
    status: str
    version: str = CONTRACT_VERSION
    diagnostics: tuple[DiagnosticResult, ...] = ()
    errors: tuple[ContractError, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        errors = [error for diagnostic in self.diagnostics for error in diagnostic.validate()]
        if not self.component.strip():
            errors.append(_validation_error("HealthReport.component is required"))
        if not self.status.strip():
            errors.append(_validation_error("HealthReport.status is required"))
        if self.version != CONTRACT_VERSION:
            errors.append(_validation_error("HealthReport.version must match contract version"))
        return tuple(errors)


@runtime_checkable
class DiagnosticReporter(Protocol):
    def emit(self, event: DiagnosticEvent) -> None:
        """Publish a diagnostic event to the host diagnostics channel."""


class DiagnosticContract(ABC):
    @property
    @abstractmethod
    def contract_version(self) -> str:
        """Return the diagnostics contract version supported by this component."""

    @abstractmethod
    def run_diagnostics(self) -> DiagnosticResult:
        """Return a diagnostics result using the unified error taxonomy."""


def _validation_error(message: str) -> ContractError:
    return ContractError(
        code=PlatformErrorCode.CONTRACT_VALIDATION_FAILED,
        message=message,
        severity=ErrorSeverity.WARNING,
        source="diagnostics_contract",
    )
