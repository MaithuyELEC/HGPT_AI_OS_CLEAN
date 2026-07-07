"""Universal Agent System APIs for LUCID PLATFORM."""

from .agent_capability import AgentCapability, AgentCapabilityMetadata
from .agent_context import AgentContext
from .agent_executor import AgentExecutor
from .agent_factory import AgentFactory
from .agent_health import AgentHealth, AgentHealthStatus
from .agent_manager import AgentManager
from .agent_memory_scope import AgentMemoryScope
from .agent_permissions import AgentPermission, AgentPermissionSet
from .agent_registry import AgentMetadata, AgentRegistry, AgentRuntimeRecord
from .agent_result import AgentResult
from .builtins import (
    BUILT_IN_AGENT_METADATA,
    DailyLifeAgent,
    DigitalFactoryAgent,
    EducationAgent,
    EngineeringAgent,
    FinanceAgent,
    HealthAgent,
    LegalAgent,
    MarketingAgent,
    OfficeAgent,
    ProgrammingAgent,
    SteelEngineeringAgent,
    TravelAgent,
    CookingAgent,
    register_builtin_agent_constructors,
    register_builtin_agents,
)

__all__ = [
    "AgentCapability",
    "AgentCapabilityMetadata",
    "AgentContext",
    "AgentExecutor",
    "AgentFactory",
    "AgentHealth",
    "AgentHealthStatus",
    "AgentManager",
    "AgentMemoryScope",
    "AgentMetadata",
    "AgentPermission",
    "AgentPermissionSet",
    "AgentRegistry",
    "AgentResult",
    "AgentRuntimeRecord",
    "BUILT_IN_AGENT_METADATA",
    "CookingAgent",
    "DailyLifeAgent",
    "DigitalFactoryAgent",
    "EducationAgent",
    "EngineeringAgent",
    "FinanceAgent",
    "HealthAgent",
    "LegalAgent",
    "MarketingAgent",
    "OfficeAgent",
    "ProgrammingAgent",
    "SteelEngineeringAgent",
    "TravelAgent",
    "register_builtin_agent_constructors",
    "register_builtin_agents",
]
