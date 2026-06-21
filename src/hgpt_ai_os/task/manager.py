import json
from pathlib import Path

from .task import Task


class TaskManager:

    def __init__(self, storage_path="data/tasks.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self):
        if not self.storage_path.exists():
            return []

        with open(self.storage_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, tasks):
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)

    def create(self, name: str):
        task = Task.create(name)

        tasks = self._load()
        tasks.append(task.__dict__)
        self._save(tasks)

        return task

    def list(self):
        return [
            Task(**item)
            for item in self._load()
        ]
