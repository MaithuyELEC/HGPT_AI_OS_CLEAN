"""
HGPT AI OS
Builder Engine - Scaffold
"""

from pathlib import Path


class ProjectScaffold:
    """Create standard HGPT project structure."""

    DEFAULT_DIRS = (
        "src",
        "tests",
        "docs",
        "configs",
        "data",
        "logs",
    )

    @classmethod
    def build(cls, root: str) -> Path:
        root_path = Path(root)

        for directory in cls.DEFAULT_DIRS:
            (root_path / directory).mkdir(
                parents=True,
                exist_ok=True,
            )

        return root_path