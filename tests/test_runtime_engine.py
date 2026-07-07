from __future__ import annotations

import unittest

from hgpt_ai_os.contracts.diagnostics_contract import HealthReport
from hgpt_ai_os.runtime_engine import (
    EventBus,
    IllegalTransitionError,
    JobLifecycleState,
    LifecycleManager,
    RetryManager,
    RetryPolicy,
    RuntimeEngine,
    RuntimeEventType,
    RuntimeLifecycleState,
    RuntimeMetrics,
    StateMachine,
    TaskScheduler,
    TaskStatus,
)
from hgpt_ai_os.runtime_engine.job_manager import JOB_TRANSITIONS, JobManager


class RuntimeLifecycleTests(unittest.TestCase):
    def test_runtime_lifecycle_happy_path(self):
        engine = RuntimeEngine()

        self.assertEqual(engine.initialize(), RuntimeLifecycleState.INITIALIZED)
        self.assertEqual(engine.start(), RuntimeLifecycleState.RUNNING)
        self.assertEqual(engine.pause(), RuntimeLifecycleState.PAUSED)
        self.assertEqual(engine.resume(), RuntimeLifecycleState.RUNNING)
        self.assertEqual(engine.shutdown(), RuntimeLifecycleState.SHUTDOWN)
        self.assertEqual(engine.dispose(), RuntimeLifecycleState.DISPOSED)

    def test_lifecycle_rejects_illegal_transition(self):
        lifecycle = LifecycleManager()

        with self.assertRaises(IllegalTransitionError):
            lifecycle.start()


class JobStateTests(unittest.TestCase):
    def test_job_lifecycle_states(self):
        manager = JobManager()
        job = manager.create("job-1")

        self.assertEqual(job.state, JobLifecycleState.QUEUED)
        self.assertEqual(manager.transition("job-1", JobLifecycleState.RUNNING).state, JobLifecycleState.RUNNING)
        self.assertEqual(manager.transition("job-1", JobLifecycleState.WAITING).state, JobLifecycleState.WAITING)
        self.assertEqual(manager.transition("job-1", JobLifecycleState.RUNNING).state, JobLifecycleState.RUNNING)
        self.assertEqual(manager.transition("job-1", JobLifecycleState.COMPLETED).state, JobLifecycleState.COMPLETED)

    def test_job_terminal_state_rejects_changes(self):
        manager = JobManager()
        manager.create("job-2")
        manager.cancel("job-2")

        with self.assertRaises(IllegalTransitionError):
            manager.transition("job-2", JobLifecycleState.RUNNING)


class StateMachineTests(unittest.TestCase):
    def test_formal_job_transition_rules(self):
        machine = StateMachine(JobLifecycleState.QUEUED, JOB_TRANSITIONS)

        self.assertTrue(machine.can_transition(JobLifecycleState.RUNNING))
        self.assertFalse(machine.can_transition(JobLifecycleState.COMPLETED))
        with self.assertRaises(IllegalTransitionError):
            machine.transition(JobLifecycleState.COMPLETED)


class RetryTests(unittest.TestCase):
    def test_retry_policy_calculates_exponential_backoff(self):
        manager = RetryManager(RetryPolicy(max_attempts=4, base_delay_seconds=0.5, multiplier=3, max_delay_seconds=2))

        first = manager.evaluate(1, "try again")
        second = manager.evaluate(2)
        final = manager.evaluate(4)

        self.assertTrue(first.should_retry)
        self.assertEqual(first.attempt, 2)
        self.assertEqual(first.delay_seconds, 0.5)
        self.assertEqual(second.delay_seconds, 1.5)
        self.assertFalse(final.should_retry)


class SchedulerTests(unittest.TestCase):
    def test_scheduler_runs_dependencies_before_dependents_and_uses_priority(self):
        events: list[str] = []
        scheduler = TaskScheduler()
        scheduler.add_task("base", lambda: events.append("base"))
        scheduler.add_task("low", lambda: events.append("low"), dependencies=("base",), priority=1)
        scheduler.add_task("high", lambda: events.append("high"), dependencies=("base",), priority=10)

        scheduler.run_all()

        self.assertEqual(events, ["base", "high", "low"])
        self.assertTrue(all(task.status is TaskStatus.COMPLETED for task in scheduler.tasks()))

    def test_scheduler_cancels_pending_task(self):
        scheduler = TaskScheduler()
        task = scheduler.add_task("skip", lambda: None)

        scheduler.cancel_task("skip")

        self.assertEqual(task.status, TaskStatus.CANCELLED)
        self.assertIsNone(scheduler.run_next())


class EventBusTests(unittest.TestCase):
    def test_event_bus_publishes_to_subscribers_and_retains_history(self):
        bus = EventBus()
        seen: list[str] = []
        bus.subscribe(RuntimeEventType.JOB, lambda event: seen.append(event.payload["job_id"]))

        bus.emit(RuntimeEventType.JOB, "test", {"job_id": "job-1"})

        self.assertEqual(seen, ["job-1"])
        self.assertEqual(len(bus.history(RuntimeEventType.JOB)), 1)


class MetricsTests(unittest.TestCase):
    def test_metrics_counts_execution_results_and_retries(self):
        metrics = RuntimeMetrics()
        metrics.record_execution()
        metrics.record_success()
        metrics.record_failure()
        metrics.record_retry()

        snapshot = metrics.snapshot()

        self.assertEqual(snapshot["execution_count"], 1)
        self.assertEqual(snapshot["success_count"], 1)
        self.assertEqual(snapshot["failure_count"], 1)
        self.assertEqual(snapshot["retry_count"], 1)


class HealthMonitorTests(unittest.TestCase):
    def test_runtime_health_includes_provider_reports_and_statistics(self):
        engine = RuntimeEngine()
        engine.submit_job("job-health")
        engine.start_job("job-health")
        engine.complete_job("job-health")
        engine.health_monitor.update_provider_health("provider-1", HealthReport(component="provider-1", status="ready"))

        health = engine.health()

        self.assertEqual(health.status, "healthy")
        self.assertEqual(len(health.provider_reports), 1)
        self.assertEqual(health.execution_statistics["execution_count"], 1)
        self.assertEqual(health.execution_statistics["success_count"], 1)
        self.assertEqual(health.memory_usage["tracked"], False)


if __name__ == "__main__":
    unittest.main()
