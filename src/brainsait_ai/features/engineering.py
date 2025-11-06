"""Feature engineering derived from raw Places + web crawl data."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from statistics import mean
from typing import Iterable, List

from bs4 import BeautifulSoup

from brainsait_ai.enrichment.web_crawler import PageSnapshot
from brainsait_ai.google_places.client import BusinessRecord

_LANGUAGE_CODE_MAP = {
    "ar": "Arabic",
    "en": "English",
    "ar-sa": "Arabic",
    "en-us": "English",
}

_ANALYTICS_PATTERNS = (
    re.compile(r"gtag\("),
    re.compile(r"googletagmanager"),
    re.compile(r"analytics.js"),
    re.compile(r"gtm-"),
)

_CONTACT_KEYWORDS = {"contact", "book", "call", "appointment", "consultation"}


@dataclass(slots=True)
class FeatureVector:
    place_id: str
    business_name: str
    website: str | None
    total_pages: int
    languages: List[str]
    avg_word_count: float
    has_structured_data: bool
    has_meta_description: bool
    has_open_graph: bool
    has_analytics: bool
    has_contact_cta: bool
    has_viewport_meta: bool
    has_email_address: bool
    has_phone_number: bool


def build_feature_vector(business: BusinessRecord, pages: Iterable[PageSnapshot]) -> FeatureVector:
    snapshots = list(pages)
    if not snapshots:
        return FeatureVector(
            place_id=business.place_id,
            business_name=business.name,
            website=business.website,
            total_pages=0,
            languages=[],
            avg_word_count=0.0,
            has_structured_data=False,
            has_meta_description=False,
            has_open_graph=False,
            has_analytics=False,
            has_contact_cta=False,
            has_viewport_meta=False,
            has_email_address=False,
            has_phone_number=False,
        )

    language_counter: Counter[str] = Counter()
    word_counts: List[int] = []
    structured_data = False
    meta_description = False
    open_graph = False
    analytics = False
    contact_cta = False
    viewport_meta = False
    email_present = False
    phone_present = False

    for snapshot in snapshots:
        text = snapshot.extracted_text
        if snapshot.language:
            language_code = snapshot.language.lower()
            language_label = _LANGUAGE_CODE_MAP.get(language_code, snapshot.language)
            if language_label:
                language_counter[language_label] += 1
        words = len(text.split())
        word_counts.append(words)

        soup = BeautifulSoup(snapshot.raw_html, "lxml")
        if soup.find("script", attrs={"type": "application/ld+json"}) or "schema.org" in snapshot.raw_html:
            structured_data = True
        if soup.find("meta", attrs={"name": "description"}):
            meta_description = True
        if soup.find("meta", attrs={"property": re.compile(r"^og:")}):
            open_graph = True
        if soup.find("meta", attrs={"name": "viewport"}):
            viewport_meta = True
        if _contains_patterns(snapshot.raw_html, _ANALYTICS_PATTERNS):
            analytics = True
        if _contains_contact_cta(soup):
            contact_cta = True
        if re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text):
            email_present = True
        if re.search(r"\+?\d[\d\s().-]{7,}", text):
            phone_present = True

    languages = [language for language, _ in language_counter.most_common()]
    avg_words = mean(word_counts) if word_counts else 0.0

    return FeatureVector(
        place_id=business.place_id,
        business_name=business.name,
        website=business.website,
        total_pages=len(snapshots),
        languages=languages,
        avg_word_count=avg_words,
        has_structured_data=structured_data,
        has_meta_description=meta_description,
        has_open_graph=open_graph,
        has_analytics=analytics,
        has_contact_cta=contact_cta,
        has_viewport_meta=viewport_meta,
        has_email_address=email_present,
        has_phone_number=phone_present,
    )


def _contains_patterns(text: str, patterns: Iterable[re.Pattern[str]]) -> bool:
    return any(pattern.search(text) for pattern in patterns)


def _contains_contact_cta(soup: BeautifulSoup) -> bool:
    for anchor in soup.find_all("a"):
        content = (anchor.get_text() or "").strip().lower()
        if any(keyword in content for keyword in _CONTACT_KEYWORDS):
            return True
    return False


__all__ = ["FeatureVector", "build_feature_vector"]
