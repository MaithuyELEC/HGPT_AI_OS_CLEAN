"""LUCID PLATFORM foundation APIs.

Sprint 01 is intentionally additive. Existing LUCID AUTO modules continue to
run while new platform code starts from this stable runtime boundary.
"""

from .interfaces import Component, Lifecycle, RuntimeContext, ServiceRegistry
from .runtime import PlatformRuntime, RuntimeSettings

__all__ = [
    "Component",
    "Lifecycle",
    "PlatformRuntime",
    "RuntimeContext",
    "RuntimeSettings",
    "ServiceRegistry",
]
