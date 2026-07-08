"""Marketplace metadata metrics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


@dataclass
class MarketplaceMetrics:
    package_count: int = 0
    install_count: int = 0
    uninstall_count: int = 0
    validation_failure_count: int = 0
    review_count: int = 0
    channel_counts: dict[str, int] = field(default_factory=dict)

    def set_package_count(self, value: int) -> None:
        self.package_count = value

    def record_install(self) -> None:
        self.install_count += 1

    def record_uninstall(self) -> None:
        self.uninstall_count += 1

    def record_validation_failure(self) -> None:
        self.validation_failure_count += 1

    def record_review(self) -> None:
        self.review_count += 1

    def record_channel(self, channel: str) -> None:
        self.channel_counts[channel] = self.channel_counts.get(channel, 0) + 1

    def snapshot(self) -> Mapping[str, object]:
        return {
            "package_count": self.package_count,
            "install_count": self.install_count,
            "uninstall_count": self.uninstall_count,
            "validation_failure_count": self.validation_failure_count,
            "review_count": self.review_count,
            "channel_counts": dict(self.channel_counts),
        }
