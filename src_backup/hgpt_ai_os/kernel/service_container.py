from typing import Any

from hgpt_ai_os.logger.logger import logger


class ServiceContainer:
    """Dependency Injection Container"""

    def __init__(self):
        self._services = {}

    def register(self, name: str, service: Any):
        self._services[name] = service
        logger.info(f"Service Registered: {name}")

    def resolve(self, name: str):
        service = self._services.get(name)

        if service is None:
            raise ValueError(f"Service '{name}' not found.")

        return service

    def exists(self, name: str) -> bool:
        return name in self._services

    def remove(self, name: str):
        if name in self._services:
            del self._services[name]
            logger.info(f"Service Removed: {name}")

    def list_services(self):
        return list(self._services.keys())

    def clear(self):
        self._services.clear()
        logger.info("All services cleared.")
