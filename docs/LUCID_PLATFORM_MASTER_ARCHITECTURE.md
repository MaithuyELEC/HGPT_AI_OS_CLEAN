# LUCID PLATFORM Master Architecture

Status: Architecture Freeze  
Authority: Single Source of Truth for repository architecture  
Scope: Entire LUCID PLATFORM / LUCID AUTO compatibility repository  
Time horizon: 5 years minimum  
Runtime baseline: Existing production path remains compatible until explicitly migrated

## 0. Architecture Contract

This document is the authoritative architecture specification for the project.
When README files, sprint notes, module comments, or old architecture documents
conflict with this document, this document wins.

The project is entering Architecture Freeze. During Architecture Freeze:

- Production code must not be changed to chase new platform ideas.
- Runtime behavior must not be changed without a written migration step.
- GUI behavior must remain stable unless a future sprint explicitly opens GUI
  scope.
- AI provider behavior must remain stable unless a future sprint explicitly opens
  provider scope.
- Architecture work must be additive, documented, reviewed, and test-backed.
- Existing LUCID AUTO production behavior is a compatibility contract, not legacy
  waste.

This repository has two truths that must both be respected:

1. Current product truth: LUCID AUTO generates production marketing outputs using
   topic analysis, knowledge retrieval, AI generation, and DOCX export.
2. Platform direction: LUCID PLATFORM becomes a universal AI operating system for
   providers, knowledge, agents, plugins, marketplace distribution, enterprise
   control, and Digital Factory workflows.

No sprint may break truth 1 while implementing truth 2.

## 1. Vision

LUCID PLATFORM is a universal AI production operating system for industrial
operations, beginning with HGPT Steel and expanding into a broad, provider-neutral
AI platform.

The product vision is to turn repeatable knowledge work into governed production
systems:

- Capture domain knowledge.
- Route user intent to the right workflow.
- Select the best available AI provider.
- Execute agent skills with observable state.
- Produce useful artifacts reliably.
- Support free-first adoption.
- Scale into enterprise and cloud deployments without rewriting the core.

The long-term product stages are:

| Stage | Product Identity | Primary Outcome |
| --- | --- | --- |
| v1 | LUCID AUTO compatibility line | Stable local AI production application |
| v2 | LUCID PLATFORM | Universal runtime, providers, knowledge, agents, plugins |
| v3 | LUCID Marketplace | Installable skills, templates, agents, workflows |
| v4 | LUCID Enterprise | Teams, tenants, audit, policy, SSO, deployment controls |
| v5 | LUCID Digital Factory | Connected production workflows and operational AI systems |
| v6 | LUCID Cloud | Hybrid cloud orchestration, managed marketplace, remote compute |

## 2. Design Principles

LUCID PLATFORM follows these non-negotiable principles.

### 2.1 Compatibility first

The current production path must continue to run while platform abstractions are
introduced. Existing entry points such as GUI generation, CLI production, provider
configuration, knowledge retrieval, and DOCX export must be wrapped before they
are replaced.

### 2.2 Free first, paid later

The platform must be useful without paid subscriptions. Paid providers and future
paid marketplace features are enhancements, not prerequisites for basic local
value.

### 2.3 Provider neutrality

No provider owns the architecture. Gemini, OpenAI, Anthropic, Ollama, local
models, and future providers are interchangeable behind provider contracts.

### 2.4 Local-first operation

The desktop/local runtime remains a first-class product. Cloud services may add
sync, scale, remote execution, and marketplace delivery, but the platform must
continue to support local work.

### 2.5 Explicit boundaries

Runtime, providers, agents, knowledge, plugins, marketplace, enterprise, GUI, and
release systems must communicate through declared contracts instead of hidden
imports.

### 2.6 Observable execution

Every production run must expose enough metadata to answer: what intent was
routed, what knowledge was used, what provider was called, what fallback happened,
what files were created, and why failures occurred.

### 2.7 Boring persistence, strong contracts

Prefer simple file and database formats until scale requires more. Complexity
belongs behind stable interfaces.

### 2.8 Incremental migration

Every migration must preserve user-visible behavior, ship with tests, and leave a
clear rollback path.

### 2.9 Security by default

Secrets must not leak into logs, documents, metadata, screenshots, or exported
artifacts. Plugins and marketplace packages must be treated as untrusted until
verified.

### 2.10 Industrial reliability

The platform is for production work. Error messages, retries, fallbacks, audit
trails, offline mode, and release verification are core architecture, not polish.

## 3. Free First Strategy

Free First means users can install LUCID PLATFORM and get real value with no paid
AI account and no cloud account.

### 3.1 Free tier capabilities

The free local product must support:

- Local workspace creation.
- Local knowledge packages.
- Local templates.
- Local agents and skills.
- Ollama or other local model adapters where available.
- Manual provider configuration for free or user-owned API keys.
- Offline browsing of installed knowledge and templates.
- Local artifact export.
- Plugin development and sideloading.

### 3.2 Paid enhancement boundaries

Paid services may add:

- Managed cloud sync.
- Managed provider routing.
- Team workspaces.
- Enterprise audit retention.
- Marketplace purchases.
- Hosted model execution.
- Premium domain knowledge packs.
- Remote agent execution.

