"""Tests for offer generation module."""

from unittest.mock import MagicMock

import pytest

from brainsait_ai.features.engineering import FeatureVector
from brainsait_ai.generation.offers import (
    BusinessAnalysis,
    OfferGenerator,
    ServicePackage,
    TailoredOffer,
)
from brainsait_ai.google_places.client import BusinessRecord, Coordinates
from brainsait_ai.scoring.digital_maturity import MaturityAssessment, SubScores


@pytest.fixture
def mock_llm():
    """Create a mock LLM client."""
    llm = MagicMock()
    llm.generate.return_value = '''{
        "justification": "Business needs digital upgrade",
        "summary_ar": "نوصي بحزمة متقدمة",
        "summary_en": "We recommend professional package",
        "priority_features": ["SEO optimization", "Content strategy"],
        "roi_projection": "40-60% increase in leads",
        "next_steps": ["Schedule workshop", "Begin implementation"]
    }'''
    return llm


@pytest.fixture
def sample_business():
    """Create sample business record."""
    return BusinessRecord(
        place_id="test123",
        name="Test Restaurant",
        address="123 Main St, Riyadh",
        location=Coordinates(lat=24.7, lng=46.6),
        types=("restaurant", "food"),
        rating=4.5,
        user_ratings_total=150,
        website="https://test-restaurant.com",
        phone_number="+966123456789",
        google_maps_url="https://maps.google.com/test123",
    )


@pytest.fixture
def sample_feature_vector():
    """Create sample feature vector."""
    return FeatureVector(
        place_id="test123",
        business_name="Test Restaurant",
        website="https://test-restaurant.com",
        total_pages=5,
        languages=["ar", "en"],
        avg_word_count=450.0,
        has_structured_data=True,
        has_meta_description=True,
        has_open_graph=False,
        has_analytics=True,
        has_contact_cta=True,
        has_viewport_meta=True,
        has_email_address=True,
        has_phone_number=False,
    )


@pytest.fixture
def sample_maturity():
    """Create sample maturity assessment."""
    return MaturityAssessment(
        place_id="test123",
        business_name="Test Restaurant",
        overall_score=65.0,
        subscores=SubScores(technical=70, seo=60, content=65, trust=65),
        highlights_en="Good technical setup",
        highlights_ar="إعداد تقني جيد",
        recommendations_en="Improve SEO",
        recommendations_ar="تحسين السيو",
    )


@pytest.fixture
def sample_analysis(sample_business, sample_feature_vector, sample_maturity):
    """Create sample business analysis."""
    return BusinessAnalysis(
        business=sample_business,
        feature_vector=sample_feature_vector,
        maturity=sample_maturity,
        industry="restaurant",
        web_page_titles=["Home", "Menu", "Contact", "About Us"],
    )


def test_analyze_package_fit_basic(mock_llm, sample_analysis):
    """Test package recommendation for low maturity."""
    generator = OfferGenerator(mock_llm)
    sample_analysis.maturity.overall_score = 25.0
    
    package = generator.analyze_package_fit(sample_analysis)
    assert package == ServicePackage.BASIC


def test_analyze_package_fit_professional(mock_llm, sample_analysis):
    """Test package recommendation for medium maturity."""
    generator = OfferGenerator(mock_llm)
    sample_analysis.maturity.overall_score = 55.0
    
    package = generator.analyze_package_fit(sample_analysis)
    assert package == ServicePackage.PROFESSIONAL


def test_analyze_package_fit_enterprise(mock_llm, sample_analysis):
    """Test package recommendation for high maturity."""
    generator = OfferGenerator(mock_llm)
    sample_analysis.maturity.overall_score = 85.0
    
    package = generator.analyze_package_fit(sample_analysis)
    assert package == ServicePackage.ENTERPRISE


def test_calculate_adjusted_price(mock_llm):
    """Test price calculation with industry premium."""
    generator = OfferGenerator(mock_llm)
    
    # Restaurant has 200 SAR premium
    price = generator.calculate_adjusted_price(ServicePackage.BASIC, "restaurant")
    assert price == 1700  # 1500 + 200
    
    # Healthcare has 500 SAR premium
    price = generator.calculate_adjusted_price(ServicePackage.PROFESSIONAL, "healthcare")
    assert price == 4000  # 3500 + 500
    
    # Unknown industry has no premium
    price = generator.calculate_adjusted_price(ServicePackage.ENTERPRISE, "unknown")
    assert price == 8000


def test_generate_tailored_offer(mock_llm, sample_analysis):
    """Test full offer generation."""
    generator = OfferGenerator(mock_llm)
    
    offer = generator.generate_tailored_offer(sample_analysis)
    
    assert isinstance(offer, TailoredOffer)
    assert offer.package_recommendation == ServicePackage.PROFESSIONAL
    assert offer.adjusted_price == 3700  # 3500 + 200 restaurant premium
    assert "digital upgrade" in offer.justification.lower()
    assert len(offer.priority_features) > 0
    assert offer.arabic_summary
    assert offer.english_summary


def test_create_outreach_message(mock_llm, sample_analysis):
    """Test outreach message generation."""
    generator = OfferGenerator(mock_llm)
    
    offer = TailoredOffer(
        package_recommendation=ServicePackage.PROFESSIONAL,
        adjusted_price=3700,
        justification="Boost digital presence",
        arabic_summary="تطوير الحضور الرقمي",
        english_summary="Digital presence upgrade",
        priority_features=["SEO", "Content"],
        roi_projection="40-60% increase",
        next_steps=["Workshop", "Implementation"],
    )
    
    mock_llm.generate.return_value = '''{
        "subject_ar": "عرض تطوير رقمي",
        "subject_en": "Digital Upgrade Offer",
        "body_ar": "عزيزي فريق المطعم",
        "body_en": "Dear restaurant team",
        "call_to_action": "Schedule free consultation",
        "business_details": "Tailored for restaurants in Riyadh"
    }'''
    
    message = generator.create_outreach_message(sample_analysis, offer)
    
    assert message.subject_ar
    assert message.subject_en
    assert message.body_ar
    assert message.body_en
    assert message.call_to_action


def test_save_offer_to_file(mock_llm, sample_analysis, tmp_path):
    """Test offer persistence to file."""
    generator = OfferGenerator(mock_llm)
    
    offer = generator.generate_tailored_offer(sample_analysis)
    
    mock_llm.generate.return_value = '''{
        "subject_ar": "عرض",
        "subject_en": "Offer",
        "body_ar": "نص",
        "body_en": "Text",
        "call_to_action": "Call",
        "business_details": "Details"
    }'''
    
    message = generator.create_outreach_message(sample_analysis, offer)
    
    output_file = tmp_path / "offer_test.json"
    result_path = generator.save_offer_to_file(sample_analysis, offer, message, output_file)
    
    assert result_path.exists()
    
    import json
    with result_path.open("r") as f:
        data = json.load(f)
    
    assert data["business"]["name"] == "Test Restaurant"
    assert data["tailored_offer"]["package_recommendation"] == "professional"
    assert data["outreach_message"]["subject_en"] == "Offer"
