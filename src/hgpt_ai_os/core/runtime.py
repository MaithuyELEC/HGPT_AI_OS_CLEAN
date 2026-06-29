from .config import Config
from .registry import Registry
from .events import EventBus


class Runtime:

    def __init__(self):
        self.config = Config.load()
        self.registry = Registry()
        self.events = EventBus()
        self._running = False

    def start(self):
        self._running = True

    def stop(self):
        self._running = False

    def status(self):
        return {
            "version": self.config.version,
            "environment": self.config.environment,
            "running": self._running,
            "agents": len(self.registry.agents),
            "workflows": len(self.registry.workflows),
        }