Paid features must not be hard dependencies of the local runtime.

### 3.3 Free-first provider order

Default provider strategy should prefer low-friction and user-owned options:

1. Local/offline provider if configured and capable.
2. User-selected configured provider.
3. Free quota cloud provider if configured.
4. Paid provider if explicitly configured.
5. Clean failure with actionable setup guidance.

The current compatibility path may use its existing order until migrated behind
the platform provider router.

## 4. Universal AI Platform Philosophy

LUCID PLATFORM is not a single-purpose content generator. It is a universal AI
platform that can host multiple domains and workflows.

The universal model is:

```text
User Intent
    -> Intent Router
    -> Workflow or Agent Plan
    -> Knowledge Retrieval
    -> Provider Selection
    -> Skill Execution
    -> Artifact Generation
    -> Review, Audit, Export
```

Universal does not mean generic output. Each domain must supply its own:

- Knowledge packages.
- Skill definitions.
- Workflow templates.
- Validation rules.
- Export formats.
- Safety constraints.
- Review steps.

The platform provides the operating system. Domains provide the work.

## 5. Runtime Architecture

The runtime is the root of platform execution. The current additive foundation is
`hgpt_ai_os.platform`.

### 5.1 Runtime responsibilities

The runtime owns:

- Immutable runtime context.
- Environment name.
- Workspace path.
- Application version.
- Component lifecycle.
- Service registry.
- Startup and shutdown ordering.
- Runtime status reporting.
- Future process, thread, and job orchestration boundaries.

The runtime must not own:

- GUI widget details.
- Provider-specific HTTP payloads.
- Knowledge ranking internals.
- Plugin business logic.
- Marketplace billing logic.
- Enterprise tenant policy internals.

### 5.2 Current runtime boundary

Current platform modules:

```text
src/hgpt_ai_os/platform/
├── interfaces.py
├── registry.py
├── runtime.py
└── __init__.py
```

The current runtime must remain additive until migration sprints wrap the
existing production path.

### 5.3 Target runtime topology

```text
Application Entry Points
├── Desktop GUI
├── CLI
├── Local API
└── Future Cloud Worker
        |
        v
PlatformRuntime
├── RuntimeContext
├── ServiceRegistry
├── ComponentLifecycle
├── EventBus
├── JobRuntime
├── PolicyRuntime
├── ProviderRuntime
├── KnowledgeRuntime
├── AgentRuntime
├── PluginRuntime
└── TelemetryRuntime
```

### 5.4 Runtime lifecycle

Runtime lifecycle phases:

1. Load settings.
2. Resolve workspace.
3. Initialize registry.
4. Register core services.
5. Load trusted plugins.
6. Register providers.
7. Register knowledge sources.
8. Register agents and skills.
9. Start lifecycle components.
10. Accept jobs.
11. Stop components in reverse order.
12. Flush logs, audit, and run metadata.

### 5.5 Runtime invariants

- Components cannot be added after runtime start unless a future hot-load API is
  explicitly designed.
- Failed startup must stop already-started components.
- Stop must be best-effort and report the first failure.
- Runtime status must be safe to display to users.
- Runtime context must be immutable during a run.

## 6. Provider Abstraction

Provider abstraction isolates AI model vendors from workflows, agents, GUI, and
content generation.

### 6.1 Current provider reality

Current compatibility modules include:

- `hgpt_ai_os.ai.client`
- `hgpt_ai_os.ai.gemini_client`
- `hgpt_ai_os.ai.config_resolver`

Current provider concepts include:

- `AIResponse`
- `AIProviderError`
- `GeminiProvider`
- `OpenAIProvider`
- `AnthropicProvider`
- `OllamaProvider`
- `AIManager`
- `LucidAI`
- `ProviderFactory`
- `provider_status()`

These are production compatibility surfaces. They must not be broken without a
documented migration adapter.

### 6.2 Target provider contract

All providers must implement a common contract:

```text
Provider
├── id
├── display_name
├── capabilities
├── cost_profile
├── privacy_profile
├── latency_profile
├── availability_status()
├── generate(request) -> ProviderResult
├── stream(request) -> ProviderStream
└── validate_config() -> ProviderConfigStatus
```

### 6.3 Provider request contract

A provider request must include:

- System prompt.
- User prompt.
- Optional tool definitions.
- Optional response schema.
- Model preference.
- Token budget.
- Timeout.
- Privacy classification.
- Cost ceiling.
- Offline allowance.
- Trace ID.

### 6.4 Provider result contract

A provider result must include:

- Provider ID.
- Model ID.
- Content.
- Structured output when requested.
- Usage metadata.
- Finish reason.
- Retryable failure classification.
- Latency.
- Cost estimate when available.
- Fallback history.
- Redacted diagnostic metadata.

### 6.5 Provider capabilities

Capabilities must be explicit:

- Text generation.
- Structured JSON generation.
- Vision input.
- Image generation.
- Embeddings.
- Reranking.
- Speech-to-text.
- Text-to-speech.
- Tool calling.
- Streaming.
- Local execution.
- Offline execution.

Workflows must request capabilities, not provider names.

### 6.6 Provider configuration

Provider configuration sources may include:

