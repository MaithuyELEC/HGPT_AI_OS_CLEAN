"""Built-in universal agent metadata skeletons."""

from __future__ import annotations

from dataclasses import dataclass

from .agent_capability import AgentCapability
from .agent_factory import AgentFactory
from .agent_permissions import AgentPermission
from .agent_registry import AgentMetadata, AgentRegistry


@dataclass(frozen=True)
class BuiltInAgentSkeleton:
    metadata: AgentMetadata


class EngineeringAgent(BuiltInAgentSkeleton):
    METADATA = AgentMetadata(
        agent_id="engineering",
        display_name="Engineering Agent",
        version="1.0.0",
        capabilities=(AgentCapability.REASONING, AgentCapability.PLANNING, AgentCapability.KNOWLEDGE),
        permissions=(AgentPermission.KNOWLEDGE, AgentPermission.DIAGNOSTICS),
        description="Metadata skeleton for engineering workflows.",
    )


class OfficeAgent(BuiltInAgentSkeleton):
    METADATA = AgentMetadata(
        agent_id="office",
        display_name="Office Agent",
        version="1.0.0",
        capabilities=(AgentCapability.WRITING, AgentCapability.PLANNING, AgentCapability.AUTOMATION),
        permissions=(AgentPermission.FILESYSTEM, AgentPermission.WORKFLOW),
        description="Metadata skeleton for office productivity workflows.",
    )


class MarketingAgent(BuiltInAgentSkeleton):
    METADATA = AgentMetadata(
        agent_id="marketing",
        display_name="Marketing Agent",
        version="1.0.0",
        capabilities=(AgentCapability.WRITING, AgentCapability.KNOWLEDGE, AgentCapability.PLANNING),
        permissions=(AgentPermission.KNOWLEDGE, AgentPermission.WORKFLOW),
        description="Metadata skeleton for marketing workflows.",
    )


class EducationAgent(BuiltInAgentSkeleton):
    METADATA = AgentMetadata(
        agent_id="education",
        display_name="Education Agent",
        version="1.0.0",
        capabilities=(AgentCapability.WRITING, AgentCapability.KNOWLEDGE, AgentCapability.PLANNING),
        permissions=(AgentPermission.KNOWLEDGE,),
        description="Metadata skeleton for education workflows.",
    )


class FinanceAgent(BuiltInAgentSkeleton):
    METADATA = AgentMetadata(
        agent_id="finance",
        display_name="Finance Agent",
        version="1.0.0",
        capabilities=(AgentCapability.REASONING, AgentCapability.KNOWLEDGE, AgentCapability.PLANNING),
        permissions=(AgentPermission.KNOWLEDGE, AgentPermission.DIAGNOSTICS),
        description="Metadata skeleton for finance workflows.",
    )


class HealthAgent(BuiltInAgentSkeleton):
    METADATA = AgentMetadata(
        agent_id="health",
        display_name="Health Agent",
        version="1.0.0",
        capabilities=(AgentCapability.REASONING, AgentCapability.KNOWLEDGE, AgentCapability.WRITING),
        permissions=(AgentPermission.KNOWLEDGE, AgentPermission.DIAGNOSTICS),
        description="Metadata skeleton for health workflows.",
    )


class LegalAgent(BuiltInAgentSkeleton):
    METADATA = AgentMetadata(
        agent_id="legal",
        display_name="Legal Agent",
        version="1.0.0",
        capabilities=(AgentCapability.REASONING, AgentCapability.KNOWLEDGE, AgentCapability.WRITING),
        permissions=(AgentPermission.KNOWLEDGE, AgentPermission.DIAGNOSTICS),
        description="Metadata skeleton for legal workflows.",
    )


class ProgrammingAgent(BuiltInAgentSkeleton):
    METADATA = AgentMetadata(
        agent_id="programming",
        display_name="Programming Agent",
        version="1.0.0",
        capabilities=(AgentCapability.CODING, AgentCapability.REASONING, AgentCapability.AUTOMATION),
        permissions=(AgentPermission.FILESYSTEM, AgentPermission.WORKFLOW, AgentPermission.DIAGNOSTICS),
        description="Metadata skeleton for programming workflows.",
    )


class TravelAgent(BuiltInAgentSkeleton):
    METADATA = AgentMetadata(
        agent_id="travel",
        display_name="Travel Agent",
        version="1.0.0",
        capabilities=(AgentCapability.PLANNING, AgentCapability.KNOWLEDGE, AgentCapability.WRITING),
        permissions=(AgentPermission.KNOWLEDGE, AgentPermission.WORKFLOW),
        description="Metadata skeleton for travel workflows.",
    )


class CookingAgent(BuiltInAgentSkeleton):
    METADATA = AgentMetadata(
        agent_id="cooking",
        display_name="Cooking Agent",
        version="1.0.0",
        capabilities=(AgentCapability.PLANNING, AgentCapability.KNOWLEDGE, AgentCapability.WRITING),
        permissions=(AgentPermission.KNOWLEDGE,),
        description="Metadata skeleton for cooking workflows.",
    )


class DailyLifeAgent(BuiltInAgentSkeleton):
    METADATA = AgentMetadata(
        agent_id="daily_life",
        display_name="Daily Life Agent",
        version="1.0.0",
        capabilities=(AgentCapability.PLANNING, AgentCapability.AUTOMATION, AgentCapability.WRITING),
        permissions=(AgentPermission.WORKFLOW,),
        description="Metadata skeleton for daily life workflows.",
    )


class DigitalFactoryAgent(BuiltInAgentSkeleton):
    METADATA = AgentMetadata(
        agent_id="digital_factory",
        display_name="Digital Factory Agent",
        version="1.0.0",
        capabilities=(AgentCapability.AUTOMATION, AgentCapability.PLANNING, AgentCapability.KNOWLEDGE),
        permissions=(AgentPermission.WORKFLOW, AgentPermission.DIAGNOSTICS, AgentPermission.KNOWLEDGE),
        description="Metadata skeleton for digital factory workflows.",
    )


class SteelEngineeringAgent(BuiltInAgentSkeleton):
    METADATA = AgentMetadata(
        agent_id="steel_engineering",
        display_name="Steel Engineering Agent",
        version="1.0.0",
        capabilities=(AgentCapability.REASONING, AgentCapability.KNOWLEDGE, AgentCapability.PLANNING),
        permissions=(AgentPermission.KNOWLEDGE, AgentPermission.DIAGNOSTICS),
        description="Metadata skeleton for steel engineering workflows.",
    )


BUILT_IN_AGENT_CLASSES = (
    EngineeringAgent,
    OfficeAgent,
    MarketingAgent,
    EducationAgent,
    FinanceAgent,
    HealthAgent,
    LegalAgent,
    ProgrammingAgent,
    TravelAgent,
    CookingAgent,
    DailyLifeAgent,
    DigitalFactoryAgent,
    SteelEngineeringAgent,
)

BUILT_IN_AGENT_METADATA = tuple(agent_class.METADATA for agent_class in BUILT_IN_AGENT_CLASSES)


def register_builtin_agents(registry: AgentRegistry) -> AgentRegistry:
    for metadata in BUILT_IN_AGENT_METADATA:
        registry.register(metadata)
    return registry


def register_builtin_agent_constructors(factory: AgentFactory) -> AgentFactory:
    for agent_class in BUILT_IN_AGENT_CLASSES:
        factory.register(agent_class.METADATA.agent_id, lambda cls=agent_class: cls(cls.METADATA))
    return factory
