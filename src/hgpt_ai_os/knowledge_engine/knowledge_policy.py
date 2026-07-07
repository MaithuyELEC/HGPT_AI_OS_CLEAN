"""Visibility and access policy for knowledge packages."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class KnowledgeVisibility(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    ENTERPRISE = "enterprise"


@dataclass(frozen=True)
class KnowledgePolicy:
    visibility: KnowledgeVisibility = KnowledgeVisibility.PRIVATE
    read_only: bool = True
    experimental: bool = False

    def can_read(self, audience: KnowledgeVisibility) -> bool:
        if self.visibility is KnowledgeVisibility.PUBLIC:
            return True
        if self.visibility is KnowledgeVisibility.PRIVATE:
            return audience in (KnowledgeVisibility.PRIVATE, KnowledgeVisibility.ENTERPRISE)
        return audience is KnowledgeVisibility.ENTERPRISE

    def can_write(self) -> bool:
        return not self.read_only

    def flags(self) -> tuple[str, ...]:
        values: list[str] = [self.visibility.value]
        if self.read_only:
            values.append("read_only")
        if self.experimental:
            values.append("experimental")
        return tuple(values)
