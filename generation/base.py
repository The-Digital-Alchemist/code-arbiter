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


class BaseGenerator(Protocol):
    """Abstract interface for all code generators (LLMs, agents, stubs)."""

    def generate(self, task: Task) -> GeneratedSolution:
        """Generate code implementing the given task."""
        ...

