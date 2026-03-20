from __future__ import annotations

import os

from generation.base import BaseGenerator


def get_generator(provider: str | None = None) -> BaseGenerator:
    """
    Return a generator for the given provider.

    Provider is resolved in this order:
      1. `provider` argument
      2. GENERATOR_PROVIDER environment variable
      3. Falls back to "stub" (safe default — no API key needed)

    Supported providers:
      - "claude"   → ClaudeGenerator  (requires ANTHROPIC_API_KEY)
      - "openai"   → OpenAIGenerator  (requires OPENAI_API_KEY)
      - "stub"     → StubGenerator    (hardcoded, no API key)

    Adding a new provider: create generation/<name>_generator.py,
    implement the BaseGenerator protocol, and add a case below.
    """
    resolved = provider or os.getenv("GENERATOR_PROVIDER", "stub")

    if resolved == "claude":
        from generation.claude_generator import ClaudeGenerator
        return ClaudeGenerator()

    if resolved == "openai":
        from generation.openai_generator import OpenAIGenerator
        return OpenAIGenerator()

    if resolved == "stub":
        from generation.stub_generator import StubGenerator
        return StubGenerator()

    raise ValueError(
        f"Unknown provider {resolved!r}. "
        "Set GENERATOR_PROVIDER to 'claude', 'openai', or 'stub'."
    )