from pathlib import Path


class KnowledgeLoader:

    BASE = Path("knowledge")

    def load(self, relative_path: str) -> str:

        path = self.BASE / relative_path

        if not path.exists():
            return ""

        text = path.read_text(encoding="utf-8")

        lines = []

        for line in text.splitlines():

            if line.strip().startswith("@include"):

                file = line.replace("@include", "").strip()

                include_path = path.parent / file

                if include_path.exists():
                    lines.append(include_path.read_text(encoding="utf-8"))
            else:
                lines.append(line)

        return "\n".join(lines)
