"""Universal agent capability model."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class AgentCapability(str, Enum):
    REASONING = "reasoning"
    WRITING = "writing"
    CODING = "coding"
    KNOWLEDGE = "knowledge"
    VISION = "vision"
    AUTOMATION = "automation"
    PLANNING = "planning"


@dataclass(frozen=True)
class AgentCapabilityMetadata:
    capabilities: tuple[AgentCapability, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def supports(self, capability: AgentCapability) -> bool:
        return capability in self.capabilities

    def names(self) -> tuple[str, ...]:
        return tuple(capability.value for capability in self.capabilities)
