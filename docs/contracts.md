# LUCID PLATFORM Contracts

Sprint 02 defines stable platform contracts only. The files under
`src/hgpt_ai_os/contracts/` provide typed dataclasses, abstract interfaces,
runtime-checkable protocol interfaces, validation hooks, lifecycle metadata,
extension rules, backward compatibility notes, and a unified error taxonomy.
They do not implement providers, runtime behavior, GUI behavior, AI behavior,
business logic, persistence, network transport, or plugin execution.

## Shared Contract Rules

- Contract package version: `2.0.0`.
- Every module exposes `CONTRACT_VERSION`, `CONTRACT_LIFECYCLE`,
  `EXTENSION_RULES`, and `BACKWARD_COMPATIBILITY_NOTES`.
- All contract validation returns `tuple[ContractError, ...]`.
- All contract errors use `PlatformErrorCode` from `diagnostics_contract.py`.
- Extension data belongs in typed fields or `metadata` mappings.
- Future minor versions must be additive; future breaking changes require a new
  major contract version.

## Unified Error Model

`diagnostics_contract.py` owns the platform error taxonomy:

- `PlatformErrorCode` defines stable codes for validation, lifecycle,
  permission, execution, provider, knowledge, plugin, workflow, memory, and
  diagnostic failures.
- `ErrorSeverity` classifies informational, warning, recoverable, and fatal
  conditions.
- `ContractError` is the common error shape used by every contract module.
- `HealthReport`, `DiagnosticEvent`, and `DiagnosticResult` provide the shared
  diagnostics surface.

## Runtime Contract

`runtime_contract.py` defines the host runtime boundary:

- Dataclasses: `Job`, `Task`, `Event`, `Cancellation`, `Retry`, `Shutdown`,
  and `HealthCheck`.
- State machines: `RuntimeState` and `TaskState`.
- Protocol: `LifecycleComponent` for start, stop, and health operations.
- ABC: `Runtime` for registration, job submission, cancellation, and shutdown.

This is a contract only. It does not modify or replace the current runtime.

## Provider Contract

`provider_contract.py` defines provider interoperability without vendor code:

- Dataclasses: `ProviderRequest`, `ProviderResponse`, `ProviderPolicy`,
  `ProviderHealth`, `ProviderMetadata`, and `ProviderError`.
- Capabilities: `ProviderCapability`.
- Protocols: `StreamingProvider` and `StructuredOutputProvider`.
- ABC: `Provider`.

The module contains no Gemini, OpenAI, Ollama, network, or credential logic.

## Agent Contract

`agent_contract.py` defines agent execution boundaries:

- Dataclasses: `AgentContext`, `AgentExecution`, and `AgentResult`.
- Policies: `AgentPermission`, `ApprovalPolicy`, and `MemoryScope`.
- Protocol: `AgentRuntimeView`.
- ABC: `Agent`.

Agents must declare permissions and memory scope before execution.

## Skill Contract

`skill_contract.py` defines skill invocation boundaries:

- Dataclasses: `SkillContext`, `SkillInput`, and `SkillOutput`.
- Capabilities: `SkillCapability`.
- Protocol: `SkillValidator`.
- ABC: `Skill`.

Skills publish capabilities and exchange serializable input/output mappings.

## Knowledge Contract

`knowledge_contract.py` defines knowledge package and retrieval boundaries:

- Dataclasses: `KnowledgePackage`, `KnowledgeSource`, `KnowledgeCitation`,
  `KnowledgeQuery`, `KnowledgeResult`, and `KnowledgeVersion`.
- Source typing: `KnowledgeSourceType`.
- Protocol: `KnowledgeIndex`.
- ABC: `KnowledgeRepository`.

Citations preserve source identity and locator information.

## Plugin Contract

`plugin_contract.py` defines plugin metadata and sandbox boundaries:

- Dataclasses: `PluginManifest`, `PluginContext`, and `SandboxRequirements`.
- Enums: `PluginPermission`, `PluginLifecycle`, and `PluginCapability`.
- Protocol: `PluginSandbox`.
- ABC: `Plugin`.

This is declaration-only and contains no plugin loading or execution logic.

## Workflow Contract

`workflow_contract.py` defines workflow graph boundaries:

- Dataclasses: `Workflow`, `WorkflowNode`, `WorkflowContext`, and
  `WorkflowExecution`.
- State machine: `WorkflowExecutionState`.
- Protocol: `WorkflowStore`.
- ABC: `WorkflowRunner`.

Workflow dependencies must reference nodes in the same workflow graph.

## Planner Contract

`planner_contract.py` defines planning boundaries:

- Dataclasses: `Intent`, `PlanTask`, `TaskGraph`, `Plan`, and
  `PlannerResult`.
- Intent typing: `IntentKind`.
- Protocol: `IntentClassifier`.
- ABC: `Planner`.

Planner task dependencies must reference tasks in the same task graph.

## Memory Contract

`memory_contract.py` defines memory scope boundaries:

- Dataclasses: `ConversationMemory`, `SessionMemory`, `ProjectMemory`, and
  `KnowledgeMemory`.
- Retention typing: `MemoryRetention`.
- Protocol: `MemoryReader`.
- ABC: `MemoryStore`.

Memory records must remain scoped to their declared memory type.

## Diagnostics Contract

`diagnostics_contract.py` defines platform diagnostics:

- Dataclasses: `HealthReport`, `DiagnosticEvent`, `DiagnosticResult`, and
  `ContractError`.
- Error taxonomy: `PlatformErrorCode` and `ErrorSeverity`.
- Protocol: `DiagnosticReporter`.
- ABC: `DiagnosticContract`.

Diagnostics provide shared health and error reporting for all contracts.

## Job Contract

`job_contract.py` defines queue-level job boundaries:

- Dataclasses: `JobRequest`, `JobState`, and `JobReceipt`.
- Enums: `JobPriority` and `JobStatus`.
- Protocol: `JobQueue`.
- ABC: `JobController`.

Jobs preserve stable identifiers across queues and runtime boundaries.

## Event Contract

`event_contract.py` defines event publication boundaries:

- Dataclasses: `PlatformEvent`, `EventSubscription`, and `EventDelivery`.
- Event typing: `EventType`.
- Protocol: `EventHandler`.
- ABC: `EventBus`.

Unknown event types are additive and must be safely ignored by older consumers.

## Result Contract

`result_contract.py` defines result exchange boundaries:

- Dataclasses: `PlatformResult` and `ResultReference`.
- State typing: `ResultStatus`.
- Protocol: `ResultConsumer`.
- ABC: `ResultStore`.

Results carry data, success state, and contract errors without assuming storage.

## Request Contract

`request_contract.py` defines platform request boundaries:

- Dataclasses: `PlatformRequest` and `RequestEnvelope`.
- Priority typing: `RequestPriority`.
- Protocol: `RequestAuthorizer`.
- ABC: `RequestDispatcher`.

Requests preserve requester, operation, payload, and authorization errors.

## Capability Contract

`capability_contract.py` defines capability declaration and negotiation:

- Dataclasses: `Capability`, `CapabilityRequirement`, and `CapabilityGrant`.
- State typing: `CapabilityStatus`.
- Protocol: `CapabilityProvider`.
- ABC: `CapabilityNegotiator`.

Unknown required capabilities must be denied by older hosts; optional
capabilities may be ignored.
