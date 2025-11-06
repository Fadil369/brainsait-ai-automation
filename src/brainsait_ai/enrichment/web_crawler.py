"""Business website enrichment crawler."""

from __future__ import annotations

import logging
import urllib.parse
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Iterable, List, Optional, Set
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from langdetect import DetectorFactory, detect
from trafilatura import extract as extract_text

from brainsait_ai.utils.http import get as http_get
from brainsait_ai.utils.text import clean_whitespace

logger = logging.getLogger(__name__)
DetectorFactory.seed = 0


@dataclass(slots=True)
class PageSnapshot:
    url: str
    title: str
    language: str | None
    raw_html: str
    extracted_text: str


class WebCrawler:
    """Respectful crawler for collecting business website evidence."""

    def __init__(
        self,
        *,
        session: Optional[requests.Session] = None,
        timeout: int = 15,
        max_pages: int = 5,
    ) -> None:
        self._session = session or requests.Session()
        self._timeout = timeout
        self._max_pages = max_pages
        self._robots_cache: Dict[str, RobotFileParser] = {}

    def crawl(self, url: str) -> List[PageSnapshot]:
        """Crawl up to max_pages internal pages starting from url."""

        normalized_root = self._normalize_url(url)
        if not normalized_root:
            logger.debug("Invalid URL skipped: %s", url)
            return []

        to_visit: List[str] = [normalized_root]
        seen: Set[str] = set()
        snapshots: List[PageSnapshot] = []

        while to_visit and len(snapshots) < self._max_pages:
            target = to_visit.pop(0)
            if target in seen or not self._is_allowed(target):
                continue
            seen.add(target)

            html = self._fetch_html(target)
            if html is None:
                continue

            soup = BeautifulSoup(html, "lxml")
            title = clean_whitespace(soup.title.string) if soup.title else ""
            text = clean_whitespace(extract_text(html) or soup.get_text(" "))
            language = self._detect_language(text)
            snapshots.append(
                PageSnapshot(
                    url=target,
                    title=title,
                    language=language,
                    raw_html=html,
                    extracted_text=text,
                )
            )

            for link in self._extract_internal_links(normalized_root, soup):
                if link not in seen and link not in to_visit and len(to_visit) < self._max_pages * 2:
                    to_visit.append(link)

        return snapshots

    def _fetch_html(self, url: str) -> str | None:
        try:
            response = http_get(url, timeout=self._timeout, session=self._session)
            response.encoding = response.encoding or "utf-8"
            return response.text
        except Exception as exc:  # pragma: no cover - network failure handled via logging
            logger.debug("Failed to fetch %s: %s", url, exc)
            return None

    def _extract_internal_links(self, root_url: str, soup: BeautifulSoup) -> Iterable[str]:
        root_parts = urllib.parse.urlsplit(root_url)
        links: Set[str] = set()
        for tag in soup.find_all("a", href=True):
            href = str(tag.get("href", ""))
            parsed = urllib.parse.urljoin(root_url, href)
            parsed_parts = urllib.parse.urlsplit(parsed)
            if parsed_parts.netloc != root_parts.netloc:
                continue
            if parsed_parts.scheme not in {"http", "https"}:
                continue
            normalized = self._normalize_url(parsed)
            if normalized:
                links.add(normalized)
        return links

    def _is_allowed(self, url: str) -> bool:
        parser = self._get_robot_parser(url)
        return parser.can_fetch("*", url)

    def _get_robot_parser(self, url: str) -> RobotFileParser:
        domain = self._domain_key(url)
        if domain in self._robots_cache:
            return self._robots_cache[domain]
        robots_url = urllib.parse.urljoin(domain, "/robots.txt")
        parser = RobotFileParser()
        parser.set_url(robots_url)
        try:
            parser.read()
        except Exception as exc:  # pragma: no cover - network errors are acceptable
            logger.debug("Could not read robots.txt for %s: %s", domain, exc)
        self._robots_cache[domain] = parser
        return parser

    @staticmethod
    def _normalize_url(url: str) -> str | None:
        try:
            parsed = urllib.parse.urlsplit(url)
        except ValueError:
            return None
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            return None
        normalized = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path or "/", "", ""))
        return normalized.rstrip("/") + ("" if parsed.path else "/")

    @staticmethod
    def _domain_key(url: str) -> str:
        parsed = urllib.parse.urlsplit(url)
        return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))

    @staticmethod
    def _detect_language(text: str) -> str | None:
        if len(text) < 20:
            return None
        try:
            return detect(text)
        except Exception:  # pragma: no cover - short texts cause detection issues
            return None


__all__ = ["WebCrawler", "PageSnapshot"]
