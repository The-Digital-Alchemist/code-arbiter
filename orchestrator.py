from __future__ import annotations

from typing import List, Tuple

from dataset.manager import Task, load_tasks
from generation.stub_generator import StubGenerator
from generation.base import GeneratedSolution
from runner.local_runner import TestRunResult, run_tests_for_solution
from metrics.engine import (
    TaskMetrics,
    AggregateMetrics,
    compute_task_metrics,
    compute_aggregate,
)


def run_stub(dataset_name: str | None = None) -> List[GeneratedSolution]:
    """
    High-level convenience function used during early development.

    It loads all tasks from the dataset manager and runs the stub generator
    for each, returning the list of GeneratedSolution objects.
    """
    tasks: List[Task] = load_tasks(dataset_name)
    generator = StubGenerator()

    results: List[GeneratedSolution] = []
    for task in tasks:
        result = generator.generate(task)
        results.append(result)

    return results


def print_stub_summary(dataset_name: str | None = None) -> None:
    """
    Convenience helper that prints a human-readable summary of stub runs.
    """
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


def run_stub_with_tests(dataset_name: str | None = None) -> list[TestRunResult]:
    """
    Run stub generation and execute the associated pytest tests locally.
    """
    solutions = run_stub(dataset_name)
    results: list[TestRunResult] = []
    for solution in solutions:
        results.append(run_tests_for_solution(solution))
    return results


def run_stub_with_metrics(
    dataset_name: str | None = None,
) -> Tuple[List[TaskMetrics], AggregateMetrics]:
    """
    Run stub generation, execute tests, and compute per-task and aggregate metrics.
    """
    solutions = run_stub(dataset_name)
    test_results: list[TestRunResult] = []
    paired: list[tuple[GeneratedSolution, TestRunResult]] = []
    for solution in solutions:
        result = run_tests_for_solution(solution)
        test_results.append(result)
        paired.append((solution, result))

    # Pair metadata with test results for metrics computation.
    meta_and_tests = [(s.metadata, r) for s, r in paired]
    task_metrics = compute_task_metrics(meta_and_tests)
    aggregate = compute_aggregate(task_metrics)
    return task_metrics, aggregate

