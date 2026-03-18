from __future__ import annotations

from typing import Protocol

from generation.base import GeneratedSolution
from runner.local_runner import TestRunResult


class BaseRunner(Protocol):
    """Abstract interface for all test runners (local, Docker, etc.)."""

    def run(self, solution: GeneratedSolution) -> TestRunResult:
        """Execute tests for the given solution and return results."""
        ...
