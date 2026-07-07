from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from hgpt_ai_os.knowledge_engine import (
    CacheScope,
    KnowledgeCache,
    KnowledgeCapability,
    KnowledgeCatalog,
    KnowledgeCitation,
    KnowledgeDomain,
    KnowledgeLoader,
    KnowledgeManager,
    KnowledgeMetrics,
    KnowledgePackageMetadata,
    KnowledgePolicy,
    KnowledgeRegistry,
    KnowledgeSearch,
    KnowledgeSearchQuery,
    KnowledgeVisibility,
    KnowledgeVersion,
    MemoryKnowledgeIndex,
    SearchMode,
    SemanticVersion,
    VersionCompatibility,
)
from hgpt_ai_os.knowledge_engine.knowledge_index import KnowledgeIndexEntry


def package(package_id: str = "steel-basics") -> KnowledgePackageMetadata:
    return KnowledgePackageMetadata(
        package_id=package_id,
        name="Steel Basics",
        version=KnowledgeVersion.from_strings("1.2.0"),
        domain=KnowledgeDomain.STEEL,
        capabilities=(KnowledgeCapability.KEYWORD, KnowledgeCapability.HYBRID),
        policy=KnowledgePolicy(KnowledgeVisibility.ENTERPRISE),
    )


class KnowledgeRegistryTests(unittest.TestCase):
    def test_register_unregister_discover_and_metadata(self):
        registry = KnowledgeRegistry()
        metadata = package()

        registry.register_package(metadata)

        self.assertTrue(registry.contains("steel-basics"))
        self.assertEqual(registry.metadata("steel-basics"), metadata)
        self.assertEqual(registry.package_ids(), ("steel-basics",))
        self.assertEqual(registry.version_metadata("steel-basics")["version"], "1.2.0")
        self.assertEqual(
            registry.capability_metadata("steel-basics"),
            (KnowledgeCapability.KEYWORD, KnowledgeCapability.HYBRID),
        )
        self.assertEqual(registry.discover_package(KnowledgeCapability.HYBRID), (metadata,))
        self.assertEqual(registry.discover_package(domain=KnowledgeDomain.STEEL), (metadata,))
        self.assertEqual(registry.unregister_package("steel-basics").metadata, metadata)
        self.assertFalse(registry.contains("steel-basics"))

    def test_rejects_duplicate_package_ids(self):
        registry = KnowledgeRegistry()
        registry.register_package(package())

        with self.assertRaises(KeyError):
            registry.register_package(package())


class KnowledgeCatalogTests(unittest.TestCase):
    def test_catalog_contains_all_required_domains(self):
        catalog = KnowledgeCatalog()

        self.assertEqual(len(catalog.names()), 21)
        self.assertTrue(catalog.contains("Engineering"))
        self.assertTrue(catalog.contains("DigitalFactory"))
        self.assertEqual(catalog.normalize("5s"), KnowledgeDomain.FIVE_S)


class KnowledgeLoaderTests(unittest.TestCase):
    def test_manifest_validation_dependencies_and_discovery(self):
        loader = KnowledgeLoader()
        registry = KnowledgeRegistry()
        base = package("base")
        registry.register_package(base)
        manifest = {
            "package_id": "steel-advanced",
            "name": "Steel Advanced",
            "version": "1.0.0",
            "domain": "Steel",
            "capabilities": ["keyword"],
            "dependencies": ["base"],
            "visibility": "enterprise",
            "read_only": True,
            "experimental": False,
        }

        metadata = loader.load_manifest(manifest)

        self.assertEqual(metadata.package_id, "steel-advanced")
        self.assertEqual(loader.validate_dependencies(metadata, registry), ())
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "pkg" / "knowledge_manifest.json"
            path.parent.mkdir()
            path.write_text(json.dumps(manifest), encoding="utf-8")

            self.assertEqual(loader.discover(temp_dir), (path,))
            self.assertEqual(loader.load_manifest_file(path).package_id, "steel-advanced")

    def test_rejects_incompatible_manifest(self):
        loader = KnowledgeLoader(engine_version="1.0.0")

        with self.assertRaises(ValueError):
            loader.load_manifest(
                {
                    "package_id": "future",
                    "name": "Future",
                    "version": "2.0.0",
                    "min_engine_version": "2.0.0",
                }
            )


class KnowledgeVersionTests(unittest.TestCase):
    def test_semantic_version_compatibility_and_migration_support(self):
        version = KnowledgeVersion.from_strings(
            "1.1.0",
            min_engine_version="1.0.0",
            migration_targets=("2.0.0",),
        )

        self.assertEqual(str(SemanticVersion.parse("1.2.3")), "1.2.3")
        self.assertEqual(version.compatibility_with_engine("1.3.0"), VersionCompatibility.COMPATIBLE)
        self.assertEqual(version.compatibility_with_engine("2.0.0"), VersionCompatibility.MIGRATION_AVAILABLE)
        self.assertEqual(version.compatibility_with_engine("0.9.0"), VersionCompatibility.INCOMPATIBLE)
        self.assertTrue(version.migration_supported("2.0.0"))


class KnowledgeCitationPolicyCacheTests(unittest.TestCase):
    def test_citation_policy_and_cache_contracts(self):
        citation = KnowledgeCitation(
            source_id="src-1",
            package_id="steel-basics",
            version="1.0.0",
            reference="manual:12",
            confidence=0.75,
        )
        policy = KnowledgePolicy(KnowledgeVisibility.PRIVATE, read_only=True, experimental=True)
        metrics = KnowledgeMetrics()
        cache = KnowledgeCache(metrics)

        cache.set(CacheScope.SESSION, "run-1", "topic", "steel")

        self.assertEqual(citation.validate(), ())
        self.assertEqual(citation.as_dict()["confidence"], 0.75)
        self.assertTrue(policy.can_read(KnowledgeVisibility.ENTERPRISE))
        self.assertFalse(policy.can_write())
        self.assertEqual(policy.flags(), ("private", "read_only", "experimental"))
        self.assertEqual(cache.get(CacheScope.SESSION, "run-1", "topic"), "steel")
        self.assertEqual(cache.get(CacheScope.PROJECT, "missing", "topic", "none"), "none")
        self.assertEqual(metrics.cache_hit_count, 1)
        self.assertEqual(metrics.cache_miss_count, 1)


class KnowledgeSearchMetricsManagerTests(unittest.TestCase):
    def test_search_abstraction_manager_health_and_metrics(self):
        registry = KnowledgeRegistry()
        manager = KnowledgeManager(registry=registry)
        manager.load_package(package())
        manager.enable("steel-basics")
        index = MemoryKnowledgeIndex()
        citation = KnowledgeCitation("src-1", "steel-basics", "1.2.0", "line:1")
        index.add(KnowledgeIndexEntry("entry-1", "steel-basics", "steel rolling maintenance", (citation,)))
        search = KnowledgeSearch(registry, index, manager.metrics)

        results = search.search(KnowledgeSearchQuery("steel maintenance", ("steel-basics",), SearchMode.KEYWORD))
        health = manager.health()

        self.assertEqual(len(results), 1)
        self.assertGreater(results[0].score, 0)
        self.assertEqual(health.status.value, "ready")
        self.assertEqual(health.package_count, 1)
        self.assertEqual(health.enabled_count, 1)
        self.assertEqual(manager.metrics.snapshot()["search_count"], 1)
        self.assertEqual(manager.metrics.snapshot()["hit_rate"], 1.0)

    def test_disabled_package_and_future_modes_are_safe_abstractions(self):
        registry = KnowledgeRegistry()
        registry.register_package(package())
        index = MemoryKnowledgeIndex()
        search = KnowledgeSearch(registry, index)

        with self.assertRaises(ValueError):
            search.search(KnowledgeSearchQuery("steel", ("steel-basics",), SearchMode.KEYWORD))

        registry.set_enabled("steel-basics", True)
        self.assertEqual(search.search(KnowledgeSearchQuery("steel", ("steel-basics",), SearchMode.SEMANTIC)), ())


if __name__ == "__main__":
    unittest.main()
