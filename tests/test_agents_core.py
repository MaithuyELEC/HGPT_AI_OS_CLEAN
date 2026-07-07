from __future__ import annotations

import unittest

from hgpt_ai_os.agents_core import (
    BUILT_IN_AGENT_METADATA,
    AgentCapability,
    AgentCapabilityMetadata,
    AgentContext,
    AgentExecutor,
    AgentFactory,
    AgentHealthStatus,
    AgentManager,
    AgentMemoryScope,
    AgentMetadata,
    AgentPermission,
    AgentPermissionSet,
    AgentRegistry,
    AgentResult,
    EngineeringAgent,
    register_builtin_agent_constructors,
    register_builtin_agents,
)


class AgentRegistryTests(unittest.TestCase):
    def test_register_unregister_discover_and_metadata(self):
        registry = AgentRegistry()
        metadata = AgentMetadata(
            agent_id="writer",
            display_name="Writer",
            version="1.2.0",
            capabilities=(AgentCapability.WRITING,),
            permissions=(AgentPermission.KNOWLEDGE,),
        )

        registry.register(metadata)

        self.assertTrue(registry.contains("writer"))
        self.assertEqual(registry.metadata("writer"), metadata)
        self.assertEqual(registry.agent_ids(), ("writer",))
        self.assertEqual(registry.version_metadata("writer")["version"], "1.2.0")
        self.assertEqual(registry.capability_metadata("writer"), (AgentCapability.WRITING,))
        self.assertEqual(registry.discover(AgentCapability.WRITING), (metadata,))
        self.assertEqual(registry.unregister("writer").metadata, metadata)
        self.assertFalse(registry.contains("writer"))

    def test_rejects_duplicate_agent_ids(self):
        registry = AgentRegistry()
        metadata = AgentMetadata("agent", "Agent", "1.0.0")
        registry.register(metadata)

        with self.assertRaises(KeyError):
            registry.register(metadata)


class AgentLifecycleTests(unittest.TestCase):
    def test_manager_load_initialize_enable_disable_health_and_shutdown(self):
        manager = AgentManager()
        metadata = AgentMetadata("agent", "Agent", "1.0.0")

        manager.load(metadata)

        self.assertEqual(manager.health("agent").status, AgentHealthStatus.OFFLINE)
        self.assertEqual(manager.initialize("agent").status, AgentHealthStatus.READY)
        self.assertTrue(manager.health("agent").metadata["initialized"])
        self.assertEqual(manager.disable("agent").status, AgentHealthStatus.DISABLED)
        self.assertEqual(manager.enable("agent").status, AgentHealthStatus.READY)
        self.assertEqual(manager.shutdown("agent")[0].status, AgentHealthStatus.OFFLINE)


class AgentFactoryTests(unittest.TestCase):
    def test_factory_instantiates_agents_only(self):
        factory = AgentFactory()
        factory.register("engineering", lambda: EngineeringAgent(EngineeringAgent.METADATA))

        agent = factory.create("engineering")

        self.assertIsInstance(agent, EngineeringAgent)
        self.assertEqual(agent.metadata.agent_id, "engineering")
        self.assertEqual(factory.available_agent_ids(), ("engineering",))

    def test_unknown_agent_is_rejected(self):
        with self.assertRaises(KeyError):
            AgentFactory().create("missing")


class AgentExecutorTests(unittest.TestCase):
    def test_executor_orchestrates_handler_without_provider_or_ai_logic(self):
        registry = AgentRegistry()
        metadata = AgentMetadata(
            "runner",
            "Runner",
            "1.0.0",
            permissions=(AgentPermission.WORKFLOW,),
        )
        registry.register(metadata)
        registry.get("runner").status = AgentHealthStatus.READY
        context = AgentContext(
            agent_id="runner",
            execution_id="exec-1",
            session_id="session-1",
            permissions=AgentPermissionSet((AgentPermission.WORKFLOW,)),
        )
        executor = AgentExecutor(registry)

        result = executor.execute(
            "runner",
            context,
            handler=lambda ctx: AgentResult.success_result(ctx.agent_id, ctx.execution_id, {"ok": True}),
        )

        self.assertTrue(result.success)
        self.assertEqual(result.output["ok"], True)
        self.assertEqual(registry.get("runner").status, AgentHealthStatus.READY)

    def test_executor_enforces_permissions_and_health(self):
        registry = AgentRegistry()
        registry.register(AgentMetadata("agent", "Agent", "1.0.0", permissions=(AgentPermission.FILESYSTEM,)))
        registry.get("agent").status = AgentHealthStatus.READY
        context = AgentContext(agent_id="agent", execution_id="exec-2", session_id="session-1")
        executor = AgentExecutor(registry)

        denied = executor.execute("agent", context)
        registry.get("agent").status = AgentHealthStatus.DISABLED
        disabled = executor.execute("agent", context)

        self.assertFalse(denied.success)
        self.assertEqual(denied.errors, ("permission denied",))
        self.assertFalse(disabled.success)
        self.assertEqual(disabled.errors, ("agent disabled",))


class AgentModelTests(unittest.TestCase):
    def test_permission_capability_health_and_memory_models(self):
        permissions = AgentPermissionSet((AgentPermission.FILESYSTEM, AgentPermission.KNOWLEDGE))
        capabilities = AgentCapabilityMetadata((AgentCapability.REASONING, AgentCapability.CODING))

        self.assertTrue(permissions.allows(AgentPermission.FILESYSTEM))
        self.assertFalse(permissions.allows(AgentPermission.PROVIDER))
        self.assertEqual(permissions.names(), ("filesystem", "knowledge"))
        self.assertTrue(capabilities.supports(AgentCapability.CODING))
        self.assertEqual(capabilities.names(), ("reasoning", "coding"))
        self.assertEqual(AgentMemoryScope.CONVERSATION.value, "conversation")
        self.assertEqual(AgentMemoryScope.SESSION.value, "session")
        self.assertEqual(AgentMemoryScope.PROJECT.value, "project")
        self.assertEqual(AgentMemoryScope.TEMPORARY.value, "temporary")
        self.assertEqual(AgentMemoryScope.READ_ONLY.value, "read_only")
        self.assertEqual(AgentHealthStatus.READY.value, "ready")


class BuiltInAgentTests(unittest.TestCase):
    def test_builtin_agents_are_metadata_skeletons(self):
        registry = register_builtin_agents(AgentRegistry())
        factory = register_builtin_agent_constructors(AgentFactory())

        self.assertEqual(len(BUILT_IN_AGENT_METADATA), 13)
        self.assertIn("steel_engineering", registry.agent_ids())
        self.assertIn("programming", factory.available_agent_ids())
        self.assertEqual(registry.metadata("programming").version, "1.0.0")
        self.assertIn(AgentCapability.CODING, registry.metadata("programming").capabilities)
        self.assertFalse(hasattr(factory.create("programming"), "execute"))


if __name__ == "__main__":
    unittest.main()