- Environment variables.
- User config file.
- OS user config directory.
- Packaged runtime config.
- Enterprise policy.
- Cloud-managed workspace settings.

Secrets must be stored only in approved secret stores or local config paths with
clear redaction rules. Secrets must never be exported in documents.

## 7. Agent Architecture

Agents are goal-oriented platform components that plan, call skills, use
knowledge, call providers, and produce artifacts or actions.

### 7.1 Current agent reality

Current compatibility modules include:

- `hgpt_ai_os.agents.base_agent`
- `hgpt_ai_os.agents.maintenance.maintenance_agent`
- `hgpt_ai_os.agents.marketing.marketing_agent`
- `hgpt_ai_os.kernel.agent_manager`

These modules establish the early agent concept but are not the final universal
agent runtime.

### 7.2 Target agent model

```text
Agent
├── Manifest
├── Permissions
├── Skills
├── Tools
├── Knowledge bindings
├── Provider policy
├── Memory policy
├── Planner
├── Executor
├── Validator
└── Audit trail
```

### 7.3 Agent types

The platform must support:

- Personal assistant agents.
- Domain agents.
- Workflow agents.
- Review agents.
- Quality agents.
- Maintenance agents.
- Production agents.
- Marketplace-installed agents.
- Enterprise-managed agents.
- Digital Factory agents.

### 7.4 Agent execution phases

1. Receive normalized intent.
2. Check permissions.
3. Select agent or workflow.
4. Build plan.
5. Retrieve knowledge.
6. Select provider.
7. Execute skills.
8. Validate outputs.
9. Produce artifacts.
10. Store run metadata.
11. Request review or complete.

### 7.5 Agent safety

Agents must:

- Declare permissions before executing external actions.
- Separate read actions from write actions.
- Support dry-run mode for high-risk actions.
- Record decisions and provider calls.
- Respect enterprise policy.
- Never bypass plugin sandbox rules.

## 8. Intent Router

The Intent Router converts user input into executable platform intent.

### 8.1 Router responsibilities

The router owns:

- Intent classification.
- Domain detection.
- Workflow selection.
- Agent selection.
- Required capability detection.
- Risk classification.
- Missing input detection.
- Clarifying question policy.
- Route confidence scoring.

### 8.2 Intent model

An intent must include:

- Raw user input.
- Normalized task.
- Domain.
- Requested artifact.
- Target audience.
- Required knowledge domains.
- Required provider capabilities.
- Required plugins or skills.
- Risk level.
- Confidence score.
- Clarification status.

### 8.3 Routing targets

The router may target:

- Existing production generator.
- Marketing workflow.
- Knowledge search workflow.
- Agent plan.
- Plugin command.
- Marketplace install flow.
- Enterprise admin workflow.
- Digital Factory workflow.
- Future cloud job.

### 8.4 Router rule

The router must never directly implement business logic. It routes to workflows,
agents, and skills that own execution.

## 9. Knowledge Architecture

Knowledge is a first-class platform asset.

### 9.1 Current knowledge reality

Current compatibility modules include:

- `knowledge/`
- `knowledge/metadata/`
- `hgpt_ai_os.knowledge.repository`
- `hgpt_ai_os.knowledge.retrieval_pipeline`
- `hgpt_ai_os.knowledge.bundle`
- `hgpt_ai_os.intelligence.topic_analyzer`
- `hgpt_ai_os.intelligence.knowledge_ranker`
- `hgpt_ai_os.intelligence.knowledge_search`

The canonical current retrieval path is the knowledge retrieval pipeline, which
analyzes topic input, loads knowledge packages, ranks them, and returns relevant
results.

### 9.2 Knowledge package model

A knowledge package must have:

- Stable ID.
- Title.
- Domain.
- Category.
- Tags.
- Version.
- Source path.
- License.
- Owner.
- Trust level.
- Language.
- Created and updated timestamps.
- Optional embeddings.
- Optional validation rules.

### 9.3 Knowledge layers

```text
Knowledge Runtime
├── Package Registry
├── Metadata Store
├── Content Store
├── Search Index
├── Embedding Index
├── Ranker
├── Context Builder
├── Citation Policy
└── Validation Rules
```

### 9.4 Knowledge source types

The platform must support:

- Local Markdown packages.
- JSON metadata.
- DOCX imports.
- PDF imports.
- Spreadsheet imports.
- Database records.
- Plugin-provided knowledge.
- Marketplace knowledge packs.
- Enterprise-managed knowledge.
- Future cloud-synced knowledge.

### 9.5 Retrieval rules

- Retrieval must be deterministic enough to debug.
- Every context item must have a source ID.
- Retrieved context is evidence, not copy-ready prose.
- Exported final artifacts must not leak internal context markers.
- Ranking logic must be testable without provider calls.
- Knowledge search must work offline for installed local packages.

## 10. Plugin SDK

The Plugin SDK allows third parties and internal teams to extend LUCID PLATFORM.

### 10.1 Plugin types

Supported plugin types:

- Provider adapter.
- Agent.
- Skill.
- Workflow.
- Knowledge package.
- Exporter.
- Importer.
- UI panel.
- CLI command.
- Marketplace listing.
- Enterprise policy extension.
- Digital Factory connector.

### 10.2 Plugin manifest

Every plugin must define a manifest:

