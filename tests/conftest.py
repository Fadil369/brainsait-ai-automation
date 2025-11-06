"""Pytest configuration and fixtures."""

import os
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def test_data_dir():
    """Return path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def mock_env_vars():
    """Set up mock environment variables for testing."""
    original_vars = {}
    test_vars = {
        "GOOGLE_MAPS_API_KEY": "test_google_api_key",
        "OPENAI_API_KEY": "test_openai_api_key",
        "LOG_LEVEL": "DEBUG",
    }
    
    for key, value in test_vars.items():
        original_vars[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield test_vars
    
    # Restore original environment
    for key, original_value in original_vars.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


@pytest.fixture
def sample_business_dict():
    """Return sample business data as dictionary."""
    return {
        "place_id": "ChIJtest123",
        "name": "Test Restaurant",
        "formatted_address": "123 Main St, Riyadh 12345, Saudi Arabia",
        "geometry": {
            "location": {"lat": 24.7136, "lng": 46.6753}
        },
        "types": ["restaurant", "food", "point_of_interest"],
        "rating": 4.5,
        "user_ratings_total": 250,
        "website": "https://test-restaurant.example.com",
        "formatted_phone_number": "+966 11 234 5678",
    }


@pytest.fixture
def sample_feature_vector_dict():
    """Return sample feature vector as dictionary."""
    return {
        "place_id": "ChIJtest123",
        "business_name": "Test Restaurant",
        "website": "https://test-restaurant.example.com",
        "total_pages": 5,
        "languages": ["ar", "en"],
        "avg_word_count": 450.0,
        "has_structured_data": True,
        "has_meta_description": True,
        "has_open_graph": False,
        "has_analytics": True,
        "has_contact_cta": True,
        "has_viewport_meta": True,
        "has_email_address": True,
        "has_phone_number": False,
    }


@pytest.fixture
def sample_maturity_dict():
    """Return sample maturity assessment as dictionary."""
    return {
        "place_id": "ChIJtest123",
        "business_name": "Test Restaurant",
        "overall_score": 65.0,
        "subscores": {
            "technical": 70.0,
            "seo": 60.0,
            "content": 65.0,
            "trust": 65.0,
        },
        "highlights_en": "Good technical foundation with room for improvement",
        "highlights_ar": "أساس تقني جيد مع مجال للتحسين",
        "recommendations_en": "Focus on SEO optimization and content strategy",
        "recommendations_ar": "التركيز على تحسين السيو واستراتيجية المحتوى",
    }
