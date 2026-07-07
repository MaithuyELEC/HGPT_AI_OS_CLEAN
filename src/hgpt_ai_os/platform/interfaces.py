from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol, TypeVar, runtime_checkable


@runtime_checkable
class Lifecycle(Protocol):
    """Minimal lifecycle contract for platform components."""

    def start(self) -> None:
        """Start the component."""

    def stop(self) -> None:
        """Stop the component."""


@runtime_checkable
class Component(Protocol):
    """Base contract shared by providers, agents, plugins, and services."""

    @property
    def name(self) -> str:
        """Stable component name used for registration and diagnostics."""


@dataclass(frozen=True)
class RuntimeContext:
    """Immutable context passed to platform components."""

    app_name: str
    environment: str
    workspace: Path
    version: str
    metadata: Mapping[str, Any]


T = TypeVar("T")


class ServiceRegistry(Protocol):
    """Typed service lookup boundary for platform subsystems."""

    def register(self, key: str, service: Any) -> None:
        """Register a service by stable key."""

    def get(self, key: str, expected_type: type[T] | None = None) -> T | Any:
        """Return a service, optionally validating its type."""

    def contains(self, key: str) -> bool:
        """Return whether a service key is registered."""