```text
plugin_id
name
version
publisher
description
entrypoint
plugin_type
minimum_platform_version
permissions
capabilities
dependencies
license
signing_info
```

### 10.3 Plugin runtime contract

Plugins must:

- Register through the platform registry.
- Declare all permissions.
- Avoid importing GUI internals unless they are UI plugins.
- Avoid importing provider internals unless they are provider plugins.
- Support validation before activation.
- Be unloadable or disableable.
- Report health and version.

### 10.4 Plugin compatibility

Plugins target platform contracts, not implementation details. Breaking plugin
contracts requires a major platform version.

### 10.5 Plugin sandbox

Plugin sandbox policy must eventually support:

- File read allowlists.
- File write allowlists.
- Network permissions.
- Secret access scopes.
- Provider access scopes.
- Enterprise approval.
- Marketplace trust levels.

## 11. Marketplace Architecture

The marketplace distributes plugins, skills, agents, templates, providers,
knowledge packs, and workflows.

### 11.1 Marketplace goals

The marketplace must:

- Make installation easy.
- Preserve trust and provenance.
- Support free and paid packages.
- Support offline-exportable packages.
- Support enterprise approval workflows.
- Support version pinning.
- Prevent unsafe auto-upgrades.

### 11.2 Marketplace package model

Marketplace packages include:

- Package manifest.
- Signed artifact.
- Publisher identity.
- Version.
- Dependencies.
- Compatibility range.
- Changelog.
- License.
- Trust score.
- Security scan result.
- Optional price and entitlement.

### 11.3 Installation flow

1. Search marketplace.
2. Inspect package metadata.
3. Validate compatibility.
4. Review permissions.
5. Download artifact.
6. Verify signature.
7. Install into plugin store.
8. Register with runtime.
9. Run health check.
10. Enable package.

### 11.4 Enterprise marketplace mode

Enterprise deployments may disable the public marketplace and use a private
catalog with approved packages only.

## 12. Enterprise Architecture

Enterprise architecture adds governance, control, auditability, and deployment
options without forking the platform.

### 12.1 Enterprise concerns

The enterprise layer owns:

- Tenants.
- Workspaces.
- Users.
- Roles.
- Permissions.
- Policy.
- Audit.
- Secrets.
- Provider budgets.
- Data retention.
- Compliance exports.
- Deployment controls.

### 12.2 Tenant model

```text
Tenant
├── Workspaces
├── Users
├── Groups
├── Roles
├── Policies
├── Provider configs
├── Knowledge catalogs
├── Plugin catalogs
├── Audit logs
└── Billing or cost allocation
```

### 12.3 Policy model

Policies may govern:

- Allowed providers.
- Allowed models.
- Data residency.
- Max cost per run.
- Plugin permissions.
- Knowledge visibility.
- Export formats.
- Approval requirements.
- Retention periods.
- Network access.

### 12.4 Enterprise deployment modes

Supported target modes:

- Single-user desktop.
- Team desktop with shared folder.
- On-prem server.
- Private cloud.
- Managed LUCID Cloud.
- Hybrid local plus cloud execution.

## 13. Digital Factory Architecture

Digital Factory architecture connects LUCID PLATFORM to real industrial
operations.

### 13.1 Digital Factory domains

Initial domains:

- Marketing production.
- QA/QC.
- Maintenance.
- Project management.
- Production planning.
- Welding and fabrication knowledge.
- Site issue analysis.
- SOP generation.
- Reporting.

Future domains:

- ERP integration.
- MES integration.
- IoT machine data.
- Inspection data.
- Inventory.
- Procurement.
- Scheduling.
- Safety.
- Training.

### 13.2 Factory workflow model

```text
Factory Event or User Request
    -> Intent Router
    -> Domain Workflow
    -> Knowledge Retrieval
    -> Agent Execution
    -> Human Review
    -> Export or System Action
    -> Audit and Feedback
```

### 13.3 Factory connector model

Factory connectors must be plugins with explicit permissions. They may connect to:

- Filesystems.
- Databases.
- ERP systems.
- MES systems.
- Email.
- Shared drives.
- Sensor APIs.
- Inspection tools.
- Reporting systems.

### 13.4 Human-in-the-loop rule

For factory-impacting actions, the platform must support human approval before
external state changes. AI may recommend; authorized users approve.

## 14. Folder Structure

### 14.1 Current repository structure

The repository currently contains:

```text
HGPT_AI_OS_CLEAN/
├── app/
├── assets/
├── docs/
├── installer/
├── knowledge/
├── planner/
├── scripts/
├── src/hgpt_ai_os/
├── templates/
├── tests/
├── build_mac.sh
├── build_windows.bat
├── lucid.spec
├── README.md
└── requirements.txt
```

### 14.2 Target source structure

The long-term source structure is:

