"""Digital maturity scoring for BrainSAIT prospects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from brainsait_ai.ai.client import SupportsLLM
from brainsait_ai.features.engineering import FeatureVector
from brainsait_ai.google_places.client import BusinessRecord


@dataclass(slots=True)
class SubScores:
    technical: float
    seo: float
    content: float
    trust: float


@dataclass(slots=True)
class MaturityAssessment:
    place_id: str
    business_name: str
    overall_score: float
    subscores: SubScores
    highlights_en: str
    highlights_ar: str
    recommendations_en: str
    recommendations_ar: str


class DigitalMaturityScorer:
    """Combine heuristic scoring with LLM insight generation."""

    def __init__(self, llm: SupportsLLM, *, locale: str = "ar-SA") -> None:
        self._llm = llm
        self._locale = locale

    def score(self, business: BusinessRecord, features: FeatureVector) -> MaturityAssessment:
        subscores = self._calculate_subscores(business, features)
        overall = round(
            (subscores.technical + subscores.seo + subscores.content + subscores.trust) / 4,
            2,
        )
        highlight_prompt = self._build_prompt(business, features, subscores, language="English")
        highlight_prompt_ar = self._build_prompt(business, features, subscores, language="Arabic")
        recommendation_prompt = self._build_recommendation_prompt(business, features, subscores, language="English")
        recommendation_prompt_ar = self._build_recommendation_prompt(business, features, subscores, language="Arabic")
        highlights_en = self._llm.generate(highlight_prompt)
        highlights_ar = self._llm.generate(highlight_prompt_ar)
        recommendations_en = self._llm.generate(recommendation_prompt)
        recommendations_ar = self._llm.generate(recommendation_prompt_ar)
        return MaturityAssessment(
            place_id=business.place_id,
            business_name=business.name,
            overall_score=overall,
            subscores=subscores,
            highlights_en=highlights_en.strip(),
            highlights_ar=highlights_ar.strip(),
            recommendations_en=recommendations_en.strip(),
            recommendations_ar=recommendations_ar.strip(),
        )

    def _calculate_subscores(self, business: BusinessRecord, features: FeatureVector) -> SubScores:
        technical = self._score_technical(business, features)
        seo = self._score_seo(features)
        content = self._score_content(features)
        trust = self._score_trust(business, features)
        return SubScores(technical=technical, seo=seo, content=content, trust=trust)

    @staticmethod
    def _score_technical(business: BusinessRecord, features: FeatureVector) -> float:
        score = 50.0
        if business.website and business.website.startswith("https"):
            score += 15
        if features.has_structured_data:
            score += 10
        if features.has_viewport_meta:
            score += 10
        if features.has_analytics:
            score += 15
        return min(score, 100.0)

    @staticmethod
    def _score_seo(features: FeatureVector) -> float:
        score = 40.0
        if features.has_meta_description:
            score += 15
        if features.has_open_graph:
            score += 10
        if len(features.languages) >= 2:
            score += 15
        if features.avg_word_count >= 300:
            score += 20
        return min(score, 100.0)

    @staticmethod
    def _score_content(features: FeatureVector) -> float:
        score = 35.0
        if features.avg_word_count >= 400:
            score += 20
        elif features.avg_word_count >= 250:
            score += 10
        if features.total_pages >= 3:
            score += 15
        if features.has_contact_cta:
            score += 10
        return min(score, 100.0)

    @staticmethod
    def _score_trust(business: BusinessRecord, features: FeatureVector) -> float:
        score = 45.0
        if (business.rating or 0) >= 4.2:
            score += 15
        if features.has_email_address:
            score += 10
        if features.has_phone_number:
            score += 10
        if business.user_ratings_total and business.user_ratings_total > 50:
            score += 10
        return min(score, 100.0)

    def _build_prompt(
        self,
        business: BusinessRecord,
        features: FeatureVector,
        subscores: SubScores,
        *,
        language: str,
    ) -> str:
        languages = ", ".join(features.languages)
        language_summary = languages if languages else "Unknown"
        return (
            f"You are an AI analyst for BrainSAIT. Provide a concise {language} summary of the "
            f"digital maturity for {business.name} located at {business.address}.\n"
            f"Technical score: {subscores.technical}. SEO score: {subscores.seo}. "
            f"Content score: {subscores.content}. Trust score: {subscores.trust}.\n"
            f"Crawled pages: {features.total_pages}. Languages detected: {language_summary}.\n"
            "Highlight strengths and call out the top risks without marketing fluff."
        )

    def _build_recommendation_prompt(
        self,
        business: BusinessRecord,
        features: FeatureVector,
        subscores: SubScores,
        *,
        language: str,
    ) -> str:
        return (
            f"You are an expert consultant at BrainSAIT. Craft a persuasive yet actionable {language} "
            f"recommendation for {business.name}. Tie the advice to BrainSAIT packages (Basic, Professional, "
            f"Enterprise) as appropriate.\n"
            f"Scores - Technical: {subscores.technical}, SEO: {subscores.seo}, Content: {subscores.content}, "
            f"Trust: {subscores.trust}.\n"
            f"Key signals: structured data={features.has_structured_data}, analytics={features.has_analytics}, "
            f"contact CTA={features.has_contact_cta}, average word count={features.avg_word_count:.0f}.\n"
            "Limit to 4 bullet points max and include a clear next step."
        )


__all__ = ["DigitalMaturityScorer", "MaturityAssessment", "SubScores"]
