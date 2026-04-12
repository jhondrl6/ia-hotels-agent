"""Tests para voice_readiness_proxy.py.

Valida scoring de voice readiness assessment proxy para AEO optimization.
"""
import sys
from pathlib import Path

# Add project root to Python path for pytest
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest

from modules.auditors.voice_readiness_proxy import (
    VoiceReadinessProxy,
    VoiceReadinessResult,
)


class TestVoiceReadinessProxyFullData:
    """Tests with complete data available - should produce high score."""

    def test_voice_readiness_full_data(self):
        """Con todos los datos disponibles → score 70-100."""
        proxy = VoiceReadinessProxy()

        audit_result = {
            "gbp_data": {
                "name": "Hotel Casa de la Paz",
                "address": "Calle 5 #4-63, Armenia, Quindio",
                "phone": "+57 606 123 4567",
                "categories": ["Hotel", "Boutique Hotel", "Spa"],  # 3 cats = 6 pts (max)
                "hours": "24 horas",
                "photo_count": 5,
                "attributes": {"wifi": True, "pool": True},
            },
            "schema_data": {
                "schema_types": ["Hotel", "LocalBusiness", "FAQ"],
                "name": "Hotel Casa de la Paz",
                "address": "Calle 5 #4-63",
                "telephone": "+57 606 123 4567",
                "priceRange": "$$",
                "faq_data": [
                    {"question": "Horario check-in?", "answer": "3:00 PM"},
                    {"question": "Teleno hotel?", "answer": "+57 606 123 4567"},
                    {"question": "Direccion?", "answer": "Calle 5 #4-63"},
                ],
            },
            "content_metrics": {
                "address": True,
                "phone": True,
                "hours": True,
                "prices": True,
                "amenities": True,
                "consistency_score": 85,
            },
            "citations": ["TripAdvisor", "Booking.com", "Google", "a", "b", "c", "d", "e", "f", "g"],
        }

        snippet_report = {
            "has_snippets": True,
            "snippet_quality": 85,
            "entities_covered": 8,
            "total_entities": 10,
        }

        result = proxy.calculate(audit_result, snippet_report)

        # Full data should produce score in 70-100 range
        assert 70 <= result.score <= 100
        assert result.level in ["good", "excellent"]
        assert result.gbp_completeness == 30  # max for GBP (3 cats, hours, photos, attributes)
        assert result.schema_for_voice == 23   # Hotel(10) + props(4) + LocalBusiness(5) + FAQ(3 capped at 5) + Restaurant(0) = 24, actually 10+4+5+4=23
        assert result.featured_snippets > 0
        assert result.factual_coverage > 0

    def test_voice_readiness_full_data_excellent(self):
        """Full data with high quality → excellent level."""
        proxy = VoiceReadinessProxy()

        audit_result = {
            "gbp_data": {
                "name": "Hotel Premium",
                "address": "Av. Bolivar 10-20",
                "phone": "+57 606 999 8888",
                "categories": ["Hotel", "Boutique Hotel", "Spa"],
                "hours": "24 horas",
                "photo_count": 10,
                "attributes": {"wifi": True, "pool": True, "spa": True},
            },
            "schema_data": {
                "schema_types": ["Hotel", "LodgingBusiness", "LocalBusiness", "FAQ", "Restaurant"],
                "name": "Hotel Premium",
                "address": "Av. Bolivar 10-20",
                "telephone": "+57 606 999 8888",
                "priceRange": "$$$",
                "faqs": [
                    {"q": "Check-in?", "a": "3PM"},
                    {"q": "Check-out?", "a": "11AM"},
                    {"q": "Desayuno?", "a": "Incluido"},
                    {"q": "Parking?", "a": "Gratis"},
                ],
            },
            "content_metrics": {
                "address": True,
                "phone": True,
                "hours": True,
                "prices": True,
                "amenities": True,
                "consistency_score": 90,
            },
            "citations": ["a"] * 15,
        }

        snippet_report = {
            "has_snippets": True,
            "snippet_quality": 90,
            "entities_covered": 10,
            "total_entities": 10,
        }

        result = proxy.calculate(audit_result, snippet_report)

        assert result.score == 100
        assert result.level == "excellent"


