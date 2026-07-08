"""Marketplace update state metadata."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class UpdateState(str, Enum):
    INSTALLED = "installed"
    AVAILABLE = "available"
    IGNORED = "ignored"
    PINNED = "pinned"
    ROLLBACK = "rollback"


@dataclass(frozen=True)
class UpdateRecord:
    package_id: str
    installed_version: str
    available_version: str
    state: UpdateState
    migration_metadata: dict[str, object] | None = None

    @property
    def actionable(self) -> bool:
        return self.state in {UpdateState.AVAILABLE, UpdateState.ROLLBACK}


class MarketplaceUpdates:
    def evaluate(self, package_id: str, installed_version: str, available_version: str) -> UpdateRecord:
        state = UpdateState.INSTALLED if installed_version == available_version else UpdateState.AVAILABLE
        return UpdateRecord(
            package_id=package_id,
            installed_version=installed_version,
            available_version=available_version,
            state=state,
            migration_metadata={"from": installed_version, "to": available_version},
        )

    def pinned(self, package_id: str, version: str) -> UpdateRecord:
        return UpdateRecord(package_id, version, version, UpdateState.PINNED, {"reason": "version pinned"})

    def ignored(self, package_id: str, installed_version: str, available_version: str) -> UpdateRecord:
        return UpdateRecord(package_id, installed_version, available_version, UpdateState.IGNORED, {"reason": "ignored"})

    def rollback(self, package_id: str, installed_version: str, rollback_version: str) -> UpdateRecord:
        return UpdateRecord(
            package_id, installed_version, rollback_version, UpdateState.ROLLBACK, {"rollback_to": rollback_version}
        )
