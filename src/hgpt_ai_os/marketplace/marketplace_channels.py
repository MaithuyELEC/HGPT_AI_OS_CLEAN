"""Marketplace release channel metadata."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MarketplaceChannel(str, Enum):
    STABLE = "stable"
    LTS = "lts"
    PREVIEW = "preview"
    BETA = "beta"
    ENTERPRISE = "enterprise"
    EXPERIMENTAL = "experimental"


@dataclass(frozen=True)
class ChannelPolicy:
    channel: MarketplaceChannel
    requires_verified_publisher: bool = False
    allows_prerelease: bool = False
    enterprise_only: bool = False

    @classmethod
    def default(cls, channel: MarketplaceChannel | str) -> "ChannelPolicy":
        value = MarketplaceChannel(channel) if isinstance(channel, str) else channel
        return cls(
            channel=value,
            requires_verified_publisher=value in {MarketplaceChannel.STABLE, MarketplaceChannel.LTS, MarketplaceChannel.ENTERPRISE},
            allows_prerelease=value in {MarketplaceChannel.PREVIEW, MarketplaceChannel.BETA, MarketplaceChannel.EXPERIMENTAL},
            enterprise_only=value is MarketplaceChannel.ENTERPRISE,
        )
