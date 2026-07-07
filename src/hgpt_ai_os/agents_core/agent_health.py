"""Universal agent health model."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class AgentHealthStatus(str, Enum):
    READY = "ready"
    BUSY = "busy"
    DISABLED = "disabled"
    FAILED = "failed"
    OFFLINE = "offline"


@dataclass(frozen=True)
class AgentHealth:
    agent_id: str
    status: AgentHealthStatus
    message: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def available(self) -> bool:
        return self.status is AgentHealthStatus.READY
