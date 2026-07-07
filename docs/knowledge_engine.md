# Universal Knowledge Engine

Sprint 06 adds `hgpt_ai_os.knowledge_engine` as a metadata-first foundation for package registration, lifecycle management, discovery, cache, citations, version compatibility, policy, metrics, and search abstraction.

The engine is intentionally independent from GUI, providers, runtime engine, agent core, production workflow, and AI generation. It does not perform HTTP calls, SDK calls, vector database access, embedding generation, or content migration.

## Package Boundary

The package lives at:

`src/hgpt_ai_os/knowledge_engine/`

It is separate from the existing production `hgpt_ai_os.knowledge` package. Current production retrieval remains unchanged.

## Modules

- `knowledge_registry.py`: register, unregister, discover, and inspect package metadata.
- `knowledge_manager.py`: load, enable, disable, refresh, validate, and report health.
- `knowledge_catalog.py`: fixed catalog of required domains.
- `knowledge_package.py`: metadata-only package model and capability metadata.
- `knowledge_loader.py`: package discovery, manifest validation, dependency validation, and version compatibility checks.
- `knowledge_index.py`: abstract search index model with keyword, semantic, and hybrid modes; no vector database or embeddings.
- `knowledge_search.py`: search coordinator that validates package state and delegates to an index.
- `knowledge_cache.py`: session, project, and package cache scopes.
- `knowledge_citation.py`: source ID, package ID, version, reference, and confidence model.
- `knowledge_version.py`: semantic version compatibility and migration support metadata.
- `knowledge_policy.py`: public, private, enterprise, read-only, and experimental policy flags.
- `knowledge_metrics.py`: package count, search count, hit rate, load time, and cache hit tracking.

## Manifest Shape

Knowledge packages are metadata-only in Sprint 06. A manifest can be represented as JSON:

```json
{
  "package_id": "steel-basics",
  "name": "Steel Basics",
  "version": "1.0.0",
  "min_engine_version": "1.0.0",
  "domain": "Steel",
  "capabilities": ["keyword"],
  "dependencies": [],
  "visibility": "enterprise",
  "read_only": true,
  "experimental": false
}
```

`KnowledgeLoader.discover(root)` finds files named `knowledge_manifest.json`. The loader validates the manifest shape, domain, dependencies, and engine compatibility before registration.

## Search Contract

`KnowledgeSearch` accepts a `KnowledgeSearchQuery`, validates enabled package IDs, checks the requested search mode, and delegates to a `KnowledgeIndex`.

`MemoryKnowledgeIndex` provides a deterministic keyword-only implementation for local tests and future integration points. Semantic and hybrid modes are represented as stable enum values, but no AI, embeddings, or vector database behavior is implemented.

## Compatibility

The new engine introduces no changes to existing contracts, providers, runtime engine, agent core, GUI, production workflow, or AI generation. Existing imports continue to compile because Sprint 06 only adds new modules and tests.
