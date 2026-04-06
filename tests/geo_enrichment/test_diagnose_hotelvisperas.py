"""Tests for diagnose() method with hotelvisperas real data.

Tests that the diagnostic produces expected score range (34-45)
for the Hotel Visperas website based on its actual data profile.
"""

import pytest
from data_models.canonical_assessment import (
    CanonicalAssessment,
    SiteMetadata,
    SchemaAnalysis,
    PerformanceAnalysis,
    PerformanceMetrics,
    GBPAnalysis,
)
from modules.geo_enrichment import GEODiagnostic, GEOBand


class TestDiagnoseHotelVisperas:
    """Test GEO diagnostic with Hotel Visperas data."""

    @pytest.fixture
    def hotelvisperas_assessment(self):
        """Create a CanonicalAssessment mimicking Hotel Visperas profile.
        
        This represents a typical small boutique hotel with:
        - Basic WordPress site
        - Limited schema
        - Some GBP presence
        - No advanced GEO optimizations
        """
        site_metadata = SiteMetadata(
            title="Hotel Visperas",  # Custom title (not default)
            description="Hotel boutique en el centro histórico de Oaxaca",  # Short description
            cms_detected="WordPress",
            has_default_title=False,
            detected_language="es",
            viewport_meta=True,
        )
        
        schema_analysis = SchemaAnalysis(
            schema_type="Hotel",
            coverage_score=0.45,  # Partial schema coverage
            missing_critical_fields=["amenityFeature", "servesCuisine"],
            present_fields=["Hotel", "address", "geo"],
            raw_schema={
                "type": "Hotel",
                "name": "Hotel Visperas",
                "url": "https://hotelvisperas.com",
            },
            has_hotel_schema=True,
            has_local_business=False,
        )
        
        performance_metrics = PerformanceMetrics(
            lcp=2.8,
            fcp=1.5,
            cls=0.05,
            ttfb=250,
        )
        
        performance_analysis = PerformanceAnalysis(
            performance_score=72.0,
            accessibility_score=80.0,
            metrics=performance_metrics,
        )
        
        gbp_analysis = GBPAnalysis(
            profile_url="https://www.google.com/maps/place/Hotel+Visperas",
            rating=4.5,
            review_count=127,
            photo_count=45,
            is_claimed=True,
            categories=["Hotel", "Boutique hotel"],
            hours_available=True,
            phone_matches=True,
        )
        
        return CanonicalAssessment(
            url="https://hotelvisperas.com",
            site_metadata=site_metadata,
            schema_analysis=schema_analysis,
            performance_analysis=performance_analysis,
            gbp_analysis=gbp_analysis,
        )

    def test_diagnose_returns_assessment(self, hotelvisperas_assessment):
        """Test that diagnose() returns a GEOAssessment object."""
        diagnostic = GEODiagnostic(hotelvisperas_assessment)
        result = diagnostic.diagnose()
        assert result is not None
        assert hasattr(result, 'total_score')
        assert hasattr(result, 'band')
        assert hasattr(result, 'breakdown')

    def test_score_in_expected_range(self, hotelvisperas_assessment):
        """Test that Hotel Visperas scores in expected range (34-45).
        
        This is the expected range based on the hotel's profile:
        - Basic WordPress with custom title (good for SEO)
        - Short meta description (partial)
        - Partial schema (partial)
        - Some GBP data (good)
        - No llms.txt, ai.txt, or advanced GEO files
        """
        diagnostic = GEODiagnostic(hotelvisperas_assessment)
        result = diagnostic.diagnose()
        
        assert 34 <= result.total_score <= 45, (
            f"Expected score between 34-45 for Hotel Visperas, got {result.total_score}"
        )

    def test_band_is_critical_or_foundation(self, hotelvisperas_assessment):
        """Test that Hotel Visperas falls in CRITICAL or FOUNDATION band."""
        diagnostic = GEODiagnostic(hotelvisperas_assessment)
        result = diagnostic.diagnose()
        
        assert result.band in (GEOBand.CRITICAL, GEOBand.FOUNDATION), (
            f"Expected CRITICAL or FOUNDATION band, got {result.band}"
        )

    def test_breakdown_has_all_areas(self, hotelvisperas_assessment):
        """Test that breakdown includes all 8 evaluation areas."""
        diagnostic = GEODiagnostic(hotelvisperas_assessment)
        result = diagnostic.diagnose()
        
        breakdown = result.breakdown
        assert hasattr(breakdown, 'robots')
        assert hasattr(breakdown, 'llms')
        assert hasattr(breakdown, 'schema')
        assert hasattr(breakdown, 'meta')
        assert hasattr(breakdown, 'content')
        assert hasattr(breakdown, 'brand')
        assert hasattr(breakdown, 'signals')
        assert hasattr(breakdown, 'ai_discovery')

    def test_total_matches_breakdown_sum(self, hotelvisperas_assessment):
        """Test that total_score matches sum of breakdown areas."""
        diagnostic = GEODiagnostic(hotelvisperas_assessment)
        result = diagnostic.diagnose()
        
        expected_total = result.breakdown.total()
        assert result.total_score == expected_total

    def test_has_gaps_and_recommendations(self, hotelvisperas_assessment):
        """Test that assessment includes gaps and recommendations."""
        diagnostic = GEODiagnostic(hotelvisperas_assessment)
        result = diagnostic.diagnose()
        
        assert hasattr(result, 'gaps_blocking')
        assert hasattr(result, 'gaps_mitigable')
        assert hasattr(result, 'recommendations')
        
        # Should have gaps since this is a basic site
        assert len(result.gaps_blocking) > 0 or len(result.gaps_mitigable) > 0
        assert len(result.recommendations) > 0

    def test_ai_discovery_area_low_score(self, hotelvisperas_assessment):
        """Test that AI discovery area has low score (no ai.txt, etc)."""
        diagnostic = GEODiagnostic(hotelvisperas_assessment)
        result = diagnostic.diagnose()
        
        # AI discovery max is 6, but without ai.txt files should be low
        assert result.breakdown.ai_discovery <= 2, (
            f"AI discovery score too high: {result.breakdown.ai_discovery}"
        )

    def test_llms_area_partial_score(self, hotelvisperas_assessment):
        """Test that llms area has partial score due to available metadata."""
        diagnostic = GEODiagnostic(hotelvisperas_assessment)
        result = diagnostic.diagnose()
        
        # Should get some points for title and description
        # But missing llms.txt itself
        assert 0 < result.breakdown.llms <= 12, (
            f"LLMS score unexpected: {result.breakdown.llms}"
        )
