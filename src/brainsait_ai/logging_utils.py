"""Centralised logging configuration."""

from __future__ import annotations

import logging
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler


def configure_logging(level: int = logging.INFO, console: Optional[Console] = None) -> None:
    """Configure application-wide logging with Rich."""

    console = console or Console()
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[RichHandler(console=console, rich_tracebacks=True, markup=True)],
        force=True,
    )


__all__ = ["configure_logging"]
