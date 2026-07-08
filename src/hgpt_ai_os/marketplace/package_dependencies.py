"""Marketplace package dependency metadata."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Mapping

from .package_compatibility import SemanticVersion


class DependencyKind(str, Enum):
    REQUIRED = "required"
    OPTIONAL = "optional"
    CONFLICTS = "conflicts"
    REPLACES = "replaces"


@dataclass(frozen=True)
class PackageDependency:
    package_id: str
    min_version: str = "1.0.0"
    kind: DependencyKind = DependencyKind.REQUIRED

    @classmethod
    def from_value(cls, value: str | Mapping[str, Any], default_kind: DependencyKind) -> "PackageDependency":
        if isinstance(value, str):
            return cls(package_id=value.strip(), kind=default_kind)
        kind_value = str(value.get("kind", default_kind.value)).strip().lower()
        return cls(
            package_id=str(value.get("package_id", "")).strip(),
            min_version=str(value.get("min_version", "1.0.0")).strip(),
            kind=DependencyKind(kind_value),
        )

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        if not self.package_id:
            errors.append("dependency package_id is required")
        try:
            SemanticVersion.parse(self.min_version)
        except ValueError:
            errors.append("dependency min_version must be semantic version")
        return tuple(errors)

    def as_dict(self) -> Mapping[str, object]:
        return {"package_id": self.package_id, "min_version": self.min_version, "kind": self.kind.value}


@dataclass(frozen=True)
class DependencySet:
    required: tuple[PackageDependency, ...] = ()
    optional: tuple[PackageDependency, ...] = ()
    conflicts: tuple[PackageDependency, ...] = ()
    replaces: tuple[PackageDependency, ...] = ()

    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | None) -> "DependencySet":
        values = data or {}
        return cls(
            required=tuple(
                PackageDependency.from_value(value, DependencyKind.REQUIRED) for value in values.get("required", ())
            ),
            optional=tuple(
                PackageDependency.from_value(value, DependencyKind.OPTIONAL) for value in values.get("optional", ())
            ),
            conflicts=tuple(
                PackageDependency.from_value(value, DependencyKind.CONFLICTS) for value in values.get("conflicts", ())
            ),
            replaces=tuple(
                PackageDependency.from_value(value, DependencyKind.REPLACES) for value in values.get("replaces", ())
            ),
        )

    def all(self) -> tuple[PackageDependency, ...]:
        return self.required + self.optional + self.conflicts + self.replaces

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        for dependency in self.all():
            errors.extend(dependency.validate())
        return tuple(errors)

    def missing_required(self, installed_package_ids: Iterable[str]) -> tuple[str, ...]:
        installed = set(installed_package_ids)
        return tuple(dependency.package_id for dependency in self.required if dependency.package_id not in installed)

    def conflict_hits(self, installed_package_ids: Iterable[str]) -> tuple[str, ...]:
        installed = set(installed_package_ids)
        return tuple(dependency.package_id for dependency in self.conflicts if dependency.package_id in installed)

    def as_dict(self) -> Mapping[str, object]:
        return {
            "required": tuple(dependency.as_dict() for dependency in self.required),
            "optional": tuple(dependency.as_dict() for dependency in self.optional),
            "conflicts": tuple(dependency.as_dict() for dependency in self.conflicts),
            "replaces": tuple(dependency.as_dict() for dependency in self.replaces),
        }