```text
src/hgpt_ai_os/
├── platform/          # Universal runtime contracts and lifecycle
├── core/              # Shared primitives, events, constants, results
├── ai/                # Compatibility AI providers until migrated
├── providers/         # Future platform-native provider adapters
├── knowledge/         # Knowledge repositories, packages, retrieval
├── intelligence/      # Topic analysis, ranking, classification
├── agents/            # Agent definitions and compatibility agents
├── skills/            # Future universal skills
├── workflows/         # Platform-native workflows
├── workflow/          # Compatibility workflow modules
├── plugins/           # Future plugin runtime and SDK
├── marketplace/       # Future marketplace client and package model
├── enterprise/        # Future tenant, policy, audit, security controls
├── factory/           # Future Digital Factory domains and connectors
├── content/           # Content generation compatibility modules
├── template/          # Template loading and rendering
├── gui/               # Desktop GUI
├── cli/               # CLI entry points
├── database/          # Local persistence
├── settings/          # User/provider configuration UI and storage
└── runtime/           # Compatibility runtime modules
```

### 14.3 Documentation structure

```text
docs/
├── LUCID_PLATFORM_MASTER_ARCHITECTURE.md
├── architecture/
├── knowledge/
├── migration_lucid_auto_to_platform.md
├── roadmap.md
└── release/
```

### 14.4 Data and artifact structure

```text
knowledge/             # Versioned local knowledge source
templates/             # Versioned templates
planner/               # Planning input files
outputs/               # Generated local artifacts, not source truth
release/               # Generated release artifacts, not source truth
build/                 # Generated build artifacts
dist/                  # Generated packaged artifacts
```

Generated artifacts must not be treated as architecture source.

## 15. Dependency Rules

### 15.1 Directional dependency rule

Dependencies flow inward:

```text
GUI / CLI / App
    -> Workflows / Agents
        -> Platform Contracts
        -> Providers / Knowledge / Plugins
            -> Core primitives
```

Lower layers must not import higher layers.

### 15.2 Forbidden dependencies

- `platform` must not import `gui`.
- `platform` must not import provider implementation modules.
- `knowledge` must not import `gui`.
- `providers` must not import `gui`.
- `plugins` must not import `gui` except UI plugin adapters.
- `enterprise` policy must not depend on desktop widgets.
- `marketplace` package metadata must not depend on runtime execution details.
- Tests must not depend on generated user outputs unless explicitly marked
  integration or golden artifact tests.

### 15.3 Compatibility exception

Existing compatibility modules may currently have imperfect dependencies. They
must be wrapped and migrated incrementally. New code must follow the target rules.

### 15.4 Dependency introduction rule

New third-party dependencies require:

- Clear purpose.
- License review.
- Packaging impact check.
- Offline impact check.
- Security review for network or code execution libraries.
- Tests proving importability in the supported runtime.

## 16. Layer Rules

### 16.1 Layer map

```text
Presentation Layer
    Desktop GUI, CLI, future web UI

Application Layer
    Workflows, orchestration, production services

Domain Layer
    Agents, skills, factory domains, knowledge domain rules

Platform Layer
    Runtime, registry, lifecycle, event bus, job runtime

Infrastructure Layer
    Providers, filesystem, database, network, marketplace transport

Data Layer
    Knowledge, templates, configs, run metadata, audit logs
```

### 16.2 Layer ownership

- Presentation displays state and collects input.
- Application coordinates work.
- Domain defines business meaning.
- Platform provides execution contracts.
- Infrastructure talks to external systems.
- Data stores durable facts and artifacts.

### 16.3 Layer crossing

Layers cross only through:

- Interfaces.
- Data classes.
- Service registry lookups.
- Events.
- Explicit adapters.

Hidden imports across layers are architecture debt.

## 17. Coding Rules

### 17.1 General coding rules

- Keep production changes small and scoped.
- Prefer explicit data objects over unstructured dictionaries at boundaries.
- Preserve backward-compatible public APIs until migration is complete.
- Do not hide provider failures behind empty strings in new platform contracts.
- Return structured errors for recoverable production failures.
- Log enough to debug without leaking secrets.
- Avoid global mutable state except documented compatibility constants.
- Keep import side effects minimal.

### 17.2 Public API rules

Public platform APIs require:

- Type hints.
- Docstrings for contracts.
- Tests.
- Compatibility notes.
- Versioning strategy.

### 17.3 Error handling rules

Errors must classify:

- Configuration error.
- Authentication error.
- Authorization error.
- Quota error.
- Timeout.
- Network error.
- SSL error.
- Provider HTTP error.
- Parse error.
- Validation error.
- Policy denial.
- Unknown error.

### 17.4 Documentation rule

Any new subsystem requires:

- Architecture note.
- Public contract.
- Migration note if replacing compatibility behavior.
- Test plan.

## 18. Testing Rules

### 18.1 Test levels

Required test levels:

- Unit tests for pure logic.
- Contract tests for interfaces.
- Integration tests for runtime wiring.
- Provider tests with mocked transports.
- Optional live provider tests gated by credentials.
- GUI smoke tests for GUI-scope changes.
- Packaging verification for release-scope changes.
- Migration tests for compatibility wrappers.

### 18.2 Provider testing

Provider tests must verify:

- Missing configuration.
- Invalid key handling.
- Timeout handling.
- SSL error handling.
- HTTP error handling.
- Retry and fallback classification.
- Response parsing.
- Redaction of secrets.

Live provider tests must be opt-in.

### 18.3 Knowledge testing

Knowledge tests must verify:

- Metadata loading.
- Missing source handling.
- Search term extraction.
- Ranking behavior.
- Context building.
- No leakage of internal context markers into final exports.

