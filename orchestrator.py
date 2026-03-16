from __future__ import annotations

from typing import List

from eval_engine.dataset.manager import Task, load_tasks
from eval_engine.generation.stub_generator import StubGenerator
from eval_engine.generation.base import GeneratedSolution
from eval_engine.runner.local_runner import TestRunResult, run_tests_for_solution


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

