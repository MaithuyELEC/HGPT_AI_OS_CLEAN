from hgpt_ai_os.database.engine import DatabaseEngine
from hgpt_ai_os.queue import TaskQueue
from hgpt_ai_os.version import APP_RELEASE


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
        return f"HGPT AI OS Runtime {APP_RELEASE}"
