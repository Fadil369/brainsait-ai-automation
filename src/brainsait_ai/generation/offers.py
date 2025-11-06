"""AI-powered offer generation and outreach creation module."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List

from brainsait_ai.ai.client import SupportsLLM
from brainsait_ai.features.engineering import FeatureVector
from brainsait_ai.google_places.client import BusinessRecord
from brainsait_ai.scoring.digital_maturity import MaturityAssessment, SubScores
from brainsait_ai.utils.text import clean_whitespace, format_currency, truncate_text


class ServicePackage(Enum):
    """BrainSAIT service packages with pricing."""
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


@dataclass
class ServiceTier:
    """Service tier configuration."""
    name: str
    base_price: int  # Price in SAR
    features: List[str]
    delivery_time: str
    support_level: str


@dataclass
class IndustryPremium:
    """Industry-specific pricing adjustments."""
    industry: str
    premium_sar: int
    description: str


# BrainSAIT Service Configuration
SERVICE_TIERS = {
    ServicePackage.BASIC: ServiceTier(
        name="أساسيات الأعمال",
        base_price=1500,
        features=[
            "Google My Business Profile Optimization",
            "Basic Website SEO Audit",
            "Local Search Presence Setup",
            "Basic Social Media Integration",
            "30 Days Performance Monitoring"
        ],
        delivery_time="7-10 أيام",
        support_level="بريد إلكتروني"
    ),
    ServicePackage.PROFESSIONAL: ServiceTier(
        name="المهنية المتقدمة",
        base_price=3500,
        features=[
            "Complete Digital Presence Audit",
            "Advanced Google Search Optimization",
            "Professional Website Development",
            "Content Marketing Strategy",
            "Social Media Management",
            "Analytics & Reporting Dashboard",
            "60 Days Performance Monitoring",
            "Priority Support"
        ],
        delivery_time="14-21 يوم",
        support_level="هاتف + بريد إلكتروني"
    ),
    ServicePackage.ENTERPRISE: ServiceTier(
        name="حلول المؤسسات",
        base_price=8000,
        features=[
            "Comprehensive Digital Transformation",
            "Multi-Platform Integration",
            "Advanced Analytics & BI",
            "Custom Software Solutions",
            "Marketing Automation",
            "24/7 Support & Monitoring",
            "Dedicated Account Manager",
            "90 Days Performance Guarantee"
        ],
        delivery_time="30-45 يوم",
        support_level="مخصص + مدير حساب"
    )
}

INDUSTRY_PREMIUMS = {
    "healthcare": IndustryPremium("الرعاية الصحية", 500, "متطلبات الامتثال الطبي"),
    "education": IndustryPremium("التعليم", 300, "متطلبات الوصول التعليمي"),
    "ecommerce": IndustryPremium("التجارة الإلكترونية", 700, "تكامل المدفوعات والأمان"),
    "restaurant": IndustryPremium("المطاعم", 200, "تطبيقات التوصيل والطلبات"),
    "real_estate": IndustryPremium("العقارات", 400, "قوائم متعددة المنصات"),
    "automotive": IndustryPremium("السيارات", 300, "معلومات المنتج التفصيلية"),
}


@dataclass
class BusinessAnalysis:
    """Business context passed to the offer generator."""

    business: BusinessRecord
    feature_vector: FeatureVector
    maturity: MaturityAssessment
    industry: str
    web_page_titles: List[str]
    locale: str = "ar-SA"

    @property
    def business_name(self) -> str:
        return self.business.name

    @property
    def location(self) -> str:
        return self.business.address


@dataclass
class TailoredOffer:
    """AI-generated tailored business offer."""
    package_recommendation: ServicePackage
    adjusted_price: int
    justification: str
    arabic_summary: str
    english_summary: str
    priority_features: List[str]
    roi_projection: str
    next_steps: List[str]


@dataclass
class OutreachMessage:
    """Bilingual outreach message for business contact."""
    subject_ar: str
    subject_en: str
    body_ar: str
    body_en: str
    call_to_action: str
    business_specific_details: str


class OfferGenerator:
    """Generates tailored offers based on business analysis."""
    
    def __init__(self, llm: SupportsLLM, *, currency: str = "SAR") -> None:
        self._llm = llm
        self._currency = currency
        
    def analyze_package_fit(self, analysis: BusinessAnalysis) -> ServicePackage:
        """Determine best service package based on business maturity and needs."""
        maturity_score = analysis.maturity.overall_score
        
        # Rule-based package recommendation
        if maturity_score < 30:
            return ServicePackage.BASIC
        elif maturity_score < 70:
            return ServicePackage.PROFESSIONAL
        else:
            return ServicePackage.ENTERPRISE
    
    def calculate_adjusted_price(self, package: ServicePackage, industry: str) -> int:
        """Calculate final price with industry premium."""
        base_price = SERVICE_TIERS[package].base_price
        
        # Apply industry premium
        industry_key = industry.lower().replace(" ", "_")
        premium = INDUSTRY_PREMIUMS.get(industry_key, IndustryPremium("", 0, ""))
        
        return base_price + premium.premium_sar
    
    def generate_tailored_offer(self, analysis: BusinessAnalysis) -> TailoredOffer:
        """Generate comprehensive tailored offer for a business."""
        
        # Determine package and price
        recommended_package = self.analyze_package_fit(analysis)
        adjusted_price = self.calculate_adjusted_price(recommended_package, analysis.industry)
        
        # Generate AI-powered content
        offer_payload = self._build_offer_prompt(analysis, recommended_package, adjusted_price)
        offer_data = self._invoke_llm_json(offer_payload)

        return TailoredOffer(
            package_recommendation=recommended_package,
            adjusted_price=adjusted_price,
            justification=offer_data.get(
                "justification",
                "عرض مخصص لتعزيز الحضور الرقمي وتحويل الزوار إلى عملاء.",
            ),
            arabic_summary=offer_data.get(
                "summary_ar",
                "نقدم لكم خطة متكاملة لتطوير حضوركم الرقمي وزيادة التفاعل مع العملاء.",
            ),
            english_summary=offer_data.get(
                "summary_en",
                "We will deliver a comprehensive digital upgrade that accelerates growth.",
            ),
            priority_features=self._extract_list(offer_data.get("priority_features")),
            roi_projection=offer_data.get(
                "roi_projection",
                "Expected uplift of 40-60% in qualified leads within 90 days.",
            ),
            next_steps=self._extract_list(offer_data.get("next_steps"), fallback=[
                "Schedule a discovery workshop",
                "Align on execution roadmap",
                "Kick off implementation with BrainSAIT team",
            ]),
        )

    def create_outreach_message(self, analysis: BusinessAnalysis, offer: TailoredOffer) -> OutreachMessage:
        """Create personalized outreach message for the business."""

        prompt = self._build_outreach_prompt(analysis, offer)
        message_data = self._invoke_llm_json(prompt)

        return OutreachMessage(
            subject_ar=message_data.get(
                "subject_ar",
                f"عرض تطوير الحضور الرقمي - {analysis.business_name}",
            ),
            subject_en=message_data.get(
                "subject_en",
                f"Digital Presence Upgrade Offer - {analysis.business_name}",
            ),
            body_ar=message_data.get("body_ar")
            or self._default_body_ar(analysis, offer),
            body_en=message_data.get("body_en")
            or self._default_body_en(analysis, offer),
            call_to_action=message_data.get("call_to_action", "احجز استشارة مجانية خلال 48 ساعة"),
            business_specific_details=message_data.get(
                "business_details",
                f"حلول مخصصة لـ {analysis.industry} في {analysis.location}",
            ),
        )

    def save_offer_to_file(
        self,
        analysis: BusinessAnalysis,
        offer: TailoredOffer,
        outreach: OutreachMessage,
        output_path: Path,
    ) -> Path:
        """Persist the generated offer package to disk."""

        payload = {
            "business": asdict(analysis.business),
            "feature_vector": asdict(analysis.feature_vector),
            "digital_maturity": asdict(analysis.maturity),
            "industry": analysis.industry,
            "tailored_offer": asdict(offer),
            "outreach_message": asdict(outreach),
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
        return output_path

    def _invoke_llm_json(self, prompt: str) -> Dict[str, Any]:
        raw = self._llm.generate(prompt)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            cleaned = self._extract_json(raw)
            if cleaned:
                try:
                    return json.loads(cleaned)
                except json.JSONDecodeError:
                    pass
        return {}

    def _extract_list(self, value: Any, *, fallback: List[str] | None = None) -> List[str]:
        if isinstance(value, list):
            return [clean_whitespace(str(item)) for item in value if str(item).strip()]
        if isinstance(value, str):
            items = [part.strip() for part in value.replace("-", "\n").splitlines()]
            return [clean_whitespace(part) for part in items if part]
        return fallback or []

    def _build_offer_prompt(self, analysis: BusinessAnalysis, package: ServicePackage, price: int) -> str:
        tier = SERVICE_TIERS[package]
        subscores: SubScores = analysis.maturity.subscores

        payload = {
            "intro": (
                "أنت استشاري تطوير أعمال في BrainSAIT تعمل مع شركات في المملكة العربية السعودية. "
                "حلل البيانات المقدمة وقدم عرضاً بلغتين (العربية والإنجليزية). يجب أن يكون الإخراج "
                "كائن JSON صالح فقط دون أي نص إضافي."
            ),
            "context": {
                "business_name": analysis.business_name,
                "industry": analysis.industry,
                "location": analysis.location,
                "overall_score": analysis.maturity.overall_score,
                "technical": subscores.technical,
                "seo": subscores.seo,
                "content": subscores.content,
                "trust": subscores.trust,
                "languages": analysis.feature_vector.languages,
                "avg_word_count": round(analysis.feature_vector.avg_word_count, 1),
                "page_titles": [title for title in analysis.web_page_titles if title],
            },
            "service_package": {
                "name": tier.name,
                "price": format_currency(price, self._currency),
                "features": tier.features,
            },
            "response_format": {
                "justification": "string",
                "summary_ar": "string",
                "summary_en": "string",
                "priority_features": ["string"],
                "roi_projection": "string",
                "next_steps": ["string"],
            },
        }

        return (
            "أعد فقط كائن JSON بالتنسيق التالي، ولا تضف أي شرح خارجي:\n\n" + json.dumps(payload, ensure_ascii=False, indent=2)
        )

    def _build_outreach_prompt(self, analysis: BusinessAnalysis, offer: TailoredOffer) -> str:
        tier = SERVICE_TIERS[offer.package_recommendation]
        payload = {
            "instruction": (
                "أنت كاتب رسائل تسويقية في BrainSAIT. أنشئ رسائل مخصصة بالعربية والإنجليزية "
                "واحرص أن يكون الإخراج JSON صالح فقط."
            ),
            "business": {
                "name": analysis.business_name,
                "industry": analysis.industry,
                "location": analysis.location,
            },
            "offer": {
                "package": tier.name,
                "price": format_currency(offer.adjusted_price, self._currency),
                "highlights": truncate_text(offer.justification, max_length=220),
            },
            "response_format": {
                "subject_ar": "string",
                "subject_en": "string",
                "body_ar": "string",
                "body_en": "string",
                "call_to_action": "string",
                "business_details": "string",
            },
        }

        return "أعد كائناً JSON مطابقاً للمخطط التالي دون أي تعليق إضافي:\n\n" + json.dumps(payload, ensure_ascii=False, indent=2)

    def _default_body_ar(self, analysis: BusinessAnalysis, offer: TailoredOffer) -> str:
        tier = SERVICE_TIERS[offer.package_recommendation]
        return (
            f"فريق {analysis.business_name} العزيز،\n\n"
            f"يسر BrainSAIT أن تقدم لكم حزمة {tier.name} بقيمة {format_currency(offer.adjusted_price, self._currency)}."
            " تهدف الحزمة إلى تعزيز حضوركم الرقمي عبر تحسين تجربة الموقع، وتحسين محركات البحث،"
            " وتطوير استراتيجية محتوى متوازنة. يسعدنا ترتيب مكالمة تعريفية لمناقشة التفاصيل." 
        )

    def _default_body_en(self, analysis: BusinessAnalysis, offer: TailoredOffer) -> str:
        tier = SERVICE_TIERS[offer.package_recommendation]
        return (
            f"Dear {analysis.business_name} team,\n\n"
            f"BrainSAIT recommends the {tier.name} package priced at {format_currency(offer.adjusted_price, self._currency)}."
            " The engagement focuses on strengthening your digital presence, SEO foundations,"
            " and content strategy. Let us schedule a discovery call to align on the roadmap."
        )

    @staticmethod
    def _extract_json(text: str) -> str | None:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start : end + 1]
        return None


__all__ = [
    "OfferGenerator",
    "ServicePackage",
    "ServiceTier",
    "IndustryPremium",
    "BusinessAnalysis",
    "TailoredOffer",
    "OutreachMessage",
]
