"""Plugin SDK metrics."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PluginMetrics:
    plugin_count: int = 0
    load_time: float = 0.0
    failure_count: int = 0
    enable_count: int = 0
    disable_count: int = 0

    def set_plugin_count(self, value: int) -> None:
        self.plugin_count = value

    def record_load_time(self, seconds: float) -> None:
        self.load_time += seconds

    def record_failure(self) -> None:
        self.failure_count += 1

    def record_enable(self) -> None:
        self.enable_count += 1

    def record_disable(self) -> None:
        self.disable_count += 1

    def snapshot(self) -> dict[str, int | float]:
        return {
            "plugin_count": self.plugin_count,
            "load_time": self.load_time,
            "failure_count": self.failure_count,
            "enable_count": self.enable_count,
            "disable_count": self.disable_count,
        }
