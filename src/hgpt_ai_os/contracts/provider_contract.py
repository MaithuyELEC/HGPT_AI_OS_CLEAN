"""Provider boundary contracts without vendor implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncIterator, Mapping, Protocol, runtime_checkable

from .diagnostics_contract import ContractError, HealthReport, PlatformErrorCode

CONTRACT_VERSION = "2.0.0"
CONTRACT_LIFECYCLE = ("registered", "configured", "available", "degraded", "unavailable", "retired")
EXTENSION_RULES = (
    "Provider-specific options must live in metadata or policy mappings.",
    "Streaming chunks must preserve ProviderResponse compatibility.",
    "Structured outputs must declare a schema name or schema URI.",
)
BACKWARD_COMPATIBILITY_NOTES = (
    "No provider implementation is implied by this contract.",
    "Future provider adapters must map vendor failures into ProviderError and PlatformErrorCode.",
)


class ProviderCapability(str, Enum):
    TEXT_GENERATION = "text_generation"
    STREAMING = "streaming"
    STRUCTURED_OUTPUT = "structured_output"
    EMBEDDINGS = "embeddings"
    TOOL_CALLING = "tool_calling"


@dataclass(frozen=True)
class ProviderPolicy:
    allow_network: bool = True
    max_tokens: int | None = None
    timeout_seconds: float | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        if self.max_tokens is not None and self.max_tokens < 1:
            return (_validation_error("ProviderPolicy.max_tokens must be positive"),)
        if self.timeout_seconds is not None and self.timeout_seconds <= 0:
            return (_validation_error("ProviderPolicy.timeout_seconds must be positive"),)
        return ()


@dataclass(frozen=True)
class ProviderMetadata:
    provider_id: str
    display_name: str
    version: str
    capabilities: tuple[ProviderCapability, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(
            ("ProviderMetadata.provider_id", self.provider_id),
            ("ProviderMetadata.display_name", self.display_name),
            ("ProviderMetadata.version", self.version),
        )


@dataclass(frozen=True)
class ProviderRequest:
    request_id: str
    prompt: str
    policy: ProviderPolicy = field(default_factory=ProviderPolicy)
    structured_schema: Mapping[str, Any] | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return (*_require_text(("ProviderRequest.request_id", self.request_id), ("ProviderRequest.prompt", self.prompt)), *self.policy.validate())


@dataclass(frozen=True)
class ProviderResponse:
    request_id: str
    text: str
    structured_output: Mapping[str, Any] | None = None
    finish_reason: str = "complete"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(("ProviderResponse.request_id", self.request_id), ("ProviderResponse.finish_reason", self.finish_reason))


@dataclass(frozen=True)
class ProviderHealth:
    metadata: ProviderMetadata
    report: HealthReport

    def validate(self) -> tuple[ContractError, ...]:
        return (*self.metadata.validate(), *self.report.validate())


@dataclass(frozen=True)
class ProviderError:
    error: ContractError
    provider_id: str
    request_id: str | None = None
    retryable: bool = False

    def validate(self) -> tuple[ContractError, ...]:
        return _require_text(("ProviderError.provider_id", self.provider_id))


@runtime_checkable
class StreamingProvider(Protocol):
    def stream(self, request: ProviderRequest) -> AsyncIterator[ProviderResponse]:
        """Return provider response chunks for a streaming request."""


@runtime_checkable
class StructuredOutputProvider(Protocol):
    def generate_structured(self, request: ProviderRequest) -> ProviderResponse:
        """Return a response that conforms to the request structured schema."""


class Provider(ABC):
    @property
    @abstractmethod
    def metadata(self) -> ProviderMetadata:
        """Return stable provider identity and capability metadata."""

    @abstractmethod
    def generate(self, request: ProviderRequest) -> ProviderResponse:
        """Generate a provider response for a validated request."""

    @abstractmethod
    def health(self) -> ProviderHealth:
        """Return provider health using the diagnostics contract."""


def _require_text(*fields: tuple[str, str]) -> tuple[ContractError, ...]:
    return tuple(_validation_error(f"{name} is required") for name, value in fields if not value.strip())


def _validation_error(message: str) -> ContractError:
    return ContractError(PlatformErrorCode.CONTRACT_VALIDATION_FAILED, message, source="provider_contract")
