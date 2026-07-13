from __future__ import annotations

import re
from dataclasses import dataclass

from hgpt_ai_os.diagnostics import instrument_runtime_tracing


@dataclass(frozen=True)
class KnowledgeFact:
    text: str
    score: float


class KnowledgeRanker:
    def rank(self, context: str, keywords: tuple[str, ...], limit: int = 3) -> tuple[KnowledgeFact, ...]:
        if not context.strip():
            return ()

        keyword_set = {word.lower() for word in keywords if len(word) > 2}
        candidates = [
            re.sub(r"\s+", " ", line.strip(" -\t"))
            for line in context.splitlines()
            if line.strip()
        ]
        scored: list[KnowledgeFact] = []
        for line in candidates:
            lowered = line.lower()
            overlap = sum(1 for word in keyword_set if word in lowered)
            if overlap == 0 and scored:
                continue
            if len(line) > 180:
                line = line[:177].rstrip() + "..."
            scored.append(KnowledgeFact(line, min(1.0, 0.25 + overlap * 0.15)))

        scored.sort(key=lambda item: item.score, reverse=True)
        return tuple(scored[: max(0, min(limit, 3))])


instrument_runtime_tracing(globals())
