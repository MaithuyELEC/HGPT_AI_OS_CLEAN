"""Universal agent execution orchestration."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .agent_context import AgentContext
from .agent_health import AgentHealthStatus
from .agent_registry import AgentRegistry
from .agent_result import AgentResult


class AgentExecutor:
    def __init__(self, registry: AgentRegistry) -> None:
        self.registry = registry

    def execute(
        self,
        agent_id: str,
        context: AgentContext,
        handler: Callable[[AgentContext], AgentResult] | None = None,
    ) -> AgentResult:
        record = self.registry.get(agent_id)
        if record.status is AgentHealthStatus.DISABLED:
            return AgentResult.failure_result(agent_id, context.execution_id, ("agent disabled",))
        if record.status is AgentHealthStatus.FAILED:
            return AgentResult.failure_result(agent_id, context.execution_id, ("agent failed",))
        if record.status is AgentHealthStatus.OFFLINE:
            return AgentResult.failure_result(agent_id, context.execution_id, ("agent offline",))
        if not context.permissions.require(record.metadata.permissions):
            return AgentResult.failure_result(agent_id, context.execution_id, ("permission denied",))

        record.status = AgentHealthStatus.BUSY
        try:
            executable = handler or getattr(record.agent, "execute", None)
            if executable is None:
                return AgentResult.success_result(
                    agent_id,
                    context.execution_id,
                    metadata={"executed": False, "reason": "metadata skeleton"},
                )
            result = executable(context)
            if not isinstance(result, AgentResult):
                return AgentResult.success_result(agent_id, context.execution_id, output=_as_mapping(result))
            return result
        except Exception as exc:
            record.status = AgentHealthStatus.FAILED
            return AgentResult.failure_result(agent_id, context.execution_id, (str(exc),))
        finally:
            if record.status is AgentHealthStatus.BUSY:
                record.status = AgentHealthStatus.READY


def _as_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {"value": value}