class TestVoiceReadinessProxyMissingData:
    """Tests with missing data components."""

    def test_voice_readiness_no_gbp(self):
        """Sin GBP data → score bajo (<40)."""
        proxy = VoiceReadinessProxy()

        audit_result = {
            "gbp_data": {},  # Empty GBP
            "schema_data": {
                "schema_types": ["Hotel"],
                "name": "Hotel Test",
            },
            "content_metrics": {
                "address": True,
                "phone": True,
            },
        }

        snippet_report = {
            "has_snippets": True,
            "snippet_quality": 50,
            "entities_covered": 5,
            "total_entities": 10,
        }

        result = proxy.calculate(audit_result, snippet_report)

        # Without GBP, score should be below 40
        assert result.score < 40
        assert result.gbp_completeness == 0
        assert "Google Business Profile" in result.recommendations[0]

    def test_voice_readiness_no_schema(self):
        """Sin schema → score bajo."""
        proxy = VoiceReadinessProxy()

        audit_result = {
            "gbp_data": {
                "name": "Hotel Test",
                "address": "Calle 1",
                "phone": "+57 606 111 2222",
                "categories": ["Hotel"],
            },
            "schema_data": {},  # Empty schema
            "content_metrics": {
                "address": True,
                "phone": True,
            },
        }

        snippet_report = {
            "has_snippets": True,
            "snippet_quality": 50,
            "entities_covered": 5,
            "total_entities": 10,
        }

        result = proxy.calculate(audit_result, snippet_report)

        assert result.schema_for_voice == 0
        assert result.score < 50  # Schema is 25 pts max, so this limits score

    def test_voice_readiness_no_snippets(self):
        """Sin snippet_report → fallback funciona (no crashea)."""
        proxy = VoiceReadinessProxy()

        audit_result = {
            "gbp_data": {
                "name": "Hotel Test",
                "address": "Calle 1",
                "phone": "+57 606 111 2222",
                "categories": ["Hotel"],
                "hours": "24 horas",
                "photo_count": 3,
            },
            "schema_data": {
                "schema_types": ["Hotel", "LocalBusiness"],
                "name": "Hotel Test",
            },
            "content_metrics": {
                "address": True,
                "phone": True,
                "hours": True,
                "consistency_score": 70,
            },
        }

        # snippet_report is None
        result = proxy.calculate(audit_result, snippet_report=None)

        # Should still produce a result, snippet score = 0
        assert isinstance(result, VoiceReadinessResult)
        assert result.featured_snippets == 0
        assert result.score < 100
        assert "snippet_report" not in result.data_sources

    def test_voice_readiness_no_snippets_fallback(self):
        """Sin snippet_report usa fallback - snippet_score = 0."""
        proxy = VoiceReadinessProxy()

        audit_result = {
            "gbp_data": {
                "name": "Hotel Test",
                "address": "Calle 1",
                "phone": "+57 606 111 2222",
                "categories": ["Hotel"],
                "hours": "24 horas",
                "photo_count": 5,
                "attributes": {"wifi": True},
            },
            "schema_data": {
                "schema_types": ["Hotel", "FAQ"],
                "name": "Hotel Test",
                "faq_data": [{"question": "Pregunta?", "answer": "Respuesta?"}],
            },
            "content_metrics": {
                "consistency_score": 80,
            },
            "citations": ["a", "b", "c", "d", "e"],
        }

        result = proxy.calculate(audit_result, snippet_report=None)

        # snippet_score should be 0 since no snippet_report
        assert result.featured_snippets == 0
        assert result.components["featured_snippets"] == 0


