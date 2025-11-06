"""LLM client abstraction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol

from openai import OpenAI


class SupportsLLM(Protocol):
    """Protocol describing the minimal interface for an LLM client."""

    def generate(self, prompt: str, **kwargs: object) -> str: ...  # pragma: no cover - interface only


@dataclass(slots=True)
class LLMConfig:
    """Runtime configuration for LLM invocations."""

    model: str
    temperature: float = 0.3
    max_output_tokens: int = 1_000
    system_prompt: str | None = None


class OpenAILLM:
    """OpenAI powered LLM client."""

    def __init__(self, api_key: str, config: LLMConfig) -> None:
        self._client = OpenAI(api_key=api_key)
        self._config = config

    def generate(self, prompt: str, *, extra_context: Iterable[str] | None = None) -> str:
        messages = []
        if self._config.system_prompt:
            messages.append({"role": "system", "content": self._config.system_prompt})
        if extra_context:
            messages.append({"role": "user", "content": "\n\n".join(extra_context)})
        messages.append({"role": "user", "content": prompt})
        response = self._client.chat.completions.create(
            model=self._config.model,
            messages=messages,
            temperature=self._config.temperature,
            max_tokens=self._config.max_output_tokens,
        )
        return response.choices[0].message.content or ""


__all__ = ["LLMConfig", "OpenAILLM", "SupportsLLM"]
