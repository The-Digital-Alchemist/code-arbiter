from __future__ import annotations

from typing import List, Tuple

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