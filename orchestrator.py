from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple

from dataset.manager import Task, load_tasks
from generation.base import GeneratedSolution
from generation.factory import get_generator
from generation.stub_generator import StubGenerator
from runner.local_runner import TestRunResult, run_tests_for_solution
from runner.docker_runner import DockerRunner
from metrics.engine import (
    TaskMetrics,
    AggregateMetrics,
    compute_task_metrics,
    compute_aggregate,
)


def run_stub(dataset_name: str | None = None) -> List[GeneratedSolution]:
    """Generate solutions using the hardcoded stub (no API key needed)."""
    tasks: List[Task] = load_tasks(dataset_name)
    generator = StubGenerator()
    return [generator.generate(task) for task in tasks]


def run_with_provider(
    provider: str | None = None,
    dataset_name: str | None = None,
) -> List[GeneratedSolution]:
    """
    Generate solutions using any provider (claude, openai, stub).

    Provider is resolved from the argument, then GENERATOR_PROVIDER env var,
    then falls back to 'stub'.
    """
    tasks: List[Task] = load_tasks(dataset_name)
    generator = get_generator(provider)
    return [generator.generate(task) for task in tasks]


def print_stub_summary(dataset_name: str | None = None) -> None:
    results = run_stub(dataset_name)
    for result in results:
        task = result.task
        meta = result.metadata
        print(
            f"[task={task.task_id}] "
            f"model={meta.model_name} "
            f"latency_ms={meta.latency_ms:.2f} "
            f"code_lines={len(result.code.splitlines())}"
        )


def _run_and_evaluate(
    solutions: List[GeneratedSolution],
    use_docker: bool = False,
) -> Tuple[List[TaskMetrics], AggregateMetrics]:
    """Shared logic: run tests (local or Docker) and compute metrics."""
    runner = DockerRunner() if use_docker else None
    paired: list[tuple[GeneratedSolution, TestRunResult]] = []
    for solution in solutions:
        result = runner.run(solution) if runner else run_tests_for_solution(solution)
        paired.append((solution, result))

    meta_and_tests = [(s.metadata, r) for s, r in paired]
    task_metrics = compute_task_metrics(meta_and_tests)
    aggregate = compute_aggregate(task_metrics)
    return task_metrics, aggregate


def run_stub_with_metrics(
    dataset_name: str | None = None,
) -> Tuple[List[TaskMetrics], AggregateMetrics]:
    """Stub generator + local test runner + metrics."""
    return _run_and_evaluate(run_stub(dataset_name), use_docker=False)


def run_docker_with_metrics(
    dataset_name: str | None = None,
) -> Tuple[List[TaskMetrics], AggregateMetrics]:
    """Stub generator + Docker sandbox + metrics."""
    return _run_and_evaluate(run_stub(dataset_name), use_docker=True)


def run_provider_with_metrics(
    provider: str | None = None,
    dataset_name: str | None = None,
    use_docker: bool = False,
) -> Tuple[List[TaskMetrics], AggregateMetrics]:
    """
    Real AI generator + local or Docker runner + metrics.

    Examples:
        run_provider_with_metrics("claude")
        run_provider_with_metrics("openai", use_docker=True)
    """
    solutions = run_with_provider(provider, dataset_name)
    return _run_and_evaluate(solutions, use_docker=use_docker)


@dataclass
class TaskPassRate:
    task_id: str
    runs: int
    passes: int
    pass_rate: float
    failure_types: Dict[str, int]  # e.g. {"logic_error": 2, "none": 8}


@dataclass
class MultiRunReport:
    provider: str
    runs_per_task: int
    task_pass_rates: List[TaskPassRate]
    overall_pass_rate: float


def run_multi(
    provider: str | None = None,
    runs: int = 5,
    dataset_name: str | None = None,
    use_docker: bool = False,
) -> MultiRunReport:
    """
    Run each task N times and compute a pass rate per task.

    This gives statistically meaningful results since models are non-deterministic.

    Example:
        report = run_multi("openai", runs=10)
        for t in report.task_pass_rates:
            print(f"{t.task_id}: {t.pass_rate:.0%} ({t.passes}/{t.runs})")
    """
    tasks = load_tasks(dataset_name)
    generator = get_generator(provider)
    runner = DockerRunner() if use_docker else None

    # task_id -> list of TaskMetrics across all runs
    results_by_task: Dict[str, List[TaskMetrics]] = defaultdict(list)

    for _ in range(runs):
        for task in tasks:
            solution = generator.generate(task)
            test_result = runner.run(solution) if runner else run_tests_for_solution(solution)
            from metrics.engine import compute_task_metrics
            metrics = compute_task_metrics([(solution.metadata, test_result)])
            results_by_task[task.task_id].extend(metrics)

    task_pass_rates: List[TaskPassRate] = []
    total_passes = 0
    total_runs = 0

    for task_id, metrics_list in sorted(results_by_task.items()):
        passes = sum(1 for m in metrics_list if m.passed)
        failure_types: Dict[str, int] = defaultdict(int)
        for m in metrics_list:
            failure_types[m.failure_type] += 1

        task_pass_rates.append(TaskPassRate(
            task_id=task_id,
            runs=len(metrics_list),
            passes=passes,
            pass_rate=passes / len(metrics_list),
            failure_types=dict(failure_types),
        ))
        total_passes += passes
        total_runs += len(metrics_list)

    resolved_provider = provider or "stub"
    return MultiRunReport(
        provider=resolved_provider,
        runs_per_task=runs,
        task_pass_rates=task_pass_rates,
        overall_pass_rate=total_passes / total_runs if total_runs else 0.0,
    )