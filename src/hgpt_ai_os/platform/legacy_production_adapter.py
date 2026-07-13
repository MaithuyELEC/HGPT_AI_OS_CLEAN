from __future__ import annotations

from pathlib import Path

from hgpt_ai_os.diagnostics import instrument_runtime_tracing, module_loaded, trace_call


class LegacyProductionAdapter:
    """Platform adapter for the existing production output pipeline."""

    def next_day(self) -> int:
        trace_call("LegacyProductionAdapter.next_day", self)
        from hgpt_ai_os import production

        return production.next_day()

    def execute(
        self,
        day: int,
        topic: str,
        open_output_folder: bool = False,
    ) -> Path:
        trace_call("LegacyProductionAdapter.execute", self, selected_topic=topic)
        from hgpt_ai_os import production

        return production.build_outputs(
            day,
            topic,
            open_output_folder=open_output_folder,
        )


instrument_runtime_tracing(globals())
module_loaded(__name__, __file__, LegacyProductionAdapter)
