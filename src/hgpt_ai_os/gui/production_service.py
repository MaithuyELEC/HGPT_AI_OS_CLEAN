from __future__ import annotations

import time

from hgpt_ai_os.core.production_result import ProductionResult
from hgpt_ai_os.diagnostics import instrument_runtime_tracing, module_loaded, trace_call
from hgpt_ai_os.platform import PlatformRuntime


class ProductionService:
    def __init__(self, runtime: PlatformRuntime | None = None):
        self.runtime = runtime or PlatformRuntime()
        self.knowledge_count = None
        self.started_at = None

    def run(self, topic: str) -> ProductionResult:
        trace_call("Controller -> ProductionService", self, selected_topic=topic)
        self.started_at = time.perf_counter()
        return self.runtime.execute(
            topic,
            open_output_folder=False,
            knowledge_count_provider=lambda: self.knowledge_count,
            started_at=self.started_at,
        )

    def failed_result(self) -> ProductionResult:
        return ProductionResult(
            success=False,
            output_dir=None,
            generated_files=[],
            knowledge_count=self.knowledge_count,
            elapsed_seconds=self.elapsed_seconds(),
        )

    def capture_metadata(self, line: str):
        if not line.startswith("Knowledge :"):
            return

        value = line.split(":", 1)[1].strip().split(" ", 1)[0]

        try:
            self.knowledge_count = int(value)
        except ValueError:
            self.knowledge_count = None

    def elapsed_seconds(self):
        if self.started_at is None:
            return None

        return time.perf_counter() - self.started_at


instrument_runtime_tracing(globals())
module_loaded(__name__, __file__, ProductionService)
