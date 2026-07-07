from __future__ import annotations

import importlib
import unittest

from hgpt_ai_os.contracts import CONTRACT_PACKAGE_VERSION
from hgpt_ai_os.contracts import agent_contract as agent
from hgpt_ai_os.contracts import capability_contract as capability
from hgpt_ai_os.contracts import diagnostics_contract as diagnostics
from hgpt_ai_os.contracts import event_contract as event
from hgpt_ai_os.contracts import job_contract as job
from hgpt_ai_os.contracts import knowledge_contract as knowledge
from hgpt_ai_os.contracts import memory_contract as memory
from hgpt_ai_os.contracts import planner_contract as planner
from hgpt_ai_os.contracts import plugin_contract as plugin
from hgpt_ai_os.contracts import provider_contract as provider
from hgpt_ai_os.contracts import request_contract as request
from hgpt_ai_os.contracts import result_contract as result
from hgpt_ai_os.contracts import runtime_contract as runtime
from hgpt_ai_os.contracts import skill_contract as skill
from hgpt_ai_os.contracts import workflow_contract as workflow


CONTRACT_MODULES = (
    "runtime_contract",
    "provider_contract",
    "agent_contract",
    "skill_contract",
    "knowledge_contract",
    "plugin_contract",
    "workflow_contract",
    "planner_contract",
    "memory_contract",
    "diagnostics_contract",
    "job_contract",
    "event_contract",
    "result_contract",
    "request_contract",
    "capability_contract",
)


class ContractImportTests(unittest.TestCase):
    def test_all_contract_modules_import(self):
        for module_name in CONTRACT_MODULES:
            with self.subTest(module=module_name):
                module = importlib.import_module(f"hgpt_ai_os.contracts.{module_name}")
                self.assertEqual(module.CONTRACT_VERSION, CONTRACT_PACKAGE_VERSION)
                self.assertTrue(module.CONTRACT_LIFECYCLE)
                self.assertTrue(module.EXTENSION_RULES)
                self.assertTrue(module.BACKWARD_COMPATIBILITY_NOTES)

    def test_error_taxonomy_is_shared(self):
        provider_error = provider.ProviderError(
            error=diagnostics.ContractError(
                code=diagnostics.PlatformErrorCode.PROVIDER_UNAVAILABLE,
                message="provider unavailable",
            ),
            provider_id="provider.test",
        )

        self.assertFalse(provider_error.validate())
        self.assertIs(provider_error.error.code, diagnostics.PlatformErrorCode.PROVIDER_UNAVAILABLE)


class ContractConstructionTests(unittest.TestCase):
    def test_core_contract_dataclasses_construct_and_validate(self):
        health = diagnostics.HealthReport(component="runtime", status="ok")
        runtime_job = runtime.Job(
            job_id="job-1",
            tasks=(runtime.Task(task_id="task-1", name="contract test"),),
        )
        provider_request = provider.ProviderRequest(request_id="req-1", prompt="Generate text")
        provider_response = provider.ProviderResponse(request_id="req-1", text="Final text")
        agent_context = agent.AgentContext(agent_id="agent-1", session_id="session-1")
        skill_context = skill.SkillContext(skill_id="skill-1", caller_id="agent-1")
        knowledge_package = knowledge.KnowledgePackage(
            package_id="steel",
            version=knowledge.KnowledgeVersion(version="1.0"),
            sources=(
                knowledge.KnowledgeSource(
                    source_id="src-1",
                    source_type=knowledge.KnowledgeSourceType.DOCUMENT,
                    locator="knowledge/library/README.md",
                ),
            ),
        )
        plugin_manifest = plugin.PluginManifest(plugin_id="plugin-1", name="Plugin", version="1.0")
        workflow_def = workflow.Workflow(
            workflow_id="workflow-1",
            version="1.0",
            nodes=(workflow.WorkflowNode(node_id="node-1", kind="start"),),
        )
        intent = planner.Intent(
            intent_id="intent-1",
            kind=planner.IntentKind.GENERATE,
            text="Create plan",
        )
        task_graph = planner.TaskGraph(
            graph_id="graph-1",
            tasks=(planner.PlanTask(task_id="task-1", description="Run"),),
        )
        plan = planner.Plan(plan_id="plan-1", intent=intent, graph=task_graph)
        memories = (
            memory.ConversationMemory("mem-1", "conversation-1", "content"),
            memory.SessionMemory("mem-2", "session-1"),
            memory.ProjectMemory("mem-3", "project-1"),
            memory.KnowledgeMemory("mem-4", "package-1"),
        )
        job_request = job.JobRequest(job_id="job-2", kind="generation")
        platform_event = event.PlatformEvent(
            event_id="event-1",
            event_type=event.EventType.LIFECYCLE,
            source="contracts",
        )
        platform_result = result.PlatformResult(
            result_id="result-1",
            producer="contracts",
            success=True,
        )
        platform_request = request.PlatformRequest(
            request_id="request-1",
            requester="test",
            operation="validate",
        )
        cap = capability.Capability(name="contracts")

        contract_values = (
            health,
            runtime_job,
            provider_request,
            provider_response,
            agent_context,
            skill_context,
            knowledge_package,
            plugin_manifest,
            workflow_def,
            plan,
            job_request,
            platform_event,
            platform_result,
            platform_request,
            cap,
            *memories,
        )

        for value in contract_values:
            with self.subTest(value=type(value).__name__):
                self.assertEqual(value.validate(), ())

    def test_validation_hooks_return_contract_errors(self):
        errors = runtime.Job(job_id=" ").validate()

        self.assertEqual(len(errors), 1)
        self.assertIs(errors[0].code, diagnostics.PlatformErrorCode.CONTRACT_VALIDATION_FAILED)


class ContractCompatibilityTests(unittest.TestCase):
    def test_protocol_runtime_compatibility(self):
        class Component:
            component_id = "component-1"

            def start(self) -> None:
                return None

            def stop(self) -> None:
                return None

            def health(self) -> diagnostics.HealthReport:
                return diagnostics.HealthReport(component=self.component_id, status="ok")

        self.assertIsInstance(Component(), runtime.LifecycleComponent)

    def test_abc_subclass_contracts(self):
        class EchoProvider(provider.Provider):
            @property
            def metadata(self) -> provider.ProviderMetadata:
                return provider.ProviderMetadata(
                    provider_id="echo",
                    display_name="Echo",
                    version="1.0",
                    capabilities=(provider.ProviderCapability.TEXT_GENERATION,),
                )

            def generate(self, request: provider.ProviderRequest) -> provider.ProviderResponse:
                return provider.ProviderResponse(request_id=request.request_id, text=request.prompt)

            def health(self) -> provider.ProviderHealth:
                return provider.ProviderHealth(
                    metadata=self.metadata,
                    report=diagnostics.HealthReport(component="echo", status="ok"),
                )

        response = EchoProvider().generate(provider.ProviderRequest("req-2", "hello"))

        self.assertEqual(response.text, "hello")
        self.assertEqual(response.validate(), ())


if __name__ == "__main__":
    unittest.main()
