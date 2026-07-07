"""Lifecycle manager for universal agents."""

from __future__ import annotations

from .agent_factory import AgentFactory
from .agent_health import AgentHealth, AgentHealthStatus
from .agent_registry import AgentMetadata, AgentRegistry


class AgentManager:
    def __init__(self, registry: AgentRegistry | None = None, factory: AgentFactory | None = None) -> None:
        self.registry = registry or AgentRegistry()
        self.factory = factory or AgentFactory()

    def load(self, metadata: AgentMetadata, agent: object | None = None) -> AgentMetadata:
        self.registry.register(metadata, agent)
        return metadata

    def initialize(self, agent_id: str) -> AgentHealth:
        record = self.registry.get(agent_id)
        if record.agent is None and agent_id in self.factory.available_agent_ids():
            record.agent = self.factory.create(agent_id)
        record.initialized = True
        record.status = AgentHealthStatus.READY
        return self.health(agent_id)

    def enable(self, agent_id: str) -> AgentHealth:
        record = self.registry.get(agent_id)
        record.status = AgentHealthStatus.READY
        return self.health(agent_id)

    def disable(self, agent_id: str) -> AgentHealth:
        record = self.registry.get(agent_id)
        record.status = AgentHealthStatus.DISABLED
        return self.health(agent_id)

    def health(self, agent_id: str) -> AgentHealth:
        record = self.registry.get(agent_id)
        return AgentHealth(agent_id=agent_id, status=record.status, metadata={"initialized": record.initialized})

    def shutdown(self, agent_id: str | None = None) -> tuple[AgentHealth, ...]:
        agent_ids = (agent_id,) if agent_id else self.registry.agent_ids()
        reports: list[AgentHealth] = []
        for current_id in agent_ids:
            record = self.registry.get(current_id)
            record.status = AgentHealthStatus.OFFLINE
            reports.append(self.health(current_id))
        return tuple(reports)
