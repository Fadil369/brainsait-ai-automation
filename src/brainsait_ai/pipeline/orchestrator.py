"""Pipeline orchestrator for end-to-end business discovery and analysis."""

from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from brainsait_ai.ai.client import LLMConfig, OpenAILLM
from brainsait_ai.config import Settings
from brainsait_ai.enrichment.web_crawler import PageSnapshot, WebCrawler
from brainsait_ai.features.engineering import FeatureVector, build_feature_vector
from brainsait_ai.generation.offers import (
    BusinessAnalysis as OfferInput,
    OfferGenerator,
    OutreachMessage,
    TailoredOffer,
)
from brainsait_ai.google_places.client import BusinessRecord, Coordinates, GooglePlacesClient
from brainsait_ai.scoring.digital_maturity import DigitalMaturityScorer, MaturityAssessment
from brainsait_ai.storage.persistence import DataStore


@dataclass
class PipelineConfig:
    """Runtime configuration for the discovery pipeline."""

    search_radius: int = 25_000
    max_businesses: int = 100
    batch_size: int = 20
    include_web_analysis: bool = True
    generate_offers: bool = True
    save_intermediate_results: bool = True
    output_directory: str = "results"


@dataclass
class DiscoveryResult:
    """Aggregated result returned by the pipeline."""

    timestamp: str
    config: PipelineConfig
    businesses_discovered: int
    analyses: List["AnalyzedBusiness"]
    offers_generated: int
    summary: Dict[str, Any]
    output_files: List[str]


@dataclass
class AnalyzedBusiness:
    """Container for an analysed business and optional generated assets."""

    business: BusinessRecord
    feature_vector: FeatureVector
    pages: List[PageSnapshot]
    maturity: MaturityAssessment
    industry: str
    offer: Optional[TailoredOffer] = None
    outreach: Optional[OutreachMessage] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "business": _dataclass_to_dict(self.business),
            "feature_vector": _dataclass_to_dict(self.feature_vector),
            "pages": [_dataclass_to_dict(page) for page in self.pages],
            "digital_maturity": _dataclass_to_dict(self.maturity),
            "industry": self.industry,
            "tailored_offer": _dataclass_to_dict(self.offer) if self.offer else None,
            "outreach_message": _dataclass_to_dict(self.outreach) if self.outreach else None,
        }


