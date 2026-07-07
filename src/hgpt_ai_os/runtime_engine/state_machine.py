"""Formal state transition support for runtime orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar

StateT = TypeVar("StateT", bound=Enum)


class IllegalTransitionError(ValueError):
    """Raised when a runtime transition is not allowed."""


@dataclass
class StateMachine(Generic[StateT]):
    """Small deterministic state machine with explicit transition rules."""

    state: StateT
    transitions: dict[StateT, frozenset[StateT]]

    def can_transition(self, target: StateT) -> bool:
        return target in self.transitions.get(self.state, frozenset())

    def transition(self, target: StateT) -> StateT:
        if self.state == target:
            return self.state
        if not self.can_transition(target):
            raise IllegalTransitionError(f"illegal transition from {self.state.value} to {target.value}")
        self.state = target
        return self.state
