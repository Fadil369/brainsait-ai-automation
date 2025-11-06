"""HTTP utility helpers."""

from __future__ import annotations

import logging
from typing import Optional

import requests
from requests import Response
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        " AppleWebKit/537.36 (KHTML, like Gecko)"
        " Chrome/119.0.0.0 Safari/537.36"
    )
}


class HttpError(RuntimeError):
    """Raised when an HTTP request ultimately fails."""


@retry(
    retry=retry_if_exception_type((requests.RequestException, HttpError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    reraise=True,
)
def get(
    url: str,
    *,
    timeout: int = 15,
    headers: Optional[dict[str, str]] = None,
    session: Optional[requests.Session] = None,
) -> Response:
    """Perform an HTTP GET request with retries and logging."""

    session = session or requests.Session()
    merged_headers = {**DEFAULT_HEADERS, **(headers or {})}
    try:
        response = session.get(url, headers=merged_headers, timeout=timeout)
    except requests.RequestException as exc:  # pragma: no cover - delegated to retry
        logger.warning("HTTP request failed: %s", exc)
        raise

    if response.status_code >= 400:
        msg = f"HTTP {response.status_code} for {url}"
        logger.warning(msg)
        raise HttpError(msg)

    return response


__all__ = ["get", "HttpError", "DEFAULT_HEADERS"]