class TestVoiceReadinessWeights:
    """Tests for weighted component scoring."""

    def test_voice_readiness_weights_sum_to_100(self):
        """WEIGHTS sum to 100 (30+25+25+20)."""
        proxy = VoiceReadinessProxy()

        total_weight = sum(proxy.WEIGHTS.values())

        assert total_weight == 100

    def test_voice_readiness_weights_components(self):
        """Verifica componentes ponderados correctamente."""
        proxy = VoiceReadinessProxy()

        assert proxy.WEIGHTS["gbp_completeness"] == 30
        assert proxy.WEIGHTS["schema_for_voice"] == 25
        assert proxy.WEIGHTS["featured_snippets"] == 25
        assert proxy.WEIGHTS["factual_coverage"] == 20

    def test_voice_readiness_gbp_weight_30(self):
        """GBP completeness contributes up to 30 points."""
        proxy = VoiceReadinessProxy()

        audit_result = {
            "gbp_data": {
                "name": "Hotel Test",
                "address": "Calle 1",
                "phone": "+57 606 111 2222",
                "categories": ["Hotel", "Boutique", "Spa"],  # 3 categories = 6 pts (max)
                "hours": "24 horas",
                "photo_count": 5,
                "attributes": {"wifi": True},  # Must have at least 1 attribute for +3
            },
            "schema_data": {},
            "content_metrics": {},
        }

        result = proxy.calculate(audit_result)

        # NAP: 3*4=12 + Categories: 3*2=6 + Hours: 6 + Photos: 3 + Attributes: 3 = 30
        assert result.gbp_completeness == 30
        assert result.components["gbp_completeness"] == 30

    def test_voice_readiness_schema_weight_25(self):
        """Schema for voice contributes up to 25 points."""
        proxy = VoiceReadinessProxy()

        audit_result = {
            "gbp_data": {},
            "schema_data": {
                "schema_types": ["Hotel", "LodgingBusiness", "LocalBusiness", "FAQ", "Restaurant"],
                "name": "Hotel Test",
                "address": "Calle 1",
                "telephone": "+57 606 111 2222",
                "priceRange": "$$",
                "faq_data": [
                    {"q": "Pregunta 1?", "a": "Respuesta 1?"},
                    {"q": "Pregunta 2?", "a": "Respuesta 2?"},
                    {"q": "Pregunta 3?", "a": "Respuesta 3?"},
                ],
            },
            "content_metrics": {},
        }

        result = proxy.calculate(audit_result)

        # Hotel + required props + LocalBusiness + FAQ(3) + Restaurant = max 25
        assert result.schema_for_voice == 25

    def test_voice_readiness_snippet_weight_25(self):
        """Featured snippets contributes up to 25 points."""
        proxy = VoiceReadinessProxy()

        audit_result = {"gbp_data": {}, "schema_data": {}, "content_metrics": {}}

        snippet_report = {
            "has_snippets": True,
            "snippet_quality": 90,  # +10
            "entities_covered": 10,
            "total_entities": 10,  # 100% → +5
        }

        result = proxy.calculate(audit_result, snippet_report)

        # has_snippets(10) + quality>=80(10) + 100% entity coverage(5) = 25
        assert result.featured_snippets == 25

    def test_voice_readiness_factual_weight_20(self):
        """Factual coverage contributes up to 20 points."""
        proxy = VoiceReadinessProxy()

        audit_result = {
            "gbp_data": {
                "address": True,
                "phone": True,
                "hours": True,
                "prices": True,
                "amenities": True,
            },
            "schema_data": {},
            "content_metrics": {
                "address": True,
                "phone": True,
                "hours": True,
                "prices": True,
                "amenities": True,
                "consistency_score": 90,
            },
            "citations": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
        }

        result = proxy.calculate(audit_result)

        # 5 key facts * 2 = 10 pts + citations>=10 = 5 pts + consistency>=80 = 5 pts = 20
        assert result.factual_coverage == 20


class TestVoiceReadinessLevels:
    """Tests for score level determination."""

    def test_voice_readiness_level_critical(self):
        """Score 0-25 → critical level."""
        proxy = VoiceReadinessProxy()

        audit_result = {
            "gbp_data": {},
            "schema_data": {},
            "content_metrics": {},
        }

        result = proxy.calculate(audit_result, snippet_report=None)

        assert result.score <= 25
        assert result.level == "critical"

    def test_voice_readiness_level_basic(self):
        """Score 26-50 → basic level."""
        proxy = VoiceReadinessProxy()

        audit_result = {
            "gbp_data": {
                "name": "Hotel Test",
                "address": "Calle 1",
                "phone": "+57 606 111 2222",
                "categories": ["Hotel"],
            },
            "schema_data": {
                "schema_types": ["Hotel"],
            },
            "content_metrics": {},
        }

        result = proxy.calculate(audit_result)

        # GBP: 3 fields * 4 = 12, categories = 2, no hours, no photos = 14 pts
        # Schema: Hotel present = 10 pts
        # Total ~24-30 pts → basic
        assert 26 <= result.score <= 50
        assert result.level == "basic"

    def test_voice_readiness_level_good(self):
        """Score 51-75 → good level."""
        proxy = VoiceReadinessProxy()

        audit_result = {
            "gbp_data": {
                "name": "Hotel Test",
                "address": "Calle 1",
                "phone": "+57 606 111 2222",
                "categories": ["Hotel", "Boutique"],
                "hours": "24 horas",
                "photo_count": 3,
                "attributes": {"wifi": True},
            },
            "schema_data": {
                "schema_types": ["Hotel", "LocalBusiness"],
                "name": "Hotel Test",
                "address": "Calle 1",
                "telephone": "+57 606 111 2222",
                "priceRange": "$$",
            },
            "content_metrics": {
                "address": True,
                "phone": True,
                "hours": True,
                "consistency_score": 60,
            },
        }

        snippet_report = {
            "has_snippets": True,
            "snippet_quality": 50,
            "entities_covered": 5,
            "total_entities": 10,
        }

        result = proxy.calculate(audit_result, snippet_report)

        # GBP: 12 + 4 + 6 + 3 + 3 = 28 pts
        # Schema: Hotel(10) + props(4) + LocalBusiness(5) = 19 pts
        # Snippets: has(10) + quality>=40(4) + 50% coverage(2) = 16 pts
        # Factual: 4 facts * 2 = 8 + consistency>=60(3) = 11 pts
        # Total ~74 pts → good
        assert 51 <= result.score <= 75
        assert result.level == "good"

    def test_voice_readiness_level_excellent(self):
        """Score 76-100 → excellent level."""
        proxy = VoiceReadinessProxy()

        audit_result = {
            "gbp_data": {
                "name": "Hotel Test",
                "address": "Calle 1",
                "phone": "+57 606 111 2222",
                "categories": ["Hotel", "Boutique", "Spa"],
                "hours": "24 horas",
                "photo_count": 10,
                "attributes": {"wifi": True, "pool": True, "spa": True},
            },
            "schema_data": {
                "schema_types": ["Hotel", "LodgingBusiness", "LocalBusiness", "FAQ", "Restaurant"],
                "name": "Hotel Test",
                "address": "Calle 1",
                "telephone": "+57 606 111 2222",
                "priceRange": "$$$",
                "faqs": [
                    {"q": "Pregunta 1?", "a": "Respuesta 1?"},
                    {"q": "Pregunta 2?", "a": "Respuesta 2?"},
                    {"q": "Pregunta 3?", "a": "Respuesta 3?"},
                ],
            },
            "content_metrics": {
                "address": True,
                "phone": True,
                "hours": True,
                "prices": True,
                "amenities": True,
                "consistency_score": 90,
            },
            "citations": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
        }

        snippet_report = {
            "has_snippets": True,
            "snippet_quality": 90,
            "entities_covered": 10,
            "total_entities": 10,
        }

        result = proxy.calculate(audit_result, snippet_report)

        assert 76 <= result.score <= 100
        assert result.level == "excellent"

    def test_voice_readiness_level_boundaries(self):
        """Test boundary conditions for levels."""
        proxy = VoiceReadinessProxy()

        # Test exact boundary: 25 → critical
        result = proxy.calculate({"gbp_data": {}, "schema_data": {}, "content_metrics": {}})
        assert result.level == "critical"

        # Test exact boundary: 76 → excellent
        audit_result = {
            "gbp_data": {
                "name": "H", "address": "A", "phone": "P",
                "categories": ["Hotel", "Boutique", "Spa"],
                "hours": "24h", "photo_count": 10,
                "attributes": {"w": True, "p": True, "s": True},
            },
            "schema_data": {
                "schema_types": ["Hotel", "LodgingBusiness", "LocalBusiness", "FAQ", "Restaurant"],
                "name": "H", "address": "A", "telephone": "P", "priceRange": "$$$",
                "faqs": [{"q": "1", "a": "1"}, {"q": "2", "a": "2"}, {"q": "3", "a": "3"}],
            },
            "content_metrics": {
                "address": True, "phone": True, "hours": True,
                "prices": True, "amenities": True, "consistency_score": 90,
            },
            "citations": list("abcdefghij"),
        }
        snippet_report = {"has_snippets": True, "snippet_quality": 90, "entities_covered": 10, "total_entities": 10}
        result = proxy.calculate(audit_result, snippet_report)
        assert result.level == "excellent"


