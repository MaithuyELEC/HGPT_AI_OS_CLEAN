"""Factory for universal agent instances."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


class AgentFactory:
    def __init__(self) -> None:
        self._constructors: dict[str, Callable[[], Any]] = {}

    def register(self, agent_id: str, constructor: Callable[[], Any]) -> None:
        if agent_id in self._constructors:
            raise KeyError(f"Agent constructor already registered: {agent_id}")
        self._constructors[agent_id] = constructor

    def create(self, agent_id: str) -> Any:
        try:
            return self._constructors[agent_id]()
        except KeyError as exc:
            raise KeyError(f"Agent constructor is not registered: {agent_id}") from exc

    def available_agent_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._constructors))
