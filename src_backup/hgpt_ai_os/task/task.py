from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4


@dataclass
class Task:
    id: str
    name: str
    status: str
    created_at: str

    @classmethod
    def create(cls, name: str):
        return cls(
            id=str(uuid4()),
            name=name,
            status="PENDING",
            created_at=datetime.now().isoformat()
        )