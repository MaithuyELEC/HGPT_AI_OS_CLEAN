from typing import Any

from hgpt_ai_os.logger.logger import logger


class Registry:
    """Central Registry for HGPT AI OS"""

    def __init__(self):
        self._items = {}

    def register(self, category: str, name: str, item: Any):
        self._items.setdefault(category, {})
        self._items[category][name] = item
        logger.info(f"[{category}] Registered: {name}")

    def get(self, category: str, name: str):
        return self._items.get(category, {}).get(name)

    def list(self, category: str):
        return list(self._items.get(category, {}).keys())

    def remove(self, category: str, name: str):
        if category in self._items and name in self._items[category]:
            del self._items[category][name]
            logger.info(f"[{category}] Removed: {name}")

    def categories(self):
        return list(self._items.keys())

    def clear(self):
        self._items.clear()
        logger.info("Registry cleared.")
