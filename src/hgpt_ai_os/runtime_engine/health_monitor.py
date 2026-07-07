"""Runtime health monitoring and provider health aggregation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from hgpt_ai_os.contracts.diagnostics_contract import HealthReport

from .runtime_metrics import RuntimeMetrics


@dataclass(frozen=True)
class RuntimeHealth:
    status: str
    report: HealthReport
    provider_reports: tuple[HealthReport, ...] = ()
    execution_statistics: dict[str, int | float] = field(default_factory=dict)
    memory_usage: dict[str, Any] = field(default_factory=dict)


class HealthMonitor:
    """Builds runtime health snapshots without owning provider behavior."""

    def __init__(self, metrics: RuntimeMetrics | None = None) -> None:
        self._metrics = metrics or RuntimeMetrics()
        self._provider_reports: dict[str, HealthReport] = {}
        self._memory_usage: dict[str, Any] = {"tracked": False, "bytes_used": None}

    def update_provider_health(self, provider_id: str, report: HealthReport) -> None:
        if not provider_id.strip():
            raise ValueError("provider_id is required")
        self._provider_reports[provider_id] = report

    def update_memory_usage(self, bytes_used: int | None) -> None:
        if bytes_used is not None and bytes_used < 0:
            raise ValueError("bytes_used cannot be negative")
        self._memory_usage = {"tracked": bytes_used is not None, "bytes_used": bytes_used}

    def snapshot(self) -> RuntimeHealth:
        reports = tuple(self._provider_reports.values())
        provider_ok = all(report.status in {"ok", "ready", "healthy"} for report in reports)
        status = "healthy" if provider_ok else "degraded"
        stats = self._metrics.snapshot()
        report = HealthReport(
            component="runtime_engine",
            status=status,
            metadata={
                "providers": len(reports),
                "execution_statistics": stats,
                "memory_usage": dict(self._memory_usage),
            },
        )
        return RuntimeHealth(status, report, reports, stats, dict(self._memory_usage))
