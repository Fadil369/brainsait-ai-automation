"""BrainSAIT automated digital maturity platform."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("brainsait-ai")
except PackageNotFoundError:  # pragma: no cover - during development without install
    __version__ = "0.0.0"

__all__ = ["__version__"]
