"""Registry for universal agent definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from .agent_capability import AgentCapability
from .agent_health import AgentHealthStatus
from .agent_permissions import AgentPermission


@dataclass(frozen=True)
class AgentMetadata:
    agent_id: str
    display_name: str
    version: str
    capabilities: tuple[AgentCapability, ...] = ()
    permissions: tuple[AgentPermission, ...] = ()
    description: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def supports(self, capability: AgentCapability) -> bool:
        return capability in self.capabilities


@dataclass
class AgentRuntimeRecord:
    metadata: AgentMetadata
    agent: Any | None = None
    status: AgentHealthStatus = AgentHealthStatus.OFFLINE
    initialized: bool = False


class AgentRegistry:
    def __init__(self) -> None:
        self._records: dict[str, AgentRuntimeRecord] = {}

    def register(self, metadata: AgentMetadata, agent: Any | None = None) -> None:
        if metadata.agent_id in self._records:
            raise KeyError(f"Agent already registered: {metadata.agent_id}")
        self._records[metadata.agent_id] = AgentRuntimeRecord(metadata=metadata, agent=agent)

    def unregister(self, agent_id: str) -> AgentRuntimeRecord:
        try:
            return self._records.pop(agent_id)
        except KeyError as exc:
            raise KeyError(f"Agent is not registered: {agent_id}") from exc

    def contains(self, agent_id: str) -> bool:
        return agent_id in self._records

    def get(self, agent_id: str) -> AgentRuntimeRecord:
        try:
            return self._records[agent_id]
        except KeyError as exc:
            raise KeyError(f"Agent is not registered: {agent_id}") from exc

    def metadata(self, agent_id: str) -> AgentMetadata:
        return self.get(agent_id).metadata

    def agent_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._records))

    def discover(self, capability: AgentCapability | None = None) -> tuple[AgentMetadata, ...]:
        records = tuple(self._records[agent_id].metadata for agent_id in self.agent_ids())
        if capability is None:
            return records
        return tuple(metadata for metadata in records if metadata.supports(capability))

    def version_metadata(self, agent_id: str) -> Mapping[str, str]:
        metadata = self.metadata(agent_id)
        return {"agent_id": metadata.agent_id, "version": metadata.version}

    def capability_metadata(self, agent_id: str) -> tuple[AgentCapability, ...]:
        return self.metadata(agent_id).capabilities