### 18.4 Release testing

Release testing must verify:

- Version source.
- Build artifact layout.
- Runtime dependencies.
- Bundled assets.
- Bundled knowledge.
- Bundled templates.
- Installer inputs.
- No stale hard-coded names.

### 18.5 Test isolation

Tests must not write to real user output directories unless explicitly marked
manual or integration and approved. Prefer temporary paths.

## 19. Release Process

### 19.1 Release principles

- Release truth comes from source, not manual artifact names.
- Generated build artifacts are not source truth.
- Local verification and CI verification must agree on artifact layout.
- Release notes must describe user-visible changes and migration impact.

### 19.2 Version source

The application version must be read from `src/hgpt_ai_os/version.py` unless a
future version authority replaces it through an explicit migration.

### 19.3 Windows release target

The accepted Windows packaging direction is OneDir:

```text
dist/LUCID/
└── LUCID.exe
```

The installer must install from the OneDir tree. Verification must prove bundled
runtime dependencies, especially Qt runtime files, not merely check that an exe
file exists.

### 19.4 macOS release target

macOS release produces an app bundle and DMG according to release scripts. The
same source version and bundled resource rules apply.

### 19.5 Release checklist

Before release:

1. Confirm clean intended diff.
2. Run unit tests.
3. Run provider config tests.
4. Run knowledge tests.
5. Run GUI smoke when GUI changed.
6. Run packaging verifier when packaging changed.
7. Verify version source.
8. Verify bundled resources.
9. Generate release notes.
10. Tag release from the approved branch.

## 20. Migration Strategy

Migration from LUCID AUTO to LUCID PLATFORM must be incremental.

### 20.1 Migration phases

| Phase | Goal | Rule |
| --- | --- | --- |
| 1 | Add platform runtime | No production behavior change |
| 2 | Wrap providers | Preserve existing provider outcomes |
| 3 | Wrap knowledge | Preserve retrieval behavior |
| 4 | Introduce intent router | Route to existing workflows first |
| 5 | Introduce agent runtime | Existing agents become adapters |
| 6 | Add plugin SDK | Plugins target platform contracts |
| 7 | Add marketplace | Install only trusted local packages first |
| 8 | Add enterprise controls | Policy is enforced at runtime boundary |
| 9 | Add Digital Factory workflows | Human approval for external actions |
| 10 | Add cloud architecture | Hybrid, opt-in, policy-governed |

### 20.2 Strangler pattern

Existing modules are not rewritten wholesale. New platform contracts wrap them,
then route traffic through the contracts. Old direct paths are removed only after:

- The wrapper is tested.
- The GUI and CLI use the wrapper.
- Release packaging uses the wrapper.
- Regression outputs are accepted.
- Rollback is documented.

### 20.3 Migration safety

Every migration PR must state:

- Old path.
- New path.
- Compatibility adapter.
- Behavior expected to remain identical.
- Tests proving compatibility.
- Known limitations.

## 21. Versioning Strategy

### 21.1 Product versioning

Use semantic versioning for platform releases:

```text
MAJOR.MINOR.PATCH
```

- Major: breaking platform contract or migration milestone.
- Minor: new compatible capability.
- Patch: bug fix, packaging fix, documentation fix.

### 21.2 Sprint labels

Sprint labels are planning markers, not substitutes for product versions.

Example:

```text
LUCID PLATFORM v1.2.0, Sprint 04 Agent Runtime
```

### 21.3 Contract versioning

Public contracts may have their own versions:

- Provider API version.
- Plugin manifest version.
- Skill manifest version.
- Knowledge package version.
- Marketplace package version.
- Enterprise policy version.

Breaking a contract requires either a compatibility adapter or a major version.

## 22. Branch Strategy

### 22.1 Branch types

Recommended branches:

- `main`: stable release-ready branch.
- `develop`: integration branch if team size requires it.
- `sprint/<number>-<name>`: sprint implementation branches.
- `fix/<scope>-<summary>`: focused bug fix branches.
- `release/<version>`: release stabilization branches.
- `docs/<summary>`: documentation-only branches.

### 22.2 Branch rules

- Architecture Freeze branches may modify docs only.
- Sprint branches must declare scope before implementation starts.
- Production code changes require tests.
- Release branches accept only bug fixes, packaging fixes, release notes, and
  verification updates.
- Emergency fixes must be cherry-picked back to active development branches.

### 22.3 Merge rules

Before merge:

- Diff matches declared scope.
- Tests pass or skipped tests are documented.
- Architecture contracts are not violated.
- Migration notes are updated when applicable.
- Release impact is understood.

## 23. Long-Term Roadmap

### 23.1 Five-year roadmap

Year 1:

- Stabilize LUCID AUTO compatibility.
- Complete platform runtime.
- Migrate provider abstraction.
- Migrate knowledge abstraction.
- Add intent router.
- Add universal agent runtime.
- Add plugin SDK foundation.

Year 2:

- Add marketplace package model.
- Add private plugin catalog.
- Add enterprise workspace and policy.
- Add audit trails.
- Add Digital Factory workflow foundation.
- Add more local/offline provider support.

Year 3:

- Add managed marketplace.
- Add advanced skill orchestration.
- Add team collaboration.
- Add connector framework.
- Add ERP/MES connector pilots.
- Add cloud sync.

Year 4:

- Add enterprise cloud deployment.
- Add hybrid local/cloud execution.
- Add managed provider routing.
- Add fleet administration.
- Add compliance exports.
- Add production-grade factory integrations.

Year 5:

- Add autonomous workflow recommendations.
- Add cross-factory knowledge learning.
- Add marketplace monetization maturity.
- Add high-availability cloud control plane.
- Add industrial AI governance suite.

### 23.2 Sprint roadmap baseline

Current planning sequence:

1. Sprint 01 Universal Runtime.
2. Sprint 02 Provider Layer.
3. Sprint 03 Universal Knowledge.
4. Sprint 04 Agent System.
5. Sprint 05 Plugin SDK.
6. Sprint 06 Marketplace Architecture.
7. Sprint 07 Enterprise Architecture.
8. Sprint 08 Digital Factory Architecture.

Sprint 02 must not start until Architecture Freeze is complete and accepted.

## 24. Non-Functional Requirements

### 24.1 Reliability

- Provider failures must not crash the app.
- Missing configuration must produce actionable user-facing guidance.
- Failed runs must leave diagnostic metadata.
- Partial output must be clearly marked or avoided.

### 24.2 Maintainability

- Modules must have clear ownership.
- Contracts must be documented.
- Compatibility adapters must be temporary and tracked.
- Generated artifacts must stay out of architecture decisions.

### 24.3 Portability

The platform must support:

- macOS.
- Windows.
- Linux where feasible.
- Local desktop runtime.
- Future server runtime.
- Future cloud runtime.

### 24.4 Observability

The platform must record:

- Run ID.
- Intent route.
- Provider selected.
- Fallback history.
- Knowledge item IDs.
- Output files.
- Duration.
- Errors.
- Policy decisions.

### 24.5 Usability

- Users must understand provider status.
- Users must know where outputs are written.
- Users must receive clean failures.
- Setup must be possible without developer knowledge.

## 25. Security

### 25.1 Secret handling

Secrets include API keys, tokens, enterprise credentials, marketplace
entitlements, and connector credentials.

Rules:

- Never commit secrets.
- Never log secrets.
- Never export secrets into user artifacts.
- Redact secrets in diagnostics.
- Prefer OS credential stores when available.
- Keep local config paths documented.

### 25.2 Plugin security

Plugins are untrusted by default. A plugin must declare:

- File permissions.
- Network permissions.
- Secret access.
- Provider access.
- UI access.
- External command access.

Marketplace plugins must be signed before trusted installation.

### 25.3 Knowledge security

Knowledge packages must carry provenance. Enterprise knowledge must respect
workspace and tenant boundaries.

### 25.4 Provider security

Provider requests may contain sensitive data. Provider policy must support:

- Allowed providers.
- Data sensitivity restrictions.
- Local-only mode.
- No-training preference metadata where provider APIs support it.
- Redaction before logging.

### 25.5 Audit security

Audit logs must be tamper-resistant in enterprise mode and must not store raw
secrets.

## 26. Performance

### 26.1 Performance goals

The platform must keep local workflows responsive:

- GUI remains responsive during generation.
- Provider calls use timeouts.
- Knowledge retrieval avoids unnecessary provider calls.
- Startup loads only required components.
- Plugins load lazily where possible.

### 26.2 Performance budgets

Initial target budgets:

- Runtime startup: under 2 seconds without heavy plugins.
- Local knowledge metadata scan: under 1 second for small repositories.
- Provider config validation: under 500 ms without network checks.
- GUI action feedback: under 100 ms for local state changes.
- Production run diagnostics: available immediately after run completion.

Budgets may be revised with measured benchmarks.

### 26.3 Scaling path

When local data grows, the knowledge architecture may add:

- Persistent indexes.
- Embeddings.
- Incremental indexing.
- Background indexing.
- Cache invalidation.
- Database-backed metadata.

## 27. Offline Strategy

Offline support is a core product capability.

### 27.1 Offline modes

The platform must support:

- Full offline mode with local model and local knowledge.
- Degraded offline mode with templates and knowledge but no model.
- Read-only offline mode for browsing installed knowledge and prior outputs.

### 27.2 Offline provider support

Offline providers include:

- Ollama.
- Future local model runtimes.
- Future embedded inference engines where feasible.

### 27.3 Offline knowledge

Installed knowledge packages must remain accessible without network access.
Marketplace packages that have been downloaded and verified should remain usable
according to their license.

### 27.4 Offline failure rule

If no provider is available offline, the platform must fail cleanly and explain
what is missing. It must not silently create fake AI output.

## 28. Provider Fallback Strategy

Provider fallback must be explicit, observable, and policy-governed.

### 28.1 Fallback inputs

Fallback decisions use:

- User-selected provider.
- Enterprise policy.
- Provider capability.
- Provider availability.
- Cost ceiling.
- Privacy classification.
- Offline requirement.
- Error type.
- Retryability.

### 28.2 Fallback order

Target fallback order:

1. Preferred provider if configured and allowed.
2. Equivalent lower-cost provider if capability matches.
3. Local provider if cloud providers fail or privacy requires local execution.
4. Alternative cloud provider if allowed.
5. Clean `all_providers_failed` style structured error.

