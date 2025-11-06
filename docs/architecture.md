# BrainSAIT Automated Digital Maturity Platform

## 1. Vision
BrainSAIT needs an AI-enabled pipeline that automatically discovers Riyadh businesses, gathers a 360° view of their digital presence, and recommends tailored interventions (Search Console verification, SEO, content, analytics, etc.). The system must deliver:

- Automated Google Places based business discovery
- Rich enrichment from public web content and social signals
- Digital maturity scoring across technical, content, UX, and trust dimensions
- AI-authored summaries, recommendations, and outreach collateral in Arabic and English
- Persisted evidence (raw data, analytics, generated assets) for sales teams

## 2. High-Level Architecture
```
┌──────────────────┐      ┌──────────────────────┐      ┌──────────────────┐      ┌─────────────────────┐      ┌───────────────────────┐
│  Scheduler / CLI │────▶│ Google Places Agent  │────▶│  Enrichment Layer │────▶│ Digital Maturity AI  │────▶│ Offer & Outreach AI   │
└──────────────────┘      │  (Discovery)         │      │ (Web, social, etc.)│      │ Scoring + Insights │      │  (Packages & Scripts) │
                          └──────────────────────┘      └──────────────────┘      └─────────────────────┘      └───────────────────────┘
                                      │                                              │                           │
                                      ▼                                              ▼                           ▼
                           ┌────────────────────┐                           ┌──────────────────────┐     ┌────────────────────┐
                           │ Persistent Storage │◀─────────────────────────│ Feature Store / Data │────▶│ Sales Enablement DB │
                           │ (Parquet + SQLite) │                           │ Frames               │     │ & Asset Library     │
                           └────────────────────┘                           └──────────────────────┘     └────────────────────┘
```

## 3. Component Responsibilities

### 3.1 Orchestrator (CLI + Workflow)
- Entry point to run full pipeline or incremental updates
- Manages configuration, logging, retries, and progress reporting
- Supports dry-run, resume, and batch segmentation

### 3.2 Google Places Discovery Agent
- Uses Places API (Nearby Search + Place Details) with API key pulled from env/secret store
- Applies smart batching, exponential backoff, daily quota cap
- Normalises outputs into canonical schema (place_id, name, categories, geo, contact, web URLs)
- Persists raw payloads for audit and reprocessing

### 3.3 Enrichment Layer
- Multi-language web crawler respecting robots.txt and rate limits
- Expands seed URLs to relevant internal pages (About, Services, Blog, Contact)
- Extracts structured signals: schema.org data, meta tags, headings, social links, contact info, analytics tags, structured data, load times (optional Lighthouse hook)
- Optionally integrates social signals (Instagram, Twitter, LinkedIn) when discoverable

### 3.4 Feature Store
- Converts raw data to analytical features per business:
  - Technical: HTTPS, canonical tags, structured data, mobile friendliness hints
  - SEO: keyword coverage, content depth, schema coverage
  - Content: language support, freshness, bilingual readiness, conversion hooks
  - Trust: reviews, testimonials, security badges, privacy policy
- Stores in Parquet/SQLite for reuse by scoring and reporting modules

### 3.5 Digital Maturity AI Scoring
- Deterministic heuristics (e.g., presence/absence of key signals) combined with LLM scoring prompts
- Produces sub-scores (0–100) and qualitative rationales per pillar
- Uses cached/persisted context to avoid repeated crawling per re-run

### 3.6 Offer & Outreach Generation
- Parameterised prompt templates keyed to maturity profiles and industries
- Generates bilingual summaries: current state, opportunities, recommended BrainSAIT packages, ROI framing
- Produces outreach email drafts, call scripts, and short social DM variants
- Provides structured JSON output plus ready-to-send Markdown/HTML assets

### 3.7 Storage & Assets
- Local `data/` directory (extensible to cloud) with hierarchy:
  - `raw/places/<date>.jsonl` – raw Places responses
  - `raw/web/<domain>/pages/*.html` – fetched pages
  - `features/*.parquet` – engineered feature tables
  - `reports/<date>/...` – generated summaries & outreach kits
  - `logs/` – pipeline execution logs
- Optional SQLite database for quick querying and deduping

## 4. Tech Stack & Dependencies
- **Python 3.11+**
- HTTP & Google APIs: `googlemaps`, `requests`, `tenacity` (retries)
- Parsing & NLP: `beautifulsoup4`, `readability-lxml`, `trafilatura`, `langdetect`
- Data handling: `pydantic`, `pandas`, `pyarrow`
- AI integration: `openai` (or Azure/Open Source adapters), `jinja2` for templating
- Orchestration & CLI: `typer` or `click`, `rich` for progress
- Testing: `pytest`, `pytest-mock`, `responses` (HTTP mocking)

## 5. Security & Compliance
- Store secrets in `.env` (never committed); support environment overrides
- Rotate and restrict Google API key (HTTP referrers or IPs)
- Respect `robots.txt`, introduce crawl delay, and cap concurrent requests
- Cache LLM prompts/responses for transparency; allow override to disable AI for sensitive contexts

## 6. Future Extensions
- Integrate CRM push (HubSpot, Salesforce) via optional connectors
- Support scheduling via GitHub Actions or Airflow
- Add dashboard (Streamlit/Next.js) for interactive review
- Expand to other geographies with dynamic locale selection

This document guides the implementation tasks and ensures all stakeholders share a consistent view of the solution. Updates should reflect refinements as we implement and test each module.
