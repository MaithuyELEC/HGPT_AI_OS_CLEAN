from pathlib import Path


class CaseLoader:

    def load(self, case_id: str) -> str:
        path = Path("knowledge/cases") / f"{case_id}.md"

        if not path.exists():
            return ""

        return path.read_text(encoding="utf-8")