The current compatibility `AIManager` order remains until migrated.

### 28.3 No silent downgrade

Fallback must not silently reduce required capability. If a task requires tool
calling, vision, JSON schema, or privacy controls, fallback providers must support
that requirement or the run must fail cleanly.

### 28.4 Fallback metadata

Outputs and run logs must record:

- Initial provider.
- Failed providers.
- Error classes.
- Final provider.
- Whether fallback changed model family.
- Whether user-visible output came from fallback.

## 29. Universal Skill Architecture

Skills are reusable units of work that agents and workflows can execute.

### 29.1 Skill definition

A skill is a declared capability with:

- Skill ID.
- Name.
- Version.
- Description.
- Inputs.
- Outputs.
- Permissions.
- Required provider capabilities.
- Required knowledge domains.
- Execution handler.
- Validation rules.
- Examples.

### 29.2 Skill types

Skill types include:

- Prompt skill.
- Tool skill.
- Export skill.
- Import skill.
- Review skill.
- Analysis skill.
- Planning skill.
- Connector skill.
- UI skill.
- Enterprise admin skill.

### 29.3 Skill execution model

```text
Skill Invocation
├── Validate inputs
├── Check permissions
├── Resolve knowledge
├── Resolve provider
├── Execute handler
├── Validate output
├── Emit events
└── Return structured result
```

### 29.4 Skill packaging

Skills may ship:

- Built into the platform.
- Inside plugins.
- Inside marketplace packages.
- Inside enterprise private catalogs.
- Inside domain knowledge packs.

### 29.5 Skill safety

Skills that write files, send data, call external systems, or trigger factory
actions require explicit permissions and audit logs.

## 30. Future Cloud Architecture

Cloud architecture is future-facing and must not compromise local-first behavior.

### 30.1 Cloud goals

Cloud adds:

- Account identity.
- Workspace sync.
- Managed marketplace.
- Remote execution.
- Team collaboration.
- Centralized audit.
- Enterprise policy.
- Managed provider routing.
- Shared knowledge catalogs.
- Fleet administration.

### 30.2 Cloud topology

```text
Desktop Client
    -> Local PlatformRuntime
    -> Cloud Sync Client
        -> LUCID Cloud API
            -> Identity Service
            -> Workspace Service
            -> Marketplace Service
            -> Provider Routing Service
            -> Job Queue
            -> Audit Service
            -> Knowledge Service
            -> Enterprise Policy Service
```

### 30.3 Hybrid execution

Hybrid execution means:

- Sensitive work can stay local.
- Heavy jobs can run remotely.
- Enterprise policy decides what may leave the device.
- Users can see where execution happened.
- Cloud failure does not break local-only workflows.

### 30.4 Cloud data boundaries

Cloud services must distinguish:

- Account metadata.
- Workspace metadata.
- Knowledge content.
- User artifacts.
- Provider request payloads.
- Audit metadata.
- Billing metadata.

Each class needs retention, encryption, and access rules.

## 31. Architecture Governance

### 31.1 Architecture decision records

Major decisions require an ADR:

```text
docs/architecture/adr/YYYY-MM-DD-short-title.md
```

An ADR must include:

- Context.
- Decision.
- Alternatives considered.
- Consequences.
- Migration impact.
- Test impact.

### 31.2 Scope gates

Before any sprint starts:

- Confirm sprint scope.
- Confirm forbidden files.
- Confirm migration target.
- Confirm test plan.
- Confirm rollback plan.

### 31.3 Definition of done for architecture changes

An architecture change is done only when:

- The master architecture remains consistent.
- Affected docs are updated.
- New contracts have tests or planned test tasks.
- Compatibility impact is stated.
- Release impact is stated.

## 32. Canonical Compatibility Map

The following modules are compatibility surfaces and must be protected during
migration:

| Area | Current Surface | Migration Direction |
| --- | --- | --- |
| Production CLI | `hgpt_ai_os.production` | Wrap behind workflow runtime |
| Desktop GUI | `hgpt_ai_os.gui` | Keep presentation-only, call services |
| Production service | `hgpt_ai_os.gui.production_service` | Route through platform job runtime |
| AI providers | `hgpt_ai_os.ai` | Wrap behind provider runtime |
| Knowledge | `hgpt_ai_os.knowledge`, `hgpt_ai_os.intelligence` | Wrap behind knowledge runtime |
| Content generation | `hgpt_ai_os.content` | Convert to skills/workflows |
| Agents | `hgpt_ai_os.agents`, `hgpt_ai_os.kernel.agent_manager` | Convert to agent runtime |
| Templates | `templates/` and template modules | Convert to template/skill packages |
| Release | build scripts, installer, spec | Keep version and artifact contract centralized |

## 33. Final Architecture Mandate

LUCID PLATFORM must grow by adding stable contracts around proven production
behavior, not by repeatedly rewriting the product core.

The correct direction is:

```text
Protect current production path.
Add platform contracts.
Wrap compatibility modules.
Move callers to contracts.
Test behavior.
Then retire direct legacy paths.
```

Architecture Freeze ends only when this document is accepted as the project
source of truth and the next sprint scope is explicitly opened.
