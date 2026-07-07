"""Universal agent execution result model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class AgentResult:
    agent_id: str
    execution_id: str
    success: bool
    output: Mapping[str, Any] = field(default_factory=dict)
    errors: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def success_result(
        cls,
        agent_id: str,
        execution_id: str,
        output: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> "AgentResult":
        return cls(agent_id=agent_id, execution_id=execution_id, success=True, output=dict(output or {}), metadata=dict(metadata or {}))

    @classmethod
    def failure_result(
        cls,
        agent_id: str,
        execution_id: str,
        errors: tuple[str, ...],
        metadata: Mapping[str, Any] | None = None,
    ) -> "AgentResult":
        return cls(agent_id=agent_id, execution_id=execution_id, success=False, errors=errors, metadata=dict(metadata or {}))
