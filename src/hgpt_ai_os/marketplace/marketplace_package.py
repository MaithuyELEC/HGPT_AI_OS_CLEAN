"""Marketplace package aggregate metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .marketplace_manifest import MarketplaceManifest


@dataclass(frozen=True)
class MarketplacePackage:
    manifest: MarketplaceManifest
    repository_id: str = "local"
    review_state: str = "draft"
    channel: str = "stable"

    @property
    def package_id(self) -> str:
        return self.manifest.package_id

    def as_dict(self) -> Mapping[str, object]:
        return {
            "manifest": self.manifest.as_dict(),
            "repository_id": self.repository_id,
            "review_state": self.review_state,
            "channel": self.channel,
        }
