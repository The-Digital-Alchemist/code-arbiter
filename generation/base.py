from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from dataset.manager import Task


@dataclass(frozen=True)
class GenerationMetadata:
    """Lightweight metadata about a code generation call."""

    model_name: str
    latency_ms: float
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


@dataclass(frozen=True)
class GeneratedSolution:
    """Result of a generation request for a single task."""

    task: Task
    code: str
    metadata: GenerationMetadata


def build_prompt(task: Task) -> str:
    """
    Construct the prompt sent to a generator.

    If the task has a solution_template, the model is asked to complete it.
    This keeps the description natural (no leaked function names) while still
    giving the model the correct signature to implement.
    """
    if task.solution_template:
        return (
            f"{task.description}\n\n"
            f"Complete the following Python template. "
            f"Return only the completed code, no explanation:\n\n"
            f"{task.solution_template}"
        )
    return f"{task.description}\n\nReturn only the code, no explanation."


class BaseGenerator(Protocol):
    """Abstract interface for all code generators (LLMs, agents, stubs)."""

    def generate(self, task: Task) -> GeneratedSolution:
        """Generate code implementing the given task."""
        ...

