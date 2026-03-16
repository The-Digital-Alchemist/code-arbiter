from __future__ import annotations

import textwrap
import time
from typing import Dict

from eval_engine.dataset.manager import Task
from eval_engine.generation.base import BaseGenerator, GeneratedSolution, GenerationMetadata


_STUB_IMPLEMENTATIONS: Dict[str, str] = {
    "lru_cache": textwrap.dedent(
        """
        from collections import OrderedDict


        class LRUCache:
            def __init__(self, capacity: int):
                self._capacity = capacity
                self._data = OrderedDict()

            def get(self, key: int) -> int:
                if key not in self._data:
                    return -1
                value = self._data.pop(key)
                self._data[key] = value
                return value

            def put(self, key: int, value: int) -> None:
                if key in self._data:
                    self._data.pop(key)
                elif len(self._data) >= self._capacity:
                    self._data.popitem(last=False)
                self._data[key] = value
        """
    ).strip(),
    "fibonacci_iterative": textwrap.dedent(
        """
        def fib(n: int) -> int:
            if n < 0:
                raise ValueError("n must be non-negative")
            if n < 2:
                return n
            a, b = 0, 1
            for _ in range(2, n + 1):
                a, b = b, a + b
            return b
        """
    ).strip(),
    "two_sum": textwrap.dedent(
        """
        from typing import List


        def two_sum(nums: List[int], target: int) -> tuple[int, int] | None:
            seen = {}
            for i, value in enumerate(nums):
                need = target - value
                if need in seen:
                    return seen[need], i
                seen[value] = i
            return None
        """
    ).strip(),
}


class StubGenerator(BaseGenerator):
    """
    Deterministic in-process generator used for development and tests.

    It pretends to be a model by:
    - looking up a canned implementation for a given task_id
    - sleeping briefly to simulate latency
    - returning basic GenerationMetadata
    """

    def __init__(self, model_name: str = "stub-model"):
        self._model_name = model_name

    def generate(self, task: Task) -> GeneratedSolution:
        start = time.perf_counter()
        code = _STUB_IMPLEMENTATIONS.get(task.task_id) or self._fallback_implementation(task)
        latency_ms = (time.perf_counter() - start) * 1000.0

        # For a real model these would come from API usage data; here we
        # just provide simple, deterministic fake numbers.
        metadata = GenerationMetadata(
            model_name=self._model_name,
            latency_ms=latency_ms,
            prompt_tokens=None,
            completion_tokens=None,
        )

        return GeneratedSolution(task=task, code=code, metadata=metadata)

    def _fallback_implementation(self, task: Task) -> str:
        return textwrap.dedent(
            f"""
            # Stub implementation for task {task.task_id!r}
            # This is intentionally minimal and may not satisfy tests.

            def solve():
                raise NotImplementedError("No stub implementation for task {task.task_id!r}")
            """
        ).strip()