class PipelineOrchestrator:
    """Main orchestrator coordinating discovery, analysis, and offer generation."""

    def __init__(self, settings: Settings, config: Optional[PipelineConfig] = None) -> None:
        self.settings = settings
        self.config = config or PipelineConfig()
        self.logger = logging.getLogger(__name__)

        self.data_store = DataStore(Path(self.config.output_directory))
        self.places_client = GooglePlacesClient(settings.google_maps_api_key)
        self.web_crawler = WebCrawler()

        llm_client = OpenAILLM(
            api_key=settings.openai_api_key,
            config=LLMConfig(
                model=settings.openai_model,
                temperature=settings.llm_temperature,
            ),
        )
        self.scorer = DigitalMaturityScorer(llm_client, locale=settings.default_locale)
        self.offer_generator = OfferGenerator(llm_client)

    async def run_discovery_pipeline(
        self,
        business_types: Sequence[str],
        location: Tuple[float, float] = (24.7136, 46.6753),
    ) -> DiscoveryResult:
        start_time = datetime.utcnow()
        self.logger.info("Starting discovery pipeline for %s business types", len(business_types))

        discovered = await self._discover_businesses(business_types, location)
        if not discovered:
            self.logger.warning("No businesses discovered. Exiting pipeline.")
            return DiscoveryResult(
                timestamp=start_time.isoformat() + "Z",
                config=self.config,
                businesses_discovered=0,
                analyses=[],
                offers_generated=0,
                summary={"total_businesses": 0, "offers_generated": 0},
                output_files=[],
            )

        analyses = await self._analyze_businesses(discovered)

        offers_generated = 0
        if self.config.generate_offers:
            offers_generated = await self._generate_offers(analyses)

        run_dir = self.data_store.create_run_directory(timestamp=start_time)
        summary = self._create_summary(analyses, offers_generated)
        output_files = self._persist_outputs(analyses, summary, run_dir)

        self.logger.info(
            "Pipeline completed in %.2fs", (datetime.utcnow() - start_time).total_seconds()
        )

        return DiscoveryResult(
            timestamp=start_time.isoformat() + "Z",
            config=self.config,
            businesses_discovered=len(discovered),
            analyses=analyses,
            offers_generated=offers_generated,
            summary=summary,
            output_files=output_files,
        )

    async def _discover_businesses(
        self, business_types: Sequence[str], location: Tuple[float, float]
    ) -> List[BusinessRecord]:
        per_type_limit = max(1, self.config.max_businesses // max(len(business_types), 1))
        coords = Coordinates(lat=location[0], lng=location[1])
        discovered: Dict[str, BusinessRecord] = {}

        for business_type in business_types:
            try:
                self.logger.debug("Discovering type '%s'", business_type)
                results = await asyncio.to_thread(
                    self.places_client.discover,
                    keyword=business_type,
                    location=coords,
                    radius_meters=self.config.search_radius,
                    language=self.settings.default_locale.split("-", 1)[0],
                    max_results=per_type_limit,
                    fetch_details=True,
                )
            except Exception as exc:  # pragma: no cover - network issues
                self.logger.error("Discovery failed for %s: %s", business_type, exc)
                continue

            for record in results:
                if record.place_id not in discovered:
                    discovered[record.place_id] = record

            await asyncio.sleep(0.25)

        self.logger.info("Discovered %s unique businesses", len(discovered))
        return list(discovered.values())

    async def _analyze_businesses(self, businesses: Sequence[BusinessRecord]) -> List[AnalyzedBusiness]:
        analyses: List[AnalyzedBusiness] = []

        for index, business in enumerate(businesses, start=1):
            self.logger.debug("Analysing %s (%s/%s)", business.name, index, len(businesses))

            pages: List[PageSnapshot] = []
            if self.config.include_web_analysis and business.website:
                pages = await asyncio.to_thread(self.web_crawler.crawl, business.website)

            feature_vector = build_feature_vector(business, pages)

            try:
                maturity = self.scorer.score(business, feature_vector)
            except Exception as exc:  # pragma: no cover - LLM/network failure
                self.logger.error("Scoring failed for %s: %s", business.name, exc)
                continue

            industry = _infer_industry(business)

            analyses.append(
                AnalyzedBusiness(
                    business=business,
                    feature_vector=feature_vector,
                    pages=pages,
                    maturity=maturity,
                    industry=industry,
                )
            )

        self.logger.info("Prepared analyses for %s businesses", len(analyses))
        return analyses

    async def _generate_offers(self, analyses: Sequence[AnalyzedBusiness]) -> int:
        offers = 0
        for analysis in analyses:
            profile = OfferInput(
                business=analysis.business,
                feature_vector=analysis.feature_vector,
                maturity=analysis.maturity,
                industry=analysis.industry,
                web_page_titles=[page.title for page in analysis.pages if page.title],
                locale=self.settings.default_locale,
            )
            try:
                offer = self.offer_generator.generate_tailored_offer(profile)
                outreach = self.offer_generator.create_outreach_message(profile, offer)
            except Exception as exc:  # pragma: no cover - LLM/network failure
                self.logger.error("Offer generation failed for %s: %s", analysis.business.name, exc)
                continue

            analysis.offer = offer
            analysis.outreach = outreach
            offers += 1

        self.logger.info("Generated %s offers", offers)
        return offers

    def _persist_outputs(
        self,
        analyses: Sequence[AnalyzedBusiness],
        summary: Dict[str, Any],
        run_dir: Path,
    ) -> List[str]:
        output_paths: List[str] = []

        analyses_path = run_dir / "analyses.jsonl"
        self.data_store.write_jsonl((analysis.to_dict() for analysis in analyses), analyses_path)
        output_paths.append(str(analyses_path))

        summary_path = run_dir / "summary.json"
        self.data_store.write_json(summary, summary_path)
        output_paths.append(str(summary_path))

        if self.config.save_intermediate_results:
            per_business_dir = run_dir / "businesses"
            per_business_dir.mkdir(parents=True, exist_ok=True)
            for analysis in analyses:
                filename = f"{_slugify(analysis.business.name)}.json"
                path = per_business_dir / filename
                self.data_store.write_json(analysis.to_dict(), path)
                output_paths.append(str(path))

        return output_paths

    def _create_summary(
        self, analyses: Sequence[AnalyzedBusiness], offers_generated: int
    ) -> Dict[str, Any]:
        if not analyses:
            return {
                "total_businesses": 0,
                "average_maturity_score": 0,
                "industries": {},
                "maturity_distribution": {},
                "offers_generated": offers_generated,
            }

        scores = [analysis.maturity.overall_score for analysis in analyses]
        industry_counter: Dict[str, int] = {}
        for analysis in analyses:
            industry_counter[analysis.industry] = industry_counter.get(analysis.industry, 0) + 1

        maturity_distribution = {
            "low (0-30)": len([score for score in scores if score <= 30]),
            "medium (31-70)": len([score for score in scores if 31 <= score <= 70]),
            "high (71-100)": len([score for score in scores if score > 70]),
        }

        return {
            "total_businesses": len(analyses),
            "average_maturity_score": round(sum(scores) / len(scores), 2),
            "min_maturity_score": min(scores),
            "max_maturity_score": max(scores),
            "industries": dict(sorted(industry_counter.items(), key=lambda kv: kv[1], reverse=True)),
            "maturity_distribution": maturity_distribution,
            "offers_generated": offers_generated,
            "analysis_completed_at": datetime.utcnow().isoformat() + "Z",
        }


def _infer_industry(business: BusinessRecord) -> str:
    if business.types:
        return business.types[0].replace("_", " ").title()
    return "General"


def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-") or "business"


def _dataclass_to_dict(obj: Any) -> Any:
    if obj is None:
        return None
    if hasattr(obj, "__dataclass_fields__"):
        from dataclasses import asdict

        return asdict(obj)
    return obj


async def run_pipeline_cli(
    business_types: Sequence[str],
    location: Tuple[float, float] = (24.7136, 46.6753),
    config: Optional[PipelineConfig] = None,
) -> DiscoveryResult:
    settings = Settings()
    orchestrator = PipelineOrchestrator(settings, config)
    return await orchestrator.run_discovery_pipeline(business_types, location)


if __name__ == "__main__":  # pragma: no cover - manual execution utility
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m brainsait_ai.pipeline.orchestrator <business_type1> [business_type2 ...]")
        raise SystemExit(1)

    result = asyncio.run(run_pipeline_cli(sys.argv[1:]))
    print("Pipeline completed. Summary:")
    print(result.summary)
