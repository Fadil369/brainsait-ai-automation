# Changelog

All notable changes to BrainSAIT AI Business Discovery System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-06

### Added
- Initial release of BrainSAIT AI Business Discovery System
- Google Places API integration for business discovery
- Web crawler with robots.txt compliance and language detection
- Feature engineering pipeline for business data extraction
- Digital maturity scoring across four dimensions (technical, SEO, content, trust)
- AI-powered bilingual narratives (Arabic/English) for maturity assessments
- Offer generation with three service tiers (Basic, Professional, Enterprise)
- Dynamic pricing with industry-specific premiums
- Bilingual outreach message generation
- CLI with three commands: discover, analyze, offers
- Comprehensive test suite with 38 tests across 3 modules
- DataStore helper for organized pipeline artifact management
- Git automation tools (git-setup.sh, GIT_SETUP.md)
- Setup automation script (setup_and_test.sh)
- Complete documentation and architecture diagrams
- GitHub Pages documentation site

### Features
- **Business Discovery**: Automated discovery via Google Maps Platform API
- **Digital Analysis**: Comprehensive maturity scoring with AI insights
- **Offer Generation**: Tailored service packages with bilingual outreach
- **Scalability**: Batch processing with configurable parameters
- **Bilingual**: Complete Arabic/English support for Saudi market
- **Testing**: 38 tests covering CLI, scoring, and offer generation

### Technical Highlights
- Python 3.11+ with modern async/await patterns
- Typer + Rich for beautiful CLI experience
- Pydantic for data validation and serialization
- pytest for comprehensive test coverage
- JSON-based structured outputs with timestamps
- Rate limiting and caching for API efficiency

[0.1.0]: https://github.com/Fadil369/brainsait-ai-automation/releases/tag/v0.1.0
