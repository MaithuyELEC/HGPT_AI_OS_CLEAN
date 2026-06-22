from __future__ import annotations

import json
from pathlib import Path

from .models import KnowledgeMetadata


def load_metadata(metadata_file: Path) -> KnowledgeMetadata:
    """Load metadata from a JSON file."""

    data = json.loads(metadata_file.read_text(encoding="utf-8"))

    return KnowledgeMetadata(
        id=data["id"],
        title=data["title"],
        category=data["category"],
        tags=data.get("tags", []),
        author=data.get("author", "MaithuyELEC"),
        version=data.get("version", "1.0"),
        status=data.get("status", "draft"),
        source_path=data.get("source_path"),
        related=data.get("related", []),
        extra=data.get("extra", {}),
    )


def load_markdown(markdown_file: Path) -> str:
    """Load markdown content."""

    return markdown_file.read_text(encoding="utf-8")
