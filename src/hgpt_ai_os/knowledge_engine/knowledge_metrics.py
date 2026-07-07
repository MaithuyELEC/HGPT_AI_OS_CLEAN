"""Metrics for package loading, search, and cache behavior."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class KnowledgeMetrics:
    package_count: int = 0
    search_count: int = 0
    hit_count: int = 0
    miss_count: int = 0
    load_time_seconds: float = 0.0
    cache_hit_count: int = 0
    cache_miss_count: int = 0

    def record_packages(self, package_count: int) -> None:
        self.package_count = package_count

    def record_search(self, hit_count: int) -> None:
        self.search_count += 1
        if hit_count:
            self.hit_count += 1
        else:
            self.miss_count += 1

    def record_load_time(self, seconds: float) -> None:
        self.load_time_seconds += max(0.0, seconds)

    def record_cache_hit(self) -> None:
        self.cache_hit_count += 1

    def record_cache_miss(self) -> None:
        self.cache_miss_count += 1

    @property
    def hit_rate(self) -> float:
        total = self.hit_count + self.miss_count
        return 0.0 if total == 0 else self.hit_count / total

    @property
    def cache_hit_rate(self) -> float:
        total = self.cache_hit_count + self.cache_miss_count
        return 0.0 if total == 0 else self.cache_hit_count / total

    def snapshot(self) -> dict[str, float | int]:
        return {
            "package_count": self.package_count,
            "search_count": self.search_count,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": self.hit_rate,
            "load_time_seconds": self.load_time_seconds,
            "cache_hit_count": self.cache_hit_count,
            "cache_miss_count": self.cache_miss_count,
            "cache_hit_rate": self.cache_hit_rate,
        }
