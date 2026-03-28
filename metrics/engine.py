from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Iterable, List

from generation.base import GenerationMetadata, GeneratedSolution
from runner.local_runner import TestRunResult


@dataclass(frozen=True)
class TaskMetrics:
    task_id: str
    model_name: str
    status: str          # "PASS" or "FAIL"
    tests_passed: int
    tests_failed: int
    failed_tests: List[str]
    latency_ms: float
    exit_code: int
    failure_type: str = "none"
    generated_code: str = ""
    test_output: str = ""

    @property
    def passed(self) -> bool:
        return self.status == "PASS"


@dataclass(frozen=True)
class AggregateMetrics:
    total_tasks: int
    passed_tasks: int
    pass_rate: float
    average_latency_ms: float | None


def compute_task_metrics(
    results: Iterable[tuple[GeneratedSolution, TestRunResult]]
) -> List[TaskMetrics]:
    metrics: List[TaskMetrics] = []
    for solution, test in results:
        meta = solution.metadata
        metrics.append(
            TaskMetrics(
                task_id=test.task_id,
                model_name=meta.model_name,
                status="PASS" if test.passed else "FAIL",
                tests_passed=test.tests_passed,
                tests_failed=test.tests_failed,
                failed_tests=list(test.failed_tests),
                latency_ms=meta.latency_ms,
                exit_code=test.exit_code,
                failure_type=test.failure_type,
                generated_code=solution.code,
                test_output=test.stdout + test.stderr,
            )
        )
    return metrics


def compute_aggregate(metrics: Iterable[TaskMetrics]) -> AggregateMetrics:
    metrics_list = list(metrics)
    total = len(metrics_list)
    if total == 0:
        return AggregateMetrics(
            total_tasks=0,
            passed_tasks=0,
            pass_rate=0.0,
            average_latency_ms=None,
        )

    passed_tasks = sum(1 for m in metrics_list if m.passed)
    return AggregateMetrics(
        total_tasks=total,
        passed_tasks=passed_tasks,
        pass_rate=passed_tasks / total,
        average_latency_ms=mean(m.latency_ms for m in metrics_list),
    )