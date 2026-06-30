from __future__ import annotations

import time

from hgpt_ai_os.core.production_result import ProductionResult


class ProductionService:
    def __init__(self):
        self.knowledge_count = None
        self.started_at = None

    def run(self, topic: str) -> ProductionResult:
        from hgpt_ai_os import production

        self.started_at = time.perf_counter()
        day = production.next_day()
        output_dir = production.build_outputs(day, topic)
        generated_files = (
            sorted(output_dir.glob("*.docx")) if output_dir.exists() else []
        )

        return ProductionResult(
            success=True,
            output_dir=output_dir,
            generated_files=generated_files,
            knowledge_count=self.knowledge_count,
            elapsed_seconds=self.elapsed_seconds(),
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
        # TODO: Replace capture_metadata() when Production Engine exposes structured metadata.
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
