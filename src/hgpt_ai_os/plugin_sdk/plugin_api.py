"""Stable extension interface contracts for plugins."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .plugin_context import PluginContext
from .plugin_manifest import PluginManifest


class PluginAPI(ABC):
    @property
    @abstractmethod
    def manifest(self) -> PluginManifest:
        """Return static plugin metadata."""

    @abstractmethod
    def configure(self, context: PluginContext) -> None:
        """Receive host context before enablement."""

    @abstractmethod
    def health(self) -> dict[str, object]:
        """Return a host-readable health payload."""
