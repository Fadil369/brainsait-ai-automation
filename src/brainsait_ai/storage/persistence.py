"""Persistence helpers for raw data, features, and generated assets."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import pandas as pd

Timestamp = datetime


def ensure_directory(path: Path) -> Path:
    """Ensure a directory exists and return it."""

    path.mkdir(parents=True, exist_ok=True)
    return path


def write_jsonl(records: Iterable[Mapping[str, Any]], path: Path) -> None:
    """Persist an iterable of mappings as newline-delimited JSON."""

    ensure_directory(path.parent)
    with path.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def write_dataframe(df: pd.DataFrame, path: Path) -> None:
    """Persist a pandas DataFrame as Parquet."""

    ensure_directory(path.parent)
    df.to_parquet(path, index=False)


def load_dataframe(path: Path) -> pd.DataFrame:
    """Load a pandas DataFrame from Parquet."""

    return pd.read_parquet(path)


def serialize_dataclass(instance: Any) -> Mapping[str, Any]:
    """Serialize dataclass or mapping objects to a dict."""

    if is_dataclass(instance) and not isinstance(instance, type):
        return asdict(instance)
    if isinstance(instance, Mapping):
        return dict(instance)
    msg = f"Unsupported type for serialization: {type(instance)!r}"
    raise TypeError(msg)


def timestamped_path(root: Path, *parts: str, suffix: str) -> Path:
    """Generate a timestamped path under a root directory."""

    ensure_directory(root)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    return root.joinpath(*parts, f"{timestamp}{suffix}")


def chunk_sequence(items: Sequence[Any], chunk_size: int) -> Iterable[Sequence[Any]]:
    """Yield chunks of a sequence."""

    for i in range(0, len(items), chunk_size):
        yield items[i : i + chunk_size]


class DataStore:
    """Convenience wrapper for organising pipeline output artifacts."""

    def __init__(self, root: Path) -> None:
        self.root = ensure_directory(root)

    def create_run_directory(self, *, timestamp: datetime | None = None) -> Path:
        run_id = (timestamp or datetime.utcnow()).strftime("%Y%m%dT%H%M%SZ")
        run_dir = self.root / run_id
        ensure_directory(run_dir)
        return run_dir

    def write_json(self, data: Any, path: Path) -> Path:
        ensure_directory(path.parent)
        with path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        return path

    def write_jsonl(self, records: Iterable[Mapping[str, Any]], path: Path) -> Path:
        ensure_directory(path.parent)
        with path.open("w", encoding="utf-8") as fh:
            for record in records:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        return path


__all__ = [
    "Timestamp",
    "ensure_directory",
    "write_jsonl",
    "write_dataframe",
    "load_dataframe",
    "serialize_dataclass",
    "timestamped_path",
    "chunk_sequence",
    "DataStore",
]
