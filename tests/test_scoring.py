"""Tests for digital maturity scoring."""

from unittest.mock import MagicMock

import pytest

from brainsait_ai.features.engineering import FeatureVector
from brainsait_ai.google_places.client import BusinessRecord, Coordinates
from brainsait_ai.scoring.digital_maturity import DigitalMaturityScorer, SubScores


@pytest.fixture
def mock_llm():
    """Create a mock LLM client."""
    llm = MagicMock()
    llm.generate.return_value = "Strong technical foundation. Good SEO practices.|أساس تقني قوي. ممارسات سيو جيدة.|Improve content quality. Add analytics.|تحسين جودة المحتوى. إضافة تحليلات."
    return llm


@pytest.fixture
def sample_business():
    """Create sample business record."""
    return BusinessRecord(
        place_id="test123",
        name="Test Business",
        address="123 Main St",
        location=Coordinates(lat=24.7, lng=46.6),
        types=("store",),
        rating=4.2,
        user_ratings_total=100,
        website="https://test-business.com",
        phone_number="+966123456789",
        google_maps_url="https://maps.google.com/test",
    )


@pytest.fixture
def high_maturity_features():
    """Create feature vector for high maturity business."""
    return FeatureVector(
        place_id="test123",
        business_name="Test Business",
        website="https://test-business.com",
        total_pages=10,
        languages=["ar", "en"],
        avg_word_count=600.0,
        has_structured_data=True,
        has_meta_description=True,
        has_open_graph=True,
        has_analytics=True,
        has_contact_cta=True,
        has_viewport_meta=True,
        has_email_address=True,
        has_phone_number=True,
    )


@pytest.fixture
def low_maturity_features():
    """Create feature vector for low maturity business."""
    return FeatureVector(
        place_id="test123",
        business_name="Test Business",
        website=None,
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


def test_score_high_maturity(mock_llm, sample_business, high_maturity_features):
    """Test scoring for high maturity business."""
    scorer = DigitalMaturityScorer(mock_llm)
    
    assessment = scorer.score(sample_business, high_maturity_features)
    
    assert assessment.overall_score > 70
    assert assessment.subscores.technical > 70
    assert assessment.subscores.seo > 60
    assert assessment.subscores.content > 60
    assert assessment.highlights_en
    assert assessment.highlights_ar
    assert assessment.recommendations_en
    assert assessment.recommendations_ar


def test_score_low_maturity(mock_llm, sample_business, low_maturity_features):
    """Test scoring for low maturity business."""
    scorer = DigitalMaturityScorer(mock_llm)
    
    assessment = scorer.score(sample_business, low_maturity_features)
    
    assert assessment.overall_score < 40
    assert assessment.subscores.technical < 30
    assert assessment.subscores.seo < 30
    assert assessment.subscores.content < 30


def test_subscores_calculation(mock_llm, sample_business, high_maturity_features):
    """Test subscore breakdown."""
    scorer = DigitalMaturityScorer(mock_llm)
    
    assessment = scorer.score(sample_business, high_maturity_features)
    subscores = assessment.subscores
    
    # Technical subscore checks
    assert isinstance(subscores.technical, (int, float))
    assert 0 <= subscores.technical <= 100
    
    # SEO subscore checks
    assert isinstance(subscores.seo, (int, float))
    assert 0 <= subscores.seo <= 100
    
    # Content subscore checks
    assert isinstance(subscores.content, (int, float))
    assert 0 <= subscores.content <= 100
    
    # Trust subscore checks
    assert isinstance(subscores.trust, (int, float))
    assert 0 <= subscores.trust <= 100


def test_overall_score_is_average(mock_llm, sample_business, high_maturity_features):
    """Test overall score equals average of subscores."""
    scorer = DigitalMaturityScorer(mock_llm)
    
    assessment = scorer.score(sample_business, high_maturity_features)
    
    expected_avg = (
        assessment.subscores.technical
        + assessment.subscores.seo
        + assessment.subscores.content
        + assessment.subscores.trust
    ) / 4
    
    assert abs(assessment.overall_score - expected_avg) < 0.1


def test_bilingual_output(mock_llm, sample_business, high_maturity_features):
    """Test bilingual highlights and recommendations."""
    scorer = DigitalMaturityScorer(mock_llm)
    
    assessment = scorer.score(sample_business, high_maturity_features)
    
    # Check both languages present
    assert len(assessment.highlights_en) > 0
    assert len(assessment.highlights_ar) > 0
    assert len(assessment.recommendations_en) > 0
    assert len(assessment.recommendations_ar) > 0
    
    # Arabic text should contain Arabic characters
    assert any('\u0600' <= c <= '\u06FF' for c in assessment.highlights_ar)


def test_missing_website_handling(mock_llm, sample_business):
    """Test scoring when business has no website."""
    features = FeatureVector(
        place_id="test123",
        business_name="Test Business",
        website=None,
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
    
    scorer = DigitalMaturityScorer(mock_llm)
    assessment = scorer.score(sample_business, features)
    
    # Should still produce valid assessment
    assert 0 <= assessment.overall_score <= 100
    assert assessment.highlights_en
    assert assessment.recommendations_en
