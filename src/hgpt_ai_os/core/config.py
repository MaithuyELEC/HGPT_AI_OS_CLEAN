from dataclasses import dataclass
from pathlib import Path

from .constants import VERSION


@dataclass
class Config:
    version: str
    environment: str
    workspace: Path

    @classmethod
    def load(cls):
        return cls(
            version=VERSION,
            environment="production",
            workspace=Path.cwd(),
        )
