from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from hgpt_ai_os.core.production_result import ProductionResult
from hgpt_ai_os.diagnostics import instrument_runtime_tracing, module_loaded, trace_call
from hgpt_ai_os.version import APP_VERSION

from .interfaces import Lifecycle, RuntimeContext
from .legacy_production_adapter import LegacyProductionAdapter
from .registry import PlatformServiceRegistry


LEGACY_PRODUCTION_SERVICE_KEY = "legacy.production"


@dataclass(frozen=True)
class RuntimeSettings:
    """Configuration for the additive LUCID PLATFORM runtime."""

    app_name: str = "LUCID PLATFORM"
    environment: str = "production"
    workspace: Path = field(default_factory=Path.cwd)
    version: str = APP_VERSION
    metadata: dict[str, Any] = field(default_factory=dict)

    def context(self) -> RuntimeContext:
        return RuntimeContext(
            app_name=self.app_name,
            environment=self.environment,
            workspace=self.workspace,
            version=self.version,
            metadata=dict(self.metadata),
        )


class PlatformRuntime:
    """Universal runtime foundation for future LUCID PLATFORM sprints."""

    def __init__(
        self,
        settings: RuntimeSettings | None = None,
        registry: PlatformServiceRegistry | None = None,
    ) -> None:
        self.settings = settings or RuntimeSettings()
        self.registry = registry or PlatformServiceRegistry()
        self._components: list[Lifecycle] = []
        self._running = False
        self._register_default_services()

    @property
    def context(self) -> RuntimeContext:
        return self.settings.context()

    @property
    def running(self) -> bool:
        return self._running

    def add_component(self, component: Lifecycle) -> None:
        if self._running:
            raise RuntimeError("components cannot be added after runtime start")
        self._components.append(component)

    def start(self) -> None:
        if self._running:
            return
        started: list[Lifecycle] = []
        try:
            for component in self._components:
                component.start()
                started.append(component)
        except Exception:
            for component in reversed(started):
                component.stop()
            raise
        self._running = True

    def stop(self) -> None:
        if not self._running:
            return
        first_error: Exception | None = None
        for component in reversed(self._components):
            try:
                component.stop()
            except Exception as exc:
                if first_error is None:
                    first_error = exc
        self._running = False
        if first_error is not None:
            raise first_error

    def status(self) -> dict[str, Any]:
        return {
            "app_name": self.settings.app_name,
            "environment": self.settings.environment,
            "workspace": str(self.settings.workspace),
            "version": self.settings.version,
            "running": self._running,
            "components": len(self._components),
            "services": list(self.registry.keys()),
        }

    def execute(
        self,
        topic: str,
        open_output_folder: bool = False,
        knowledge_count_provider: Callable[[], int | None] | None = None,
        started_at: float | None = None,
    ) -> ProductionResult:
        trace_call("PlatformRuntime.execute", self, selected_topic=topic)
        adapter = self.registry.get(
            LEGACY_PRODUCTION_SERVICE_KEY,
            LegacyProductionAdapter,
        )
        output_dir = adapter.execute(
            adapter.next_day(),
            topic,
            open_output_folder=open_output_folder,
        )
        generated_files = (
            sorted(output_dir.glob("*.docx")) if output_dir.exists() else []
        )
        knowledge_count = None
        if knowledge_count_provider is not None:
            knowledge_count = knowledge_count_provider()
        elapsed_seconds = (
            time.perf_counter() - started_at if started_at is not None else None
        )

        return ProductionResult(
            success=True,
            output_dir=output_dir,
            generated_files=generated_files,
            knowledge_count=knowledge_count,
            elapsed_seconds=elapsed_seconds,
        )

    def _register_default_services(self) -> None:
        if not self.registry.contains(LEGACY_PRODUCTION_SERVICE_KEY):
            self.registry.register(
                LEGACY_PRODUCTION_SERVICE_KEY,
                LegacyProductionAdapter(),
            )


instrument_runtime_tracing(globals())
module_loaded(__name__, __file__, PlatformRuntime)
