from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProductionResult:
    success: bool
    output_dir: Path | None
    generated_files: list[Path]
    knowledge_count: int | None
    elapsed_seconds: float | None
