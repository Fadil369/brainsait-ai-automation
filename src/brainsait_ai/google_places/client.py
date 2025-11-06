"""Google Places integration for business discovery."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence

import googlemaps
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from brainsait_ai.storage.persistence import chunk_sequence

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class Coordinates:
    lat: float
    lng: float


@dataclass(slots=True)
class BusinessRecord:
    place_id: str
    name: str
    address: str
    location: Coordinates
    types: Sequence[str]
    rating: float | None
    user_ratings_total: int | None
    website: str | None
    phone_number: str | None
    google_maps_url: str


class GooglePlacesClient:
    """Wrapper around googlemaps.Client with quota-aware helpers."""

    def __init__(
        self,
        api_key: str,
        *,
        request_timeout: int = 15,
        underlying_client: Optional[googlemaps.Client] = None,
    ) -> None:
        self._client = underlying_client or googlemaps.Client(key=api_key, timeout=request_timeout)
        self._request_timeout = request_timeout

    @retry(
        retry=retry_if_exception_type(googlemaps.exceptions.TransportError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    def _places_nearby(self, **kwargs: object) -> dict:
        return self._client.places_nearby(**kwargs)

    @retry(
        retry=retry_if_exception_type(googlemaps.exceptions.TransportError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    def _place_details(self, place_id: str, fields: Optional[List[str]] = None) -> dict:
        return self._client.place(place_id=place_id, fields=fields)

    def discover(
        self,
        *,
        keyword: str,
        location: Coordinates,
        radius_meters: int,
        language: str = "en",
        max_results: int = 60,
        fetch_details: bool = True,
    ) -> List[BusinessRecord]:
        """Discover businesses using Places Nearby Search."""

        results: Dict[str, BusinessRecord] = {}
        page_token: Optional[str] = None

        while True:
            response = self._places_nearby(
                keyword=keyword,
                location=(location.lat, location.lng),
                radius=radius_meters,
                language=language,
                page_token=page_token,
            )
            for candidate in response.get("results", []):
                place_id = candidate["place_id"]
                if place_id in results:
                    continue
                record = BusinessRecord(
                    place_id=place_id,
                    name=candidate.get("name", ""),
                    address=candidate.get("vicinity") or candidate.get("formatted_address", ""),
                    location=Coordinates(
                        lat=candidate["geometry"]["location"]["lat"],
                        lng=candidate["geometry"]["location"]["lng"],
                    ),
                    types=tuple(candidate.get("types", [])),
                    rating=candidate.get("rating"),
                    user_ratings_total=candidate.get("user_ratings_total"),
                    website=None,
                    phone_number=None,
                    google_maps_url=f"https://maps.google.com/?cid={candidate.get('place_id')}",
                )
                results[place_id] = record
            page_token = response.get("next_page_token")
            if not page_token or len(results) >= max_results:
                break

        if fetch_details:
            self._enrich_with_details(results.values())

        return list(results.values())[:max_results]

    def _enrich_with_details(self, records: Iterable[BusinessRecord]) -> None:
        fields = [
            "formatted_phone_number",
            "international_phone_number",
            "website",
            "url",
        ]
        for batch in chunk_sequence(list(records), 10):
            for record in batch:
                try:
                    detail = self._place_details(record.place_id, fields=fields)
                except googlemaps.exceptions.ApiError as exc:
                    logger.warning("Places detail fetch failed for %s: %s", record.place_id, exc)
                    continue
                result = detail.get("result", {})
                record.phone_number = (
                    result.get("formatted_phone_number")
                    or result.get("international_phone_number")
                    or record.phone_number
                )
                record.website = result.get("website", record.website)
                record.google_maps_url = result.get("url", record.google_maps_url)


__all__ = ["GooglePlacesClient", "BusinessRecord", "Coordinates"]
