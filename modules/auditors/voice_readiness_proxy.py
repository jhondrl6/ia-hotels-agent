# modules/auditors/voice_readiness_proxy.py
"""Voice readiness assessment proxy for AEO optimization.

Assesses how well a hotel's digital presence is optimized for voice search
based on Google Business Profile completeness, schema markup, featured
snippets, and factual coverage.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class VoiceReadinessResult:
    """Result of voice readiness assessment."""
    score: float
    level: str  # critical, basic, good, excellent
    components: Dict[str, float]
    recommendations: List[str] = field(default_factory=list)
    data_sources: List[str] = field(default_factory=list)
    gbp_completeness: int = 0
    schema_for_voice: int = 0
    featured_snippets: int = 0
    factual_coverage: int = 0


class VoiceReadinessProxy:
    """Proxy for assessing voice search readiness.

    Evaluates four key components:
    - GBP completeness (30 points max)
    - Schema markup for voice (25 points max)
    - Featured snippets optimization (25 points max)
    - Factual coverage (20 points max)
    """

    WEIGHTS = {
        "gbp_completeness": 30,
        "schema_for_voice": 25,
        "featured_snippets": 25,
        "factual_coverage": 20,
    }

    def calculate(
        self,
        audit_result: Dict[str, Any],
        snippet_report: Optional[Dict[str, Any]] = None
    ) -> VoiceReadinessResult:
        """Calculate voice readiness score from audit and optional snippet data.

        Args:
            audit_result: Audit data containing GBP data, schema data, and content analysis.
                         Expected keys: gbp_data, schema_data, content_metrics
            snippet_report: Optional dict with featured snippets data.
                          Expected keys: has_snippets, snippet_quality, entities_covered

        Returns:
            VoiceReadinessResult with score, level, components, recommendations, and data sources.
        """
        gbp_data = audit_result.get("gbp_data", {})
        schema_data = audit_result.get("schema_data", {})
        content_metrics = audit_result.get("content_metrics", {})

        data_sources = ["audit_result"]
        if snippet_report:
            data_sources.append("snippet_report")

        # Assess each component
        gbp_score = self._assess_gbp_completeness(gbp_data)
        schema_score = self._assess_schema_for_voice(schema_data)
        snippet_score = self._assess_featured_snippets(snippet_report or {})
        factual_score = self._assess_factual_coverage(audit_result)

        # Calculate total score
        total = gbp_score + schema_score + snippet_score + factual_score

        # Determine level
        level = self._get_level(total)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            gbp_score, schema_score, snippet_score, factual_score
        )

        components = {
            "gbp_completeness": gbp_score,
            "schema_for_voice": schema_score,
            "featured_snippets": snippet_score,
            "factual_coverage": factual_score,
        }

        return VoiceReadinessResult(
            score=total,
            level=level,
            components=components,
            recommendations=recommendations,
            data_sources=data_sources,
            gbp_completeness=gbp_score,
            schema_for_voice=schema_score,
            featured_snippets=snippet_score,
            factual_coverage=factual_score,
        )

    def _assess_gbp_completeness(self, gbp_data: Dict[str, Any]) -> int:
        """Assess Google Business Profile completeness (max 30 points).

        Scoring based on:
        - NAP consistency and completeness (name, address, phone)
        - Business categories filled
        - Operating hours specified
        - Photos/attributes
        """
        score = 0

        if not gbp_data:
            return 0

        # NAP completeness (12 points max)
        nap_fields = ["name", "address", "phone"]
        nap_complete = sum(1 for f in nap_fields if gbp_data.get(f))
        score += min(nap_complete * 4, 12)

        # Categories (6 points max)
        categories = gbp_data.get("categories", [])
        if categories:
            score += min(len(categories) * 2, 6)

        # Hours (6 points max)
        if gbp_data.get("hours"):
            score += 6

        # Photos/attributes (6 points max)
        has_photos = gbp_data.get("photo_count", 0) >= 3
        has_attributes = bool(gbp_data.get("attributes"))
        score += 3 if has_photos else 0
        score += 3 if has_attributes else 0

        return min(score, 30)

    def _assess_schema_for_voice(self, schema_data: Dict[str, Any]) -> int:
        """Assess schema markup readiness for voice search (max 25 points).

        Scoring based on:
        - Presence of Hotel schema with required fields
        - LocalBusiness schema
        - FAQ schema for direct answers
        - Restaurant/menu schema if applicable
        """
        score = 0

        if not schema_data:
            return 0

        schema_types = schema_data.get("schema_types", [])

        # Hotel or LodgingBusiness schema (10 points max)
        hotel_schema = any(t in schema_types for t in ["Hotel", "LodgingBusiness", "Hostel", "BedAndBreakfast"])
        if hotel_schema:
            score += 10
            # Check for required hotel properties
            required_props = ["name", "address", "telephone", "priceRange"]
            found_props = sum(1 for p in required_props if schema_data.get(p))
            score += min(found_props * 2, 5)

        # LocalBusiness schema (5 points)
        if "LocalBusiness" in schema_types:
            score += 5

        # FAQ schema (5 points max) - important for voice
        faq_schema = schema_data.get("faq_data") or schema_data.get("faqs")
        if faq_schema:
            faq_count = len(faq_schema) if isinstance(faq_schema, list) else 1
            score += min(faq_count, 5)

        # Restaurant schema if applicable (5 points)
        restaurant_schema = any(t in schema_types for t in ["Restaurant", "FoodEstablishment"])
        if restaurant_schema:
            score += 5

        return min(score, 25)

    def _assess_featured_snippets(self, snippet_report: Dict[str, Any]) -> int:
        """Assess featured snippet optimization (max 25 points).

        Scoring based on:
        - Presence of featured snippets
        - Snippet quality and completeness
        - Entity coverage in snippets
        """
        score = 0

        if not snippet_report:
            return 0

        # Has snippets (10 points)
        if snippet_report.get("has_snippets", False):
            score += 10

        # Snippet quality (10 points max)
        snippet_quality = snippet_report.get("snippet_quality", 0)
        if snippet_quality >= 80:
            score += 10
        elif snippet_quality >= 60:
            score += 7
        elif snippet_quality >= 40:
            score += 4
        elif snippet_quality > 0:
            score += 2

        # Entity coverage (5 points max)
        entities_covered = snippet_report.get("entities_covered", 0)
        total_entities = snippet_report.get("total_entities", 1)
        coverage_ratio = entities_covered / max(total_entities, 1)
        score += min(int(coverage_ratio * 5), 5)

        return min(score, 25)

    def _assess_factual_coverage(self, audit_result: Dict[str, Any]) -> int:
        """Assess factual coverage in content (max 20 points).

        Scoring based on:
        - Key facts present (address, phone, hours, prices)
        - Consistency across content
        - Authority signals (citations, references)
        """
        score = 0

        content_metrics = audit_result.get("content_metrics", {})
        gbp_data = audit_result.get("gbp_data", {})
        citations = audit_result.get("citations", [])

        if not content_metrics and not gbp_data:
            return 0

        # Key facts presence (10 points max)
        key_facts = ["address", "phone", "hours", "prices", "amenities"]
        facts_found = sum(
            1 for fact in key_facts
            if content_metrics.get(fact) or gbp_data.get(fact)
        )
        score += min(facts_found * 2, 10)

        # Citations/authority signals (5 points max)
        citation_count = len(citations) if citations else 0
        if citation_count >= 10:
            score += 5
        elif citation_count >= 5:
            score += 3
        elif citation_count >= 1:
            score += 1

        # Content consistency signals (5 points max)
        consistency = content_metrics.get("consistency_score", 0)
        if consistency >= 80:
            score += 5
        elif consistency >= 60:
            score += 3
        elif consistency >= 40:
            score += 1

        return min(score, 20)

    def _get_level(self, score: float) -> str:
        """Determine voice readiness level based on score.

        Levels:
        - critical: 0-25
        - basic: 26-50
        - good: 51-75
        - excellent: 76-100
        """
        if score <= 25:
            return "critical"
        elif score <= 50:
            return "basic"
        elif score <= 75:
            return "good"
        else:
            return "excellent"

    def _generate_recommendations(
        self,
        gbp_score: int,
        schema_score: int,
        snippet_score: int,
        factual_score: int
    ) -> List[str]:
        """Generate recommendations based on component scores."""
        recommendations = []

        # GBP completeness recommendations
        if gbp_score < 20:
            recommendations.append(
                "Complete Google Business Profile: ensure NAP consistency, "
                "add categories, operating hours, and at least 3 photos"
            )
        elif gbp_score < 30:
            recommendations.append(
                "Enhance GBP with additional attributes and photo gallery"
            )

        # Schema recommendations
        if schema_score < 15:
            recommendations.append(
                "Implement Hotel/LodgingBusiness JSON-LD schema with "
                "required properties (name, address, telephone, priceRange)"
            )
        if schema_score < 20:
            recommendations.append(
                "Add FAQ schema to capture voice search direct answers"
            )

        # Featured snippets recommendations
        if snippet_score < 15:
            recommendations.append(
                "Optimize content for featured snippets: use clear "
                "question-answer format, structure with H2/H3 tags"
            )
        if snippet_score < 25:
            recommendations.append(
                "Target long-tail question queries in content to "
                "increase snippet eligibility"
            )

        # Factual coverage recommendations
        if factual_score < 12:
            recommendations.append(
                "Strengthen factual coverage: explicitly state address, "
                "phone, hours, and prices in accessible content"
            )
        if factual_score < 20:
            recommendations.append(
                "Build citation authority through local partnerships "
                "and industry references"
            )

        if not recommendations:
            recommendations.append(
                "Maintain current optimization levels and continue "
                "monitoring voice search performance"
            )

        return recommendations
