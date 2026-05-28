"""FASE-ROICRIII-F2: Asset Confidence Enrichment - Tests.

Tests the fix for faq_page and optimization_guide confidence scoring.

Issue: faq_page and optimization_guide were getting confidence=0.5 because:
1. faq_page: lists (FAQs) were treated as UNKNOWN instead of ESTIMATED
2. optimization_guide: required field 'metadata' was never populated by orchestrator

Fix: _evaluate_check in preflight_checks.py now handles list data_points
as ESTIMATED (0.7) when non-empty, instead of UNKNOWN (0.0).
"""

import pytest
from modules.asset_generation.preflight_checks import PreflightChecker, PreflightStatus
from modules.asset_generation.conditional_generator import ConditionalGenerator


class TestFaqPageListConfidence:
    """faq_page with real FAQ list should score as ESTIMATED, not UNKNOWN."""

    def test_faq_list_with_items_gets_estimated_confidence(self):
        """Non-empty list of FAQs should be treated as ESTIMATED (0.7)."""
        checker = PreflightChecker()
        gen = ConditionalGenerator()

        # Real FAQ data as a plain list (not DataPoint wrapper)
        validated_data = {
            "faqs": [
                {"question": "¿Check-in?", "answer": "Desde las 15:00"},
                {"question": "¿Desayuno?", "answer": "Incluido"},
            ]
        }
        # Hotel Castilla Real context (not new hotel)
        hotel_context = {"reviews": 534, "photos": 10, "place_found": True}

        report = checker.check_asset("faq_page", validated_data, hotel_context)
        confidence = gen._calculate_confidence_score(report)

        assert report.overall_status == PreflightStatus.PASSED, (
            f"Expected PASSED, got {report.overall_status}"
        )
        assert report.checks[0].status == PreflightStatus.PASSED
        assert confidence >= 0.7, f"Expected confidence >= 0.7, got {confidence}"
        assert "confidence_score" not in report.warnings

    def test_faq_empty_list_gets_unknown_confidence(self):
        """Empty FAQ list should remain UNKNOWN (0.0), producing WARNING."""
        checker = PreflightChecker()
        gen = ConditionalGenerator()

        validated_data = {"faqs": []}
        hotel_context = {"reviews": 534, "photos": 10, "place_found": True}

        report = checker.check_asset("faq_page", validated_data, hotel_context)
        confidence = gen._calculate_confidence_score(report)

        # Empty list → UNKNOWN → BLOCKED (below 0.5) → converts to WARNING
        assert report.overall_status == PreflightStatus.WARNING
        assert report.can_proceed is True  # block_on_failure=False
        assert confidence == 0.5  # WARNING fallback


class TestOptimizationGuideConfidence:
    """optimization_guide requires 'metadata' field with real SEO data."""

    def test_optimization_guide_with_real_metadata_passes(self):
        """Real metadata dict should be ESTIMATED and pass for established hotels."""
        checker = PreflightChecker()
        gen = ConditionalGenerator()

        validated_data = {
            "metadata": {
                "title": "Hotel Castilla Real",
                "description": "Hotel boutique en Pereira",
                "og_title": "Hotel Castilla Real - Pereira",
            }
        }
        hotel_context = {"reviews": 534, "photos": 10, "place_found": True}

        report = checker.check_asset(
            "optimization_guide", validated_data, hotel_context
        )
        confidence = gen._calculate_confidence_score(report)

        assert report.overall_status == PreflightStatus.PASSED
        assert confidence >= 0.7

    def test_optimization_guide_with_minimal_metadata_fails_threshold(self):
        """Metadata dict with only 1 field should be UNKNOWN (< 0.5 threshold)."""
        checker = PreflightChecker()
        gen = ConditionalGenerator()

        validated_data = {
            "metadata": {"title": "Hotel Castilla Real"}
        }
        hotel_context = {"reviews": 534, "photos": 10, "place_found": True}

        report = checker.check_asset(
            "optimization_guide", validated_data, hotel_context
        )
        confidence = gen._calculate_confidence_score(report)

        # Only 1 non-empty value → UNKNOWN → BLOCKED → WARNING with 0.5
        assert report.overall_status == PreflightStatus.WARNING
        assert confidence == 0.5


class TestConfidenceNotRegressed:
    """Ensure other assets are not affected by the list handling change."""

    def test_hotel_data_dict_still_works(self):
        """hotel_data dict without explicit confidence still gets ESTIMATED heuristic."""
        checker = PreflightChecker()
        gen = ConditionalGenerator()

        validated_data = {
            "hotel_data": {
                "name": "Hotel Test",
                "telephone": "+57 300 123 4567",
                "address": "Calle 10 #5-20",
                "latitude": 4.6,
                "longitude": -75.6,
            }
        }
        hotel_context = {"reviews": 100, "photos": 10, "place_found": True}

        report = checker.check_asset("hotel_schema", validated_data, hotel_context)
        confidence = gen._calculate_confidence_score(report)

        # hotel_data dict with 5 fields → ESTIMATED → 0.7
        assert confidence >= 0.7
