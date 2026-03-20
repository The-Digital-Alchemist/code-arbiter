from __future__ import annotations

import os
import re
import time

from openai import OpenAI

from dataset.manager import Task
from generation.base import BaseGenerator, GeneratedSolution, GenerationMetadata


def _strip_code_fences(text: str) -> str:
    """Remove ```python ... ``` or ``` ... ``` wrappers LLMs often include."""
    match = re.search(r"```(?:\w+)?\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


class OpenAIGenerator:
    """
    Generates code using the OpenAI API.

    Set OPENAI_API_KEY in your environment or .env file.
    Override the model with OPENAI_MODEL (default: gpt-4o-mini).
    """

    def __init__(self, model: str | None = None) -> None:
        self._model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate(self, task: Task) -> GeneratedSolution:
        prompt = (
            f"{task.description}\n\n"
            "Return ONLY the code. No explanation, no markdown, no extra text."
        )

        start = time.perf_counter()
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
        )
        latency_ms = (time.perf_counter() - start) * 1000.0

        code = _strip_code_fences(response.choices[0].message.content)

        metadata = GenerationMetadata(
            model_name=self._model,
            latency_ms=latency_ms,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
        )
        return GeneratedSolution(task=task, code=code, metadata=metadata)