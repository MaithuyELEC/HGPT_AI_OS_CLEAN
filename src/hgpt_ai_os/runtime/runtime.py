from hgpt_ai_os.database.engine import DatabaseEngine
from hgpt_ai_os.queue import TaskQueue


class Runtime:

    def __init__(self):
        self.database = DatabaseEngine()
        self.queue = TaskQueue()

    def status(self):
        return {
            "database": "READY",
            "queue": "READY",
            "runtime": "READY"
        }

    def version(self):
        return "HGPT AI OS Runtime v0.4.0"