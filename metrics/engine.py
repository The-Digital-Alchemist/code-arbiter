from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Iterable, List

from eval_engine.generation.base import GenerationMetadata
from eval_engine.runner.local_runner import TestRunResult


@dataclass(frozen=True)
class TaskMetrics:
    task_id: str
    model_name: str
    passed: bool
    latency_ms: float
    exit_code: int


@dataclass(frozen=True)
class AggregateMetrics:
    total_tasks: int
    passed_tasks: int
    pass_rate: float
    average_latency_ms: float | None


def compute_task_metrics(
    results: Iterable[tuple[GenerationMetadata, TestRunResult]]
) -> List[TaskMetrics]:
    """
    Zip together generation metadata and test run results into per-task metrics.
    """
    metrics: List[TaskMetrics] = []
    for meta, test in results:
        metrics.append(
            TaskMetrics(
                task_id=test.task_id,
                model_name=meta.model_name,
                passed=test.passed,
                latency_ms=meta.latency_ms,
                exit_code=test.exit_code,
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
    pass_rate = passed_tasks / total
    average_latency = mean(m.latency_ms for m in metrics_list)

    return AggregateMetrics(
        total_tasks=total,
        passed_tasks=passed_tasks,
        pass_rate=pass_rate,
        average_latency_ms=average_latency,
    )

