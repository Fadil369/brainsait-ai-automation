"""Configuration management for the BrainSAIT automation platform."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field, HttpUrl, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class PlacesQuery(BaseModel):
    """Typed representation of a Google Places query configuration."""

    keyword: str
    radius_meters: int = Field(default=25_000, ge=100, le=50_000)
    type: str = Field(default="establishment")


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    google_maps_api_key: str = Field(..., alias="GOOGLE_MAPS_API_KEY")
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    openai_model: str = Field("gpt-5-codex", alias="OPENAI_MODEL")
    default_locale: str = Field("ar-SA", alias="DEFAULT_LOCALE")
    target_city: str = Field("Riyadh", alias="TARGET_CITY")
    target_country: str = Field("Saudi Arabia", alias="TARGET_COUNTRY")
    data_directory: Path = Field(Path("data"), alias="DATA_DIR")
    max_places_per_query: int = Field(60, alias="MAX_PLACES_PER_QUERY", ge=1, le=60)
    request_timeout_seconds: int = Field(20, alias="REQUEST_TIMEOUT_SECONDS", ge=5, le=120)
    places_radius_meters: int = Field(25_000, alias="PLACES_RADIUS_METERS", ge=1000, le=50_000)
    llm_temperature: float = Field(0.3, alias="LLM_TEMPERATURE", ge=0.0, le=1.0)
    allowed_industries: List[str] = Field(
        default_factory=lambda: [
            "restaurant",
            "clinic",
            "hospital",
            "dentist",
            "pharmacy",
            "retail",
            "education",
            "real estate",
            "law firm",
        ],
        alias="ALLOWED_INDUSTRIES",
    )
    outreach_reply_to: HttpUrl | None = Field(default=None, alias="OUTREACH_REPLY_TO")

    @validator("data_directory", pre=True)
    def _expand_data_dir(cls, value: str | Path) -> Path:  # noqa: D401
        """Ensure the data directory resolves to an absolute path."""

        return Path(value).expanduser().resolve()


@lru_cache
def get_settings() -> Settings:
    """Load and cache application settings."""

    settings = Settings()
    settings.data_directory.mkdir(parents=True, exist_ok=True)
    return settings


__all__ = ["Settings", "PlacesQuery", "get_settings"]
