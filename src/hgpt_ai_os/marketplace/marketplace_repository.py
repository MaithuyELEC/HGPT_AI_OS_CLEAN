"""Marketplace repository metadata model."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RepositoryType(str, Enum):
    OFFICIAL = "official"
    COMMUNITY = "community"
    ENTERPRISE = "enterprise"
    PRIVATE = "private"
    LOCAL = "local"
    OFFLINE = "offline"


@dataclass(frozen=True)
class MarketplaceRepository:
    repository_id: str
    repository_type: RepositoryType
    name: str
    enabled: bool = True
    priority: int = 100

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.repository_id:
            errors.append("repository_id is required")
        if not self.name:
            errors.append("repository name is required")
        return tuple(errors)


class RepositoryRegistry:
    def __init__(self) -> None:
        self._repositories: dict[str, MarketplaceRepository] = {}

    def register(self, repository: MarketplaceRepository) -> MarketplaceRepository:
        errors = repository.validate()
        if errors:
            raise ValueError(errors[0])
        if repository.repository_id in self._repositories:
            raise KeyError(f"repository already registered: {repository.repository_id}")
        self._repositories[repository.repository_id] = repository
        return repository

    def remove(self, repository_id: str) -> MarketplaceRepository:
        if repository_id not in self._repositories:
            raise KeyError(f"repository not registered: {repository_id}")
        return self._repositories.pop(repository_id)

    def list(self, *, enabled_only: bool = False) -> tuple[MarketplaceRepository, ...]:
        repositories = sorted(self._repositories.values(), key=lambda value: (value.priority, value.repository_id))
        if enabled_only:
            repositories = [repository for repository in repositories if repository.enabled]
        return tuple(repositories)
