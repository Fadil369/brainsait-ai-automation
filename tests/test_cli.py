"""Tests for CLI commands."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from brainsait_ai.cli import app, _load_analysis_records, _summarise_records, _slugify


runner = CliRunner()


def test_version_command():
    """Test version command displays correct information."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "BrainSAIT AI Business Discovery" in result.stdout


def test_config_command():
    """Test config command displays settings table."""
    result = runner.invoke(app, ["config"])
    assert result.exit_code == 0
    assert "BrainSAIT Configuration" in result.stdout


def test_load_analysis_records_json(tmp_path):
    """Test loading analysis records from JSON file."""
    test_data = [
        {"business": {"name": "Test Co"}, "digital_maturity": {"overall_score": 75}},
        {"business": {"name": "Demo Inc"}, "digital_maturity": {"overall_score": 55}},
    ]
    
    json_file = tmp_path / "analyses.json"
    json_file.write_text(json.dumps(test_data))
    
    records = _load_analysis_records(json_file)
    assert len(records) == 2
    assert records[0]["business"]["name"] == "Test Co"


def test_load_analysis_records_jsonl(tmp_path):
    """Test loading analysis records from JSONL file."""
    test_data = [
        {"business": {"name": "Test Co"}, "digital_maturity": {"overall_score": 75}},
        {"business": {"name": "Demo Inc"}, "digital_maturity": {"overall_score": 55}},
    ]
    
    jsonl_file = tmp_path / "analyses.jsonl"
    with jsonl_file.open("w") as f:
        for record in test_data:
            f.write(json.dumps(record) + "\n")
    
    records = _load_analysis_records(jsonl_file)
    assert len(records) == 2
    assert records[1]["business"]["name"] == "Demo Inc"


def test_summarise_records():
    """Test summary statistics generation."""
    records = [
        {
            "digital_maturity": {"overall_score": 80},
            "industry": "healthcare",
        },
        {
            "digital_maturity": {"overall_score": 60},
            "industry": "restaurant",
        },
        {
            "digital_maturity": {"overall_score": 70},
            "industry": "healthcare",
        },
    ]
    
    summary = _summarise_records(records)
    assert summary["total"] == 3
    assert summary["average_score"] == 70.0
    assert summary["industries"]["healthcare"] == 2
    assert summary["industries"]["restaurant"] == 1


def test_summarise_records_empty():
    """Test summary with empty records."""
    summary = _summarise_records([])
    assert summary == {"total": 0}


def test_slugify():
    """Test slugification for filesystem safety."""
    assert _slugify("Test Business Name") == "test-business-name"
    assert _slugify("Café & Restaurant!!") == "caf-restaurant"
    assert _slugify("   spaces   everywhere   ") == "spaces-everywhere"
    assert _slugify("αβγ123") == "123"
    assert _slugify("!!!") == "business"


@patch("brainsait_ai.cli.run_pipeline_cli")
def test_discover_command(mock_pipeline):
    """Test discover command execution."""
    from brainsait_ai.pipeline.orchestrator import DiscoveryResult, PipelineConfig
    
    mock_result = DiscoveryResult(
        timestamp="2025-11-05T10:00:00Z",
        config=PipelineConfig(),
        businesses_discovered=50,
        analyses=[],
        offers_generated=0,
        summary={"total_businesses": 50},
        output_files=["results/summary.json"],
    )
    mock_pipeline.return_value = mock_result
    
    result = runner.invoke(app, ["discover", "restaurant", "--max", "50", "--no-web-analysis"])
    assert result.exit_code == 0
    assert mock_pipeline.called


def test_analyze_command(tmp_path):
    """Test analyze command with sample data."""
    test_data = [
        {
            "business": {"name": "Test Co", "place_id": "abc123"},
            "digital_maturity": {"overall_score": 75},
            "industry": "healthcare",
        }
    ]
    
    json_file = tmp_path / "test_analyses.json"
    json_file.write_text(json.dumps(test_data))
    
    result = runner.invoke(app, ["analyze", str(json_file)])
    assert result.exit_code == 0
    assert "Loaded" in result.stdout
    assert "1 business" in result.stdout


@patch("brainsait_ai.cli.OpenAILLM")
@patch("brainsait_ai.cli.OfferGenerator")
def test_offers_command(mock_generator_class, mock_llm_class, tmp_path):
    """Test offers command with mocked LLM."""
    test_data = [
        {
            "business": {
                "name": "Test Co",
                "place_id": "abc123",
                "address": "123 Test St",
                "location": {"lat": 24.7, "lng": 46.6},
                "types": ["restaurant"],
                "google_maps_url": "https://maps.google.com/test",
            },
            "feature_vector": {
                "place_id": "abc123",
                "business_name": "Test Co",
                "total_pages": 5,
                "languages": ["ar", "en"],
                "avg_word_count": 500.0,
                "has_structured_data": True,
                "has_meta_description": True,
                "has_open_graph": False,
                "has_analytics": True,
                "has_contact_cta": True,
                "has_viewport_meta": True,
                "has_email_address": True,
                "has_phone_number": False,
            },
            "digital_maturity": {
                "place_id": "abc123",
                "business_name": "Test Co",
                "overall_score": 75.0,
                "subscores": {"technical": 80, "seo": 70, "content": 75, "trust": 75},
                "highlights_en": "Strong technical foundation",
                "highlights_ar": "أساس تقني قوي",
                "recommendations_en": "Improve content",
                "recommendations_ar": "تحسين المحتوى",
            },
            "industry": "restaurant",
            "pages": [],
        }
    ]
    
    json_file = tmp_path / "test_analyses.json"
    json_file.write_text(json.dumps(test_data))
    
    output_dir = tmp_path / "offers"
    
    # Mock generator instance
    mock_generator = MagicMock()
    mock_generator_class.return_value = mock_generator
    
    result = runner.invoke(app, ["offers", str(json_file), "--output", str(output_dir)])
    
    # Should initialize LLM and generator
    assert mock_llm_class.called
    assert mock_generator_class.called
    assert result.exit_code == 0
