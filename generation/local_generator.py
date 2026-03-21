from __future__ import annotations

import os
import re
import time

from openai import OpenAI

from dataset.manager import Task
from generation.base import BaseGenerator, GeneratedSolution, GenerationMetadata, build_prompt


def _strip_code_fences(text: str) -> str:
    match = re.search(r"```(?:\w+)?\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


class LocalGenerator:
    """
    Generates code using a locally-hosted model via an OpenAI-compatible API
    (e.g. LM Studio, Ollama, llama.cpp server).

    Set LOCAL_MODEL_URL in your .env to point at the server.
    Set LOCAL_MODEL_NAME to the model identifier the server expects.

    Defaults:
        LOCAL_MODEL_URL  = http://192.168.100.68:1234
        LOCAL_MODEL_NAME = local-model
    """

    def __init__(self, model: str | None = None, base_url: str | None = None) -> None:
        self._base_url = base_url or os.getenv("LOCAL_MODEL_URL", "http://192.168.100.68:1234")
        self._model = model or os.getenv("LOCAL_MODEL_NAME", "local-model")
        self._client = OpenAI(
            base_url=f"{self._base_url}/v1",
            api_key="local",  # LM Studio ignores this but the client requires it
        )

    def generate(self, task: Task) -> GeneratedSolution:
        prompt = build_prompt(task)

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
            prompt_tokens=response.usage.prompt_tokens if response.usage else None,
            completion_tokens=response.usage.completion_tokens if response.usage else None,
        )
        return GeneratedSolution(task=task, code=code, metadata=metadata)
