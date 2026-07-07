"""Knowledge package discovery and manifest validation."""

from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter
from typing import Any, Mapping

from .knowledge_catalog import KnowledgeCatalog
from .knowledge_package import KnowledgeCapability, KnowledgePackageMetadata
from .knowledge_policy import KnowledgePolicy, KnowledgeVisibility
from .knowledge_registry import KnowledgeRegistry
from .knowledge_version import KnowledgeVersion, VersionCompatibility


class KnowledgeLoader:
    def __init__(
        self,
        catalog: KnowledgeCatalog | None = None,
        *,
        engine_version: str = "1.0.0",
    ) -> None:
        self.catalog = catalog or KnowledgeCatalog()
        self.engine_version = engine_version

    def discover(self, root: str | Path) -> tuple[Path, ...]:
        root_path = Path(root)
        if not root_path.exists():
            return ()
        return tuple(sorted(root_path.rglob("knowledge_manifest.json")))

    def load_manifest_file(self, manifest_path: str | Path) -> KnowledgePackageMetadata:
        with Path(manifest_path).open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, Mapping):
            raise ValueError("knowledge manifest must be an object")
        return self.load_manifest(data)

    def load_manifest(self, manifest: Mapping[str, Any]) -> KnowledgePackageMetadata:
        metadata = self._metadata_from_manifest(manifest)
        errors = self.validate_manifest(metadata)
        if errors:
            raise ValueError(errors[0])
        return metadata

    def validate_manifest(self, metadata: KnowledgePackageMetadata) -> tuple[str, ...]:
        errors = list(metadata.validate(self.catalog))
        compatibility = metadata.version.compatibility_with_engine(self.engine_version)
        if compatibility is VersionCompatibility.INCOMPATIBLE:
            errors.append("knowledge package is not compatible with this engine version")
        return tuple(errors)

    def validate_dependencies(
        self,
        metadata: KnowledgePackageMetadata,
        registry: KnowledgeRegistry,
    ) -> tuple[str, ...]:
        return tuple(
            f"missing dependency: {dependency}"
            for dependency in metadata.dependencies
            if not registry.contains(dependency)
        )

    def load_directory(self, root: str | Path, registry: KnowledgeRegistry) -> tuple[KnowledgePackageMetadata, ...]:
        loaded: list[KnowledgePackageMetadata] = []
        start = perf_counter()
        for manifest_path in self.discover(root):
            metadata = self.load_manifest_file(manifest_path)
            dependency_errors = self.validate_dependencies(metadata, registry)
            if dependency_errors:
                raise ValueError(dependency_errors[0])
            registry.register_package(metadata)
            loaded.append(metadata)
        elapsed = perf_counter() - start
        for metadata in loaded:
            extra = dict(metadata.metadata)
            extra.setdefault("load_time_seconds", elapsed)
        return tuple(loaded)

    def _metadata_from_manifest(self, manifest: Mapping[str, Any]) -> KnowledgePackageMetadata:
        version = KnowledgeVersion.from_strings(
            str(manifest.get("version", "")),
            min_engine_version=str(manifest.get("min_engine_version", "1.0.0")),
            migration_targets=tuple(str(item) for item in manifest.get("migration_targets", ())),
            metadata=manifest.get("version_metadata", {}),
        )
        visibility = KnowledgeVisibility(str(manifest.get("visibility", KnowledgeVisibility.PRIVATE.value)))
        policy = KnowledgePolicy(
            visibility=visibility,
            read_only=bool(manifest.get("read_only", True)),
            experimental=bool(manifest.get("experimental", False)),
        )
        domain = self.catalog.normalize(str(manifest.get("domain", "General")))
        capabilities = tuple(KnowledgeCapability(str(value)) for value in manifest.get("capabilities", ("keyword",)))
        return KnowledgePackageMetadata(
            package_id=str(manifest.get("package_id", "")),
            name=str(manifest.get("name", "")),
            version=version,
            domain=domain,
            capabilities=capabilities,
            dependencies=tuple(str(value) for value in manifest.get("dependencies", ())),
            policy=policy,
            description=str(manifest.get("description", "")),
            metadata=manifest.get("metadata", {}),
        )
