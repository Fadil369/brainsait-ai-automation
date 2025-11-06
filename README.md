# BrainSAIT AI-Powered Business Discovery System

[![License](https://img.shields.io/badge/license-Proprietary-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-brightgreen.svg)](https://python.org)
[![GitHub Pages](https://img.shields.io/badge/docs-GitHub%20Pages-brightgreen.svg)](https://fadil369.github.io/brainsait-ai-automation/)

## 🏢 Project Overview

BrainSAIT AI-Powered Business Discovery System is a comprehensive automation platform that discovers businesses using Google Maps Platform, analyzes their digital maturity, and generates tailored outreach campaigns with service packages. Built specifically for the Saudi Arabian market with bilingual support (Arabic/English).

🌐 **[View Documentation Site](https://fadil369.github.io/brainsait-ai-automation/)**

## ✨ Key Features

- **🔍 AI-Powered Business Discovery**: Automated discovery of businesses via Google Places API
- **📊 Digital Maturity Analysis**: Comprehensive scoring across technical, SEO, content, and trust dimensions  
- **🤖 Intelligent Offer Generation**: AI-generated tailored service packages with bilingual outreach
- **💰 Dynamic Pricing**: Industry-specific pricing with BrainSAIT's 3-tier service structure
- **🌍 Bilingual Support**: Complete Arabic/English support for Saudi market
- **⚡ Scalable Pipeline**: Batch processing with configurable parameters
- **💾 Comprehensive Storage**: JSON-based results with detailed analytics

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Google Maps Platform API Key
- OpenAI API Key (optional, for enhanced AI features)

### Installation

```bash
# Clone the repository
cd /Users/fadil369/Desktop/brainsait_ai_automation

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Edit `.env` file with your API credentials:

```env
# Google Maps Platform API Key (required)
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# OpenAI API Key (optional, for enhanced AI features)
OPENAI_API_KEY=your_openai_api_key_here

# OpenAI Base URL (optional)
OPENAI_BASE_URL=https://api.openai.com/v1

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Basic Usage

```bash
# Discover restaurants and clinics in Riyadh
brainsait-discover restaurant clinic

# Custom location and radius
brainsait-discover restaurant hospital --location "21.3891,39.8579" --radius 30000

# Analyze existing business data
brainsait-discover analyze business_data.json

# Generate offers for analyzed businesses  
brainsait-discover offers analysis_results.json

# Check configuration
brainsait-discover config
```

## 🏗️ Architecture

```
brainsait_ai_automation/
├── src/brainsait_ai/
│   ├── ai/                     # AI client and processing
│   │   └── client.py          # OpenAI integration
│   ├── config.py              # Settings and configuration
│   ├── features/              # Feature engineering
│   │   └── engineering.py     # Business feature extraction
│   ├── generation/            # AI offer generation
│   │   └── offers.py          # Tailored offer creation
│   ├── google_places/         # Google Places integration
│   │   └── client.py          # Places API client
│   ├── pipeline/              # Orchestration
│   │   └── orchestrator.py    # Main pipeline controller
│   ├── scoring/               # Digital maturity scoring
│   │   └── digital_maturity.py # Scoring algorithms
│   ├── storage/               # Data persistence
│   │   └── persistence.py     # File storage utilities
│   ├── utils/                 # Utilities
│   │   ├── http.py           # HTTP client with retry
│   │   └── text.py           # Text processing utilities
│   ├── cli.py                 # Command-line interface
│   └── logging_utils.py       # Logging configuration
├── tests/                     # Test suite
├── docs/                      # Documentation
├── data/                      # Data storage
└── results/                   # Output directory
```

## 🔧 Core Components

### 1. Business Discovery (`google_places/client.py`)

- Google Places API integration
- Bilingual search (English/Arabic)
- Rate limiting and caching
- Duplicate detection and removal

### 2. Feature Engineering (`features/engineering.py`)

- Business data extraction and normalization
- Website URL processing
- Contact information parsing
- Industry classification

### 3. Digital Maturity Scoring (`scoring/digital_maturity.py`)

- **Technical Score**: Website performance, mobile-friendliness, loading speed
- **SEO Score**: Search engine optimization signals, meta tags, structured data
- **Content Score**: Content quality, language support, information architecture
- **Trust Score**: SSL certificates, contact information, social proof

### 4. AI Offer Generation (`generation/offers.py`)

- **Service Packages**: Basic (1,500 SAR), Professional (3,500 SAR), Enterprise (8,000 SAR)
- **Industry Premiums**: Healthcare (+500 SAR), Education (+300 SAR), E-commerce (+700 SAR)
- **Bilingual Outreach**: Arabic and English email templates
- **ROI Projections**: Expected business growth metrics

### 5. Pipeline Orchestrator (`pipeline/orchestrator.py`)

- End-to-end pipeline execution
- Batch processing with configurable parameters
- Error handling and recovery
- Progress tracking and logging

## 📋 Usage Examples

### Basic Business Discovery

```bash
# Discover restaurants and healthcare facilities
brainsait-discover restaurant clinic hospital

# With custom parameters
brainsait-discover restaurant cafe \
  --location "24.7136,46.6753" \
  --radius 25000 \
  --max 50 \
  --batch 10
```

### Advanced Analysis

```bash
# Full pipeline with web analysis and offer generation
brainsait-discover restaurant medical-center \
  --location "21.3891,39.8579" \
  --radius 30000 \
  --max 100 \
  --output-dir "jeddah_analysis"

# Quick scan without web analysis
brainsait-discover retail shop \
  --no-web-analysis \
  --no-offers \
  --max 25
```

### Data Analysis

```bash
# Analyze existing business data
brainsait-discover analyze existing_businesses.json

# Generate offers for pre-analyzed businesses
brainsait-discover offers digital_maturity_results.json \
  --output-dir "tailored_offers" \
  --batch 5
```

## 📊 Output Structure

### Business Analysis Results

```json
{
  "timestamp": "2025-01-11T22:45:00+03:00",
  "config": {
    "search_radius": 25000,
    "max_businesses": 100,
    "include_web_analysis": true
  },
  "businesses_discovered": 85,
  "businesses_analyzed": 78,
  "offers_generated": 78,
  "results": [
    {
      "business": {
        "name": "مطعم和专业",
        "formatted_address": "Riyadh, Saudi Arabia",
        "place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
        "rating": 4.2,
        "user_ratings_total": 150
      },
      "features": {
        "industry": "restaurant",
        "website_url": "https://example.com",
        "phone_number": "+966112345678",
        "price_level": 2
      },
      "digital_maturity": {
        "overall_score": 65,
        "subscores": {
          "technical": 70,
          "seo": 60,
          "content": 75,
          "trust": 55
        },
        "english_analysis": "Moderate digital presence...",
        "arabic_analysis": "حضور رقمي متوسط...",
        "recommendations": ["Improve website SEO", "Add Arabic content"]
      }
    }
  ],
  "summary": {
    "total_businesses": 78,
    "average_maturity_score": 58.5,
    "industries": {
      "restaurant": 45,
      "healthcare": 20,
      "retail": 13
    },
    "maturity_distribution": {
      "low (0-30)": 15,
      "medium (31-70)": 48,
      "high (71-100)": 15
    }
  }
}
```

### Tailored Offer Structure

```json
{
  "business_analysis": {
    "business_name": "مطعم和专业",
    "industry": "restaurant",
    "location": "Riyadh, Saudi Arabia"
  },
  "tailored_offer": {
    "package_recommendation": "professional",
    "adjusted_price": 3700,
    "justification": "High potential for digital growth...",
    "arabic_summary": "حلول شاملة لتطوير الوجود الرقمي",
    "english_summary": "Comprehensive digital presence solutions",
    "priority_features": [
      "Google My Business optimization",
      "Professional website development",
      "Digital marketing strategy"
    ],
    "roi_projection": "زيادة 300-500% في الظهور الرقمي",
    "next_steps": [
      "Needs assessment meeting",
      "Custom implementation plan",
      "Development phase start"
    ]
  },
  "outreach_message": {
    "subject_ar": "عرض تطوير الأعمال الرقمية - مطعم和专业",
    "subject_en": "Digital Business Development Offer - Restaurant",
    "body_ar": "عزيزي فريق مطعم和专业...",
    "body_en": "Dear Restaurant Team...",
    "call_to_action": "احجز استشارة مجانية خلال 48 ساعة",
    "business_specific_details": "مخصص للمطاعم في الرياض"
  }
}
```

## 🔧 Configuration

### Pipeline Configuration

```python
from brainsait_ai.pipeline.orchestrator import PipelineConfig

config = PipelineConfig(
    search_radius=25000,        # 25km radius
    max_businesses=100,         # Maximum businesses to discover
    batch_size=20,             # Processing batch size
    include_web_analysis=True,   # Enable web content analysis
    generate_offers=True,       # Generate AI offers
    save_intermediate_results=True,
    output_directory="results"
)
```

### Service Package Configuration

```python
from brainsait_ai.generation.offers import SERVICE_TIERS, INDUSTRY_PREMIUMS

# Available service tiers
SERVICE_TIERS = {
    ServicePackage.BASIC: ServiceTier(
        name="أساسيات الأعمال",
        base_price=1500,
        features=["Google My Business optimization", "Basic SEO audit"],
        delivery_time="7-10 أيام",
        support_level="بريد إلكتروني"
    ),
    # ... additional tiers
}

# Industry-specific premiums
INDUSTRY_PREMIUMS = {
    "healthcare": IndustryPremium("الرعاية الصحية", 500),
    "education": IndustryPremium("التعليم", 300),
    "ecommerce": IndustryPremium("التجارة الإلكترونية", 700),
    # ... additional industries
}
```

## 🧪 Testing

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=src/brainsait_ai --cov-report=html

# Run specific test modules
pytest tests/test_cli.py
pytest tests/test_scoring.py
pytest tests/test_offers.py

# Run with verbose output
pytest -v

# Run specific test function
pytest tests/test_cli.py::test_version_command
```

### Test Coverage

The test suite includes:

- **CLI Tests** (`test_cli.py`): Command-line interface, data loading, summarization
- **Scoring Tests** (`test_scoring.py`): Digital maturity calculations, subscore validation
- **Offer Tests** (`test_offers.py`): Package recommendations, price adjustments, outreach generation
- **Integration Tests**: End-to-end pipeline validation with mocked dependencies

## 📈 Performance

- **Discovery Speed**: 2-5 seconds per business type
- **Analysis Rate**: 20 businesses per batch (configurable)
- **API Usage**: ~30-60 Google Places API requests per full scan
- **Memory Usage**: ~50-100MB for 100 businesses
- **Output Size**: ~1-2MB per 100 businesses analyzed

## 🔐 Security & Privacy

- **API Key Management**: Secure environment variable storage
- **Data Privacy**: Local processing, no external data transmission
- **Rate Limiting**: Automatic API call throttling
- **Error Handling**: Graceful degradation on API failures
- **Caching**: Local result caching to minimize API usage

## 🌍 Saudi Market Adaptation

- **Bilingual Support**: Complete Arabic/English interface
- **Local Coordinates**: Pre-configured for Saudi cities (Riyadh, Jeddah, Dammam)
- **Cultural Sensitivity**: Healthcare and professional services focus
- **Currency**: Saudi Riyal (SAR) pricing
- **Business Types**: Local industry categorization

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is proprietary software owned by BrainSAIT. All rights reserved.

## 🆘 Support

For technical support or questions:

- 📧 Email: support@brainsait.com
- 🌐 Documentation: [docs.brainsait.com](https://docs.brainsait.com)
- 📱 WhatsApp: +966501234567

---

**BrainSAIT AI-Powered Business Discovery System** - Transforming business intelligence for the Saudi digital economy.
