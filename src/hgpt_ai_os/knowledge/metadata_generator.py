from pathlib import Path
import json


KNOWLEDGE_ROOT = Path("knowledge")
METADATA_ROOT = KNOWLEDGE_ROOT / "metadata"


def build():

    METADATA_ROOT.mkdir(parents=True, exist_ok=True)

    for md in KNOWLEDGE_ROOT.rglob("*.md"):

        if "metadata" in md.parts:
            continue

        rel = md.relative_to(KNOWLEDGE_ROOT)

        category = rel.parts[0]

        kid = md.stem.upper()

        data = {
            "id": kid,
            "title": md.stem.replace("_", " "),
            "category": category,
            "tags": [category.lower()],
            "author": "MaithuyELEC",
            "version": "1.0",
            "status": "active",
            "source_path": rel.as_posix(),
            "related": [],
            "extra": {},
        }

        out = METADATA_ROOT / f"{kid}.json"

        out.write_text(
            json.dumps(data, indent=4, ensure_ascii=False),
            encoding="utf-8",
        )

        print("OK", out.name)


if __name__ == "__main__":
    build()
