from __future__ import annotations

from typing import Any, TypeVar


T = TypeVar("T")


class PlatformServiceRegistry:
    """Small production registry used by the universal runtime foundation."""

    def __init__(self) -> None:
        self._services: dict[str, Any] = {}

    def register(self, key: str, service: Any) -> None:
        normalized_key = key.strip()
        if not normalized_key:
            raise ValueError("service key must not be empty")
        if normalized_key in self._services:
            raise KeyError(f"service already registered: {normalized_key}")
        self._services[normalized_key] = service

    def get(self, key: str, expected_type: type[T] | None = None) -> T | Any:
        if key not in self._services:
            raise KeyError(f"service not registered: {key}")
        service = self._services[key]
        if expected_type is not None and not isinstance(service, expected_type):
            raise TypeError(
                f"service {key} is {type(service).__name__}, "
                f"expected {expected_type.__name__}"
            )
        return service

    def contains(self, key: str) -> bool:
        return key in self._services

    def keys(self) -> tuple[str, ...]:
        return tuple(sorted(self._services))
