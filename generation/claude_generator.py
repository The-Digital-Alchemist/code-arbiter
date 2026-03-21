from __future__ import annotations

import os
import re
import time

import anthropic

from dataset.manager import Task
from generation.base import BaseGenerator, GeneratedSolution, GenerationMetadata, build_prompt


def _strip_code_fences(text: str) -> str:
    """Remove ```python ... ``` or ``` ... ``` wrappers LLMs often include."""
    match = re.search(r"```(?:\w+)?\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


class ClaudeGenerator:
    """
    Generates code using the Anthropic Claude API.

    Set ANTHROPIC_API_KEY in your environment or .env file.
    Override the model with CLAUDE_MODEL (default: claude-opus-4-6).
    """

    def __init__(self, model: str | None = None) -> None:
        self._model = model or os.getenv("CLAUDE_MODEL", "claude-opus-4-6")
        self._client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def generate(self, task: Task) -> GeneratedSolution:
        prompt = build_prompt(task)

        start = time.perf_counter()
        message = self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        latency_ms = (time.perf_counter() - start) * 1000.0

        code = _strip_code_fences(message.content[0].text)

        metadata = GenerationMetadata(
            model_name=self._model,
            latency_ms=latency_ms,
            prompt_tokens=message.usage.input_tokens,
            completion_tokens=message.usage.output_tokens,
        )
        return GeneratedSolution(task=task, code=code, metadata=metadata)