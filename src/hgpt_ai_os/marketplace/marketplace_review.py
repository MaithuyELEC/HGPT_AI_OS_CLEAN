"""Marketplace package review lifecycle."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ReviewState(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    VERIFIED = "verified"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


ALLOWED_TRANSITIONS: dict[ReviewState, set[ReviewState]] = {
    ReviewState.DRAFT: {ReviewState.SUBMITTED, ReviewState.ARCHIVED},
    ReviewState.SUBMITTED: {ReviewState.VERIFIED, ReviewState.REJECTED, ReviewState.ARCHIVED},
    ReviewState.VERIFIED: {ReviewState.APPROVED, ReviewState.REJECTED, ReviewState.ARCHIVED},
    ReviewState.APPROVED: {ReviewState.DEPRECATED, ReviewState.ARCHIVED},
    ReviewState.REJECTED: {ReviewState.DRAFT, ReviewState.ARCHIVED},
    ReviewState.DEPRECATED: {ReviewState.ARCHIVED},
    ReviewState.ARCHIVED: set(),
}


@dataclass
class ReviewRecord:
    package_id: str
    state: ReviewState = ReviewState.DRAFT
    history: list[ReviewState] = field(default_factory=lambda: [ReviewState.DRAFT])

    def transition(self, state: ReviewState) -> ReviewState:
        if state not in ALLOWED_TRANSITIONS[self.state]:
            raise ValueError(f"invalid review transition: {self.state.value} -> {state.value}")
        self.state = state
        self.history.append(state)
        return self.state
