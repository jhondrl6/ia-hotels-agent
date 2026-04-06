"""Tests for GEO Dashboard Generator - FASE-3 validation."""

import pytest

from data_models.canonical_assessment import (
    CanonicalAssessment, SiteMetadata, GBPAnalysis,
    SchemaAnalysis, PerformanceAnalysis, PerformanceMetrics
)
from modules.geo_enrichment.geo_dashboard import GEODashboard
from modules.geo_enrichment.geo_diagnostic import GEOAssessment, ScoreBreakdown, GEOBand


def _create_mock_hotel_data() -> CanonicalAssessment:
    """Create mock CanonicalAssessment for testing."""
    return CanonicalAssessment(
        url="https://hotelvisperas.com",
        name="Hotel Visperas",
        site_metadata=SiteMetadata(
            title="Hotel Visperas - Boutique",
            description="Hotel boutique con encanto colonial en el centro histórico",
            has_default_title=False,
            cms_detected="WordPress",
        ),
        schema_analysis=SchemaAnalysis(
            schema_type="Hotel",
            coverage_score=0.75,
            missing_critical_fields=[],
            present_fields=["name", "address"],
            raw_schema={"@type": "Hotel", "name": "Hotel Visperas"},
            has_hotel_schema=True,
            has_local_business=False,
        ),
        performance_analysis=PerformanceAnalysis(
            performance_score=65,
            accessibility_score=80,
            metrics=PerformanceMetrics(lcp=3.2, fcp=2.0, cls=0.15, ttfb=800),
            severity="high",
            has_critical_issues=False,
        ),
        gbp_analysis=GBPAnalysis(
            profile_url="https://business.google.com/hotelvisperas",
            categories=["Hotel", "Boutique Hotel", "Alojamiento"],
        ),
    )


def _create_geo_assessment(band: GEOBand, gaps_blocking=None, gaps_mitigable=None, recommendations=None) -> GEOAssessment:
    """Create mock GEOAssessment."""
    scores = {
        GEOBand.EXCELLENT: ScoreBreakdown(robots=17, llms=17, schema=15, meta=13, content=11, brand=9, signals=5, ai_discovery=5),
        GEOBand.GOOD: ScoreBreakdown(robots=14, llms=14, schema=12, meta=10, content=9, brand=7, signals=4, ai_discovery=3),
        GEOBand.FOUNDATION: ScoreBreakdown(robots=8, llms=9, schema=7, meta=6, content=5, brand=4, signals=2, ai_discovery=1),
        GEOBand.CRITICAL: ScoreBreakdown(robots=3, llms=2, schema=2, meta=2, content=1, brand=1, signals=0, ai_discovery=0),
    }
    
    return GEOAssessment(
        site_url="https://hotelvisperas.com",
        total_score=scores[band].total(),
        band=band,
        breakdown=scores[band],
        details={},
        gaps_blocking=gaps_blocking or [],
        gaps_mitigable=gaps_mitigable or [],
        recommendations=recommendations or ["Generate llms.txt with GEOEnrichmentLayer"],
    )


class TestGEODashboardFull:
    """Test full dashboard generation."""

    def test_generates_full_dashboard(self):
        """Full dashboard should generate valid markdown."""
        dashboard = GEODashboard()
        hotel_data = _create_mock_hotel_data()
        geo_assessment = _create_geo_assessment(GEOBand.GOOD)
        
        output = dashboard.generate_full(hotel_data, geo_assessment)
        
        assert output is not None
        assert len(output) > 0

    def test_full_dashboard_has_title(self):
        """Full dashboard should have title."""
        dashboard = GEODashboard()
        hotel_data = _create_mock_hotel_data()
        geo_assessment = _create_geo_assessment(GEOBand.GOOD)
        
        output = dashboard.generate_full(hotel_data, geo_assessment)
        
        assert "# GEO Dashboard" in output

    def test_full_dashboard_has_hotel_name(self):
        """Full dashboard should include hotel name."""
        dashboard = GEODashboard()
        hotel_data = _create_mock_hotel_data()
        geo_assessment = _create_geo_assessment(GEOBand.GOOD)
        
        output = dashboard.generate_full(hotel_data, geo_assessment)
        
        assert "Hotel Visperas" in output

    def test_full_dashboard_has_band_label(self):
        """Full dashboard should show band label."""
        dashboard = GEODashboard()
        hotel_data = _create_mock_hotel_data()
        geo_assessment = _create_geo_assessment(GEOBand.GOOD)
        
        output = dashboard.generate_full(hotel_data, geo_assessment)
        
        assert "GOOD" in output or "BUENO" in output

    def test_full_dashboard_has_breakdown_table(self):
        """Full dashboard should have breakdown table."""
        dashboard = GEODashboard()
        hotel_data = _create_mock_hotel_data()
        geo_assessment = _create_geo_assessment(GEOBand.GOOD)
        
        output = dashboard.generate_full(hotel_data, geo_assessment)
        
        assert "## Breakdown por Área" in output
        assert "Robots.txt" in output or "robots" in output

    def test_full_dashboard_shows_score(self):
        """Full dashboard should display score."""
        dashboard = GEODashboard()
        hotel_data = _create_mock_hotel_data()
        geo_assessment = _create_geo_assessment(GEOBand.GOOD)
        
        output = dashboard.generate_full(hotel_data, geo_assessment)
        
        assert "Score GEO" in output
        assert "/" in output  # Score format 73/100


