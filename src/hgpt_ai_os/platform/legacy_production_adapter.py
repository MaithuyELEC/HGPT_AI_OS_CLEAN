from __future__ import annotations

from pathlib import Path


class LegacyProductionAdapter:
    """Platform adapter for the existing production output pipeline."""

    def next_day(self) -> int:
        from hgpt_ai_os import production

        return production.next_day()

    def execute(
        self,
        day: int,
        topic: str,
        open_output_folder: bool = False,
    ) -> Path:
        from hgpt_ai_os import production

        return production.build_outputs(
            day,
            topic,
            open_output_folder=open_output_folder,
        )
