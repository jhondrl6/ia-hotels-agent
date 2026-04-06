"""Tests for GEOBand classification correctness.

Tests that various score scenarios correctly map to the appropriate
GEO bands according to the defined thresholds.
"""

import pytest
from data_models.canonical_assessment import (
    CanonicalAssessment,
    SiteMetadata,
    SchemaAnalysis,
    PerformanceAnalysis,
    PerformanceMetrics,
)
from modules.geo_enrichment import GEODiagnostic, GEOBand, ScoreBreakdown


class TestBandClassification:
    """Test GEOBand classification accuracy."""

    def _create_minimal_assessment(self) -> CanonicalAssessment:
        """Create a minimal assessment for testing."""
        return CanonicalAssessment(
            url="https://example.com",
            site_metadata=SiteMetadata(
                title="Test Hotel",
                description="Test description",
                has_default_title=False,
            ),
            schema_analysis=SchemaAnalysis(
                coverage_score=0.0,
                has_hotel_schema=False,
            ),
            performance_analysis=PerformanceAnalysis(
                performance_score=50.0,
            ),
        )

    def test_score_100_is_excellent(self):
        """Test that maximum score 100 maps to EXCELLENT."""
        assessment = self._create_minimal_assessment()
        diagnostic = GEODiagnostic(assessment)
        assessment.schema_analysis.coverage_score = 1.0
        
        # We can't easily set total to 100 without modifying the logic
        # So we test the from_score method directly
        band = GEOBand.from_score(100)
        assert band == GEOBand.EXCELLENT

    def test_score_86_is_excellent(self):
        """Test that score 86 maps to EXCELLENT (lower threshold)."""
        band = GEOBand.from_score(86)
        assert band == GEOBand.EXCELLENT

    def test_score_85_is_good(self):
        """Test that score 85 maps to GOOD (one below EXCELLENT threshold)."""
        band = GEOBand.from_score(85)
        assert band == GEOBand.GOOD

    def test_score_68_is_good(self):
        """Test that score 68 maps to GOOD (lower threshold)."""
        band = GEOBand.from_score(68)
        assert band == GEOBand.GOOD

    def test_score_67_is_foundation(self):
        """Test that score 67 maps to FOUNDATION (one below GOOD threshold)."""
        band = GEOBand.from_score(67)
        assert band == GEOBand.FOUNDATION

    def test_score_36_is_foundation(self):
        """Test that score 36 maps to FOUNDATION (lower threshold)."""
        band = GEOBand.from_score(36)
        assert band == GEOBand.FOUNDATION

    def test_score_35_is_critical(self):
        """Test that score 35 maps to CRITICAL (one below FOUNDATION threshold)."""
        band = GEOBand.from_score(35)
        assert band == GEOBand.CRITICAL

    def test_score_0_is_critical(self):
        """Test that score 0 maps to CRITICAL (minimum)."""
        band = GEOBand.from_score(0)
        assert band == GEOBand.CRITICAL

    def test_score_50_is_foundation(self):
        """Test that mid-range score 50 maps to FOUNDATION."""
        band = GEOBand.from_score(50)
        assert band == GEOBand.FOUNDATION

    def test_score_75_is_good(self):
        """Test that upper-mid range score 75 maps to GOOD."""
        band = GEOBand.from_score(75)
        assert band == GEOBand.GOOD

    def test_score_90_is_excellent(self):
        """Test that high score 90 maps to EXCELLENT."""
        band = GEOBand.from_score(90)
        assert band == GEOBand.EXCELLENT

    def test_score_20_is_critical(self):
        """Test that low score 20 maps to CRITICAL."""
        band = GEOBand.from_score(20)
        assert band == GEOBand.CRITICAL

    def test_diagnose_band_matches_score(self):
        """Test that diagnose() band matches from_score() calculation."""
        assessment = self._create_minimal_assessment()
        assessment.site_metadata.has_default_title = False
        
        # Set up a high-scoring scenario
        assessment.site_metadata.description = "A" * 100
        assessment.schema_analysis.has_hotel_schema = True
        assessment.schema_analysis.present_fields = ["Hotel", "amenityFeature", "aggregateRating"]
        assessment.schema_analysis.raw_schema = {
            "name": "Test Hotel",
            "url": "https://example.com",
            "telephone": "+1234567890",
            "address": {"street": "123 Main St"},
        }
        assessment.gbp_analysis = None
        
        diagnostic = GEODiagnostic(assessment)
        result = diagnostic.diagnose()
        
        expected_band = GEOBand.from_score(result.total_score)
        assert result.band == expected_band

    def test_band_enum_has_all_four_values(self):
        """Test that GEOBand enum has exactly 4 values."""
        values = list(GEOBand)
        assert len(values) == 4
        assert GEOBand.EXCELLENT in values
        assert GEOBand.GOOD in values
        assert GEOBand.FOUNDATION in values
        assert GEOBand.CRITICAL in values

    def test_all_bands_are_unique(self):
        """Test that all band values are unique strings."""
        values = [b.value for b in GEOBand]
        assert len(values) == len(set(values))


class TestScoreBreakdownIntegration:
    """Test ScoreBreakdown with band classification integration."""

    def test_breakdown_total_with_specific_scores(self):
        """Test that specific score combinations produce expected bands."""
        # Test EXCELLENT range
        breakdown = ScoreBreakdown(
            robots=18, llms=18, schema=14, meta=12,
            content=10, brand=8, signals=5, ai_discovery=5,
        )
        total = breakdown.total()
        assert total == 90
        assert GEOBand.from_score(total) == GEOBand.EXCELLENT

    def test_good_range_breakdown(self):
        """Test a GOOD range breakdown."""
        breakdown = ScoreBreakdown(
            robots=15, llms=14, schema=12, meta=10,
            content=8, brand=6, signals=3, ai_discovery=3,
        )
        total = breakdown.total()
        assert total == 71
        assert GEOBand.from_score(total) == GEOBand.GOOD

    def test_foundation_range_breakdown(self):
        """Test a FOUNDATION range breakdown."""
        breakdown = ScoreBreakdown(
            robots=10, llms=8, schema=6, meta=4,
            content=3, brand=2, signals=2, ai_discovery=1,
        )
        total = breakdown.total()
        assert total == 36
        assert GEOBand.from_score(total) == GEOBand.FOUNDATION

    def test_critical_range_breakdown(self):
        """Test a CRITICAL range breakdown."""
        breakdown = ScoreBreakdown(
            robots=3, llms=3, schema=2, meta=2,
            content=1, brand=1, signals=0, ai_discovery=0,
        )
        total = breakdown.total()
        assert total == 12
        assert GEOBand.from_score(total) == GEOBand.CRITICAL