class TestGEODashboardMinimal:
    """Test minimal dashboard generation for EXCELLENT band."""

    def test_generates_minimal_dashboard(self):
        """Minimal dashboard should generate valid markdown."""
        dashboard = GEODashboard()
        hotel_data = _create_mock_hotel_data()
        geo_assessment = _create_geo_assessment(GEOBand.EXCELLENT)
        
        output = dashboard.generate_minimal(hotel_data, geo_assessment)
        
        assert output is not None
        assert len(output) > 0

    def test_minimal_dashboard_has_title(self):
        """Minimal dashboard should have title."""
        dashboard = GEODashboard()
        hotel_data = _create_mock_hotel_data()
        geo_assessment = _create_geo_assessment(GEOBand.EXCELLENT)
        
        output = dashboard.generate_minimal(hotel_data, geo_assessment)
        
        assert "# GEO Dashboard" in output

    def test_minimal_shows_excellent_status(self):
        """Minimal dashboard should show EXCELLENT status."""
        dashboard = GEODashboard()
        hotel_data = _create_mock_hotel_data()
        geo_assessment = _create_geo_assessment(GEOBand.EXCELLENT)
        
        output = dashboard.generate_minimal(hotel_data, geo_assessment)
        
        assert "Excelente" in output or "EXCELLENT" in output

    def test_minimal_has_fewer_sections(self):
        """Minimal dashboard should have fewer sections than full."""
        dashboard = GEODashboard()
        hotel_data = _create_mock_hotel_data()
        geo_excellent = _create_geo_assessment(GEOBand.EXCELLENT)
        geo_good = _create_geo_assessment(GEOBand.GOOD)
        
        minimal_output = dashboard.generate_minimal(hotel_data, geo_excellent)
        full_output = dashboard.generate_full(hotel_data, geo_good)
        
        # Minimal should have fewer section headers
        minimal_headers = minimal_output.count("## ")
        full_headers = full_output.count("## ")
        
        assert minimal_headers < full_headers


class TestGEODashboardBands:
    """Test dashboard generation for different bands."""

    def test_critical_band_shows_urgency(self):
        """CRITICAL dashboard should show urgency."""
        dashboard = GEODashboard()
        hotel_data = _create_mock_hotel_data()
        geo_assessment = _create_geo_assessment(
            GEOBand.CRITICAL,
            gaps_blocking=["Critical gap 1"],
            recommendations=["Fix critical issue immediately"]
        )
        
        output = dashboard.generate_full(hotel_data, geo_assessment)
        
        assert "CRITICO" in output or "CRITICAL" in output

    def test_critical_shows_gaps_when_present(self):
        """Dashboard should show gaps when present."""
        dashboard = GEODashboard()
        hotel_data = _create_mock_hotel_data()
        geo_assessment = _create_geo_assessment(
            GEOBand.CRITICAL,
            gaps_blocking=["Gap blocking 1", "Gap blocking 2"],
        )
        
        output = dashboard.generate_full(hotel_data, geo_assessment)
        
        assert "Gaps" in output or "Gap" in output

    def test_excellent_band_shows_positive_message(self):
        """EXCELLENT dashboard should show positive message."""
        dashboard = GEODashboard()
        hotel_data = _create_mock_hotel_data()
        geo_assessment = _create_geo_assessment(GEOBand.EXCELLENT)
        
        output = dashboard.generate_full(hotel_data, geo_assessment)
        
        # Should have positive indicator
        assert "EXCELENTE" in output or "Excelente" in output


class TestGEODashboardProgressBars:
    """Test progress bar rendering."""

    def test_render_bar_returns_string(self):
        """_render_bar should return a string."""
        dashboard = GEODashboard()
        
        bar = dashboard._render_bar(75)
        
        assert isinstance(bar, str)
        assert "[" in bar
        assert "]" in bar

    def test_render_bar_0_percent(self):
        """_render_bar with 0% should show empty bar."""
        dashboard = GEODashboard()
        
        bar = dashboard._render_bar(0)
        
        assert "░" in bar

    def test_render_bar_100_percent(self):
        """_render_bar with 100% should show full bar."""
        dashboard = GEODashboard()
        
        bar = dashboard._render_bar(100)
        
        assert "█" in bar
