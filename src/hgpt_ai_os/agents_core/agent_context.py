"""Universal agent context model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from .agent_memory_scope import AgentMemoryScope
from .agent_permissions import AgentPermission, AgentPermissionSet


@dataclass(frozen=True)
class AgentContext:
    agent_id: str
    execution_id: str
    session_id: str
    memory_scope: AgentMemoryScope = AgentMemoryScope.SESSION
    permissions: AgentPermissionSet = field(default_factory=AgentPermissionSet)
    inputs: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def allows(self, permission: AgentPermission) -> bool:
        return self.permissions.allows(permission)

    def with_inputs(self, inputs: Mapping[str, Any]) -> "AgentContext":
        return AgentContext(
            agent_id=self.agent_id,
            execution_id=self.execution_id,
            session_id=self.session_id,
            memory_scope=self.memory_scope,
            permissions=self.permissions,
            inputs=dict(inputs),
            metadata=self.metadata,
        )