class TestVoiceReadinessEdgeCases:
    """Edge case tests."""

    def test_empty_audit_result(self):
        """Empty audit_result returns zero score."""
        proxy = VoiceReadinessProxy()

        result = proxy.calculate({})

        assert result.score == 0
        assert result.level == "critical"

    def test_partial_gbp_data(self):
        """Partial GBP data is scored proportionally."""
        proxy = VoiceReadinessProxy()

        audit_result = {
            "gbp_data": {
                "name": "Hotel Test",
                # Missing address and phone
            },
            "schema_data": {},
            "content_metrics": {},
        }

        result = proxy.calculate(audit_result)

        # Only name field: 1 * 4 = 4 pts for NAP
        assert result.gbp_completeness == 4

    def test_snippet_quality_thresholds(self):
        """Snippet quality scoring thresholds work correctly."""
        proxy = VoiceReadinessProxy()

        base_audit = {"gbp_data": {}, "schema_data": {}, "content_metrics": {}}

        # Quality >= 80 → +10
        sr = {"has_snippets": True, "snippet_quality": 80, "entities_covered": 10, "total_entities": 10}
        r1 = proxy.calculate(base_audit, sr)
        assert r1.featured_snippets == 25  # 10 + 10 + 5

        # 60 <= quality < 80 → +7
        sr = {"has_snippets": True, "snippet_quality": 60, "entities_covered": 10, "total_entities": 10}
        r2 = proxy.calculate(base_audit, sr)
        assert r2.featured_snippets == 22  # 10 + 7 + 5

        # 40 <= quality < 60 → +4
        sr = {"has_snippets": True, "snippet_quality": 40, "entities_covered": 10, "total_entities": 10}
        r3 = proxy.calculate(base_audit, sr)
        assert r3.featured_snippets == 19  # 10 + 4 + 5

        # 0 < quality < 40 → +2
        sr = {"has_snippets": True, "snippet_quality": 20, "entities_covered": 10, "total_entities": 10}
        r4 = proxy.calculate(base_audit, sr)
        assert r4.featured_snippets == 17  # 10 + 2 + 5

    def test_data_sources_tracked(self):
        """data_sources tracks which inputs were used."""
        proxy = VoiceReadinessProxy()

        audit_result = {"gbp_data": {}, "schema_data": {}, "content_metrics": {}}

        result_no_snippets = proxy.calculate(audit_result)
        assert "audit_result" in result_no_snippets.data_sources
        assert len(result_no_snippets.data_sources) == 1

        result_with_snippets = proxy.calculate(audit_result, {"has_snippets": True, "snippet_quality": 50})
        assert "audit_result" in result_with_snippets.data_sources
        assert "snippet_report" in result_with_snippets.data_sources


class TestVoiceReadinessResult:
    """Tests for VoiceReadinessResult dataclass."""

    def test_result_creation(self):
        """Verify VoiceReadinessResult can be created."""
        result = VoiceReadinessResult(
            score=75.0,
            level="good",
            components={"gbp": 30, "schema": 20, "snippets": 15, "factual": 10},
            recommendations=["Rec 1", "Rec 2"],
            data_sources=["audit_result", "snippet_report"],
            gbp_completeness=30,
            schema_for_voice=20,
            featured_snippets=15,
            factual_coverage=10,
        )

        assert result.score == 75.0
        assert result.level == "good"
        assert len(result.components) == 4
        assert len(result.recommendations) == 2
        assert len(result.data_sources) == 2
