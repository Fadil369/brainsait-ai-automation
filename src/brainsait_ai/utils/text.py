"""Text processing utilities."""

from __future__ import annotations

import re
from typing import Iterable, List


def clean_whitespace(text: str) -> str:
    """Collapse redundant whitespace and strip ends."""

    return re.sub(r"\s+", " ", text or "").strip()


def truncate_text(text: str, *, max_length: int = 280) -> str:
    """Trim text to a maximum length with an ellipsis if needed."""

    cleaned = clean_whitespace(text)
    if len(cleaned) <= max_length:
        return cleaned
    return cleaned[: max_length - 1].rstrip() + "…"


def chunk_text(text: str, *, max_tokens: int = 500) -> List[str]:
    """Chunk text into roughly max_tokens sized pieces."""

    words = text.split()
    if not words:
        return []

    chunks: List[str] = []
    current: List[str] = []
    for word in words:
        current.append(word)
        if len(current) >= max_tokens:
            chunks.append(" ".join(current))
            current = []
    if current:
        chunks.append(" ".join(current))
    return chunks


def merge_texts(texts: Iterable[str]) -> str:
    """Join multiple text snippets into a single cleaned blob."""

    return "\n\n".join(clean_whitespace(t) for t in texts if t)


def format_currency(value: float | int, currency: str = "SAR") -> str:
    """Format numeric values as a human-friendly currency string."""

    return f"{value:,.0f} {currency}"


__all__ = ["clean_whitespace", "chunk_text", "merge_texts", "truncate_text", "format_currency"]
