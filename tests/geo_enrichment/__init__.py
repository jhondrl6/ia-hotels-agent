"""Tests for GEO Enrichment Layer - FASE-3 validation.

These tests verify the conditional generation of GEO assets by band.
"""

import pytest
import json
import tempfile
from pathlib import Path

from data_models.canonical_assessment import (
    CanonicalAssessment, SiteMetadata, GBPAnalysis,
    SchemaAnalysis, PerformanceAnalysis, PerformanceMetrics
)
from modules.geo_enrichment.geo_enrichment_layer import (
    GEOEnrichmentLayer,
    GEOBand,
    FILENAME_GEO_BADGE,
    FILENAME_GEO_DASHBOARD_MIN,
    FILENAME_GEO_DASHBOARD,
    FILENAME_GEO_CHECKLIST_MIN,
    FILENAME_LLMS_TXT,
    FILENAME_HOTEL_SCHEMA_RICH,
    FILENAME_FAQ_SCHEMA,
    FILENAME_GEO_FIX_KIT,
)
from modules.geo_enrichment.geo_diagnostic import GEOAssessment, ScoreBreakdown


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


def _create_geo_assessment(band: GEOBand) -> GEOAssessment:
    """Create mock GEOAssessment with specified band."""
    scores = {
        GEOBand.EXCELLENT: ScoreBreakdown(
            robots=17, llms=17, schema=15, meta=13, content=11, brand=9, signals=5, ai_discovery=5
        ),
        GEOBand.GOOD: ScoreBreakdown(
            robots=14, llms=14, schema=12, meta=10, content=9, brand=7, signals=4, ai_discovery=3
        ),
        GEOBand.FOUNDATION: ScoreBreakdown(
            robots=8, llms=9, schema=7, meta=6, content=5, brand=4, signals=2, ai_discovery=1
        ),
        GEOBand.CRITICAL: ScoreBreakdown(
            robots=3, llms=2, schema=2, meta=2, content=1, brand=1, signals=0, ai_discovery=0
        ),
    }
    
    breakdowns = scores[band]
    total = breakdowns.total()
    
    return GEOAssessment(
        site_url="https://hotelvisperas.com",
        total_score=total,
        band=band,
        breakdown=breakdowns,
        details={},
        gaps_blocking=[f"Gap blocking for {band.value}"],
        gaps_mitigable=[f"Gap mitigable for {band.value}"],
        recommendations=[f"Recommendation for {band.value}"],
    )


class TestEnrichmentLayerEXCELLENT:
    """Test EXCELLENT band (86-100) generates minimal assets."""
    
    def test_excellent_generates_badge_and_min_dashboard(self):
        """EXCELLENT band should generate only 2 files: geo_badge.md + geo_dashboard_min.md."""
        layer = GEOEnrichmentLayer()
        hotel_data = _create_mock_hotel_data()
        geo_assessment = _create_geo_assessment(GEOBand.EXCELLENT)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            generated = layer.generate(hotel_data, geo_assessment, tmpdir)
            
            assert len(generated) == 2, f"EXCELLENT should generate 2 files, got {len(generated)}: {generated}"
            
            # Check file names
            filenames = [Path(f).name for f in generated]
            assert FILENAME_GEO_BADGE in filenames
            assert FILENAME_GEO_DASHBOARD_MIN in filenames
    
    def test_excellent_does_not_generate_llms(self):
        """EXCELLENT band should NOT generate llms.txt."""
        layer = GEOEnrichmentLayer()
        hotel_data = _create_mock_hotel_data()
        geo_assessment = _create_geo_assessment(GEOBand.EXCELLENT)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            generated = layer.generate(hotel_data, geo_assessment, tmpdir)
            filenames = [Path(f).name for f in generated]
            
            assert FILENAME_LLMS_TXT not in filenames


class TestEnrichmentLayerGOOD:
    """Test GOOD band (68-85) generates light assets."""
    
    def test_good_generates_three_files(self):
        """GOOD band should generate 3 files."""
        layer = GEOEnrichmentLayer()
        hotel_data = _create_mock_hotel_data()
        geo_assessment = _create_geo_assessment(GEOBand.GOOD)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            generated = layer.generate(hotel_data, geo_assessment, tmpdir)
            
            assert len(generated) == 3, f"GOOD should generate 3 files, got {len(generated)}: {generated}"
            
            filenames = [Path(f).name for f in generated]
            assert FILENAME_GEO_BADGE in filenames
            assert FILENAME_GEO_DASHBOARD in filenames
            assert FILENAME_GEO_CHECKLIST_MIN in filenames
    
    def test_good_does_not_generate_llms(self):
        """GOOD band should NOT generate llms.txt."""
        layer = GEOEnrichmentLayer()
        hotel_data = _create_mock_hotel_data()
        geo_assessment = _create_geo_assessment(GEOBand.GOOD)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            generated = layer.generate(hotel_data, geo_assessment, tmpdir)
            filenames = [Path(f).name for f in generated]
            
            assert FILENAME_LLMS_TXT not in filenames


class TestEnrichmentLayerFOUNDATION:
    """Test FOUNDATION band (36-67) generates full assets."""
    
    def test_foundation_generates_seven_files(self):
        """FOUNDATION band should generate 7 files."""
        layer = GEOEnrichmentLayer()
        hotel_data = _create_mock_hotel_data()
        geo_assessment = _create_geo_assessment(GEOBand.FOUNDATION)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            generated = layer.generate(hotel_data, geo_assessment, tmpdir)
            
            assert len(generated) == 7, f"FOUNDATION should generate 7 files, got {len(generated)}: {generated}"
            
            filenames = [Path(f).name for f in generated]
            assert FILENAME_GEO_BADGE in filenames
            assert FILENAME_GEO_DASHBOARD in filenames
            assert FILENAME_GEO_CHECKLIST_MIN in filenames
            assert FILENAME_LLMS_TXT in filenames
            assert FILENAME_HOTEL_SCHEMA_RICH in filenames
            assert FILENAME_FAQ_SCHEMA in filenames
            assert FILENAME_GEO_FIX_KIT in filenames
    
    def test_foundation_llms_content_valid(self):
        """FOUNDATION llms.txt should have valid content."""
        layer = GEOEnrichmentLayer()
        hotel_data = _create_mock_hotel_data()
        geo_assessment = _create_geo_assessment(GEOBand.FOUNDATION)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            generated = layer.generate(hotel_data, geo_assessment, tmpdir)
            
            llms_path = Path(tmpdir) / "geo_enriched" / FILENAME_LLMS_TXT
            content = llms_path.read_text(encoding="utf-8")
            
            assert "# Hotel Visperas" in content
            assert "https://hotelvisperas.com" in content


class TestEnrichmentLayerCRITICAL:
    """Test CRITICAL band (0-35) generates full + urgent assets."""
    
    def test_critical_generates_nine_files(self):
        """CRITICAL band should generate 9 files (7 from FOUNDATION + 2 urgent)."""
        layer = GEOEnrichmentLayer()
        hotel_data = _create_mock_hotel_data()
        geo_assessment = _create_geo_assessment(GEOBand.CRITICAL)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            generated = layer.generate(hotel_data, geo_assessment, tmpdir)
            
            assert len(generated) >= 9, f"CRITICAL should generate 9+ files, got {len(generated)}: {generated}"
            
            filenames = [Path(f).name for f in generated]
            assert "robots_fix.txt" in filenames
            assert "seo_fix_kit.md" in filenames


class TestEnrichmentLayerOutputStructure:
    """Test output directory structure."""
    
    def test_files_created_in_geo_enriched_subdirectory(self):
        """All files should be created in geo_enriched/ subdirectory."""
        layer = GEOEnrichmentLayer()
        hotel_data = _create_mock_hotel_data()
        geo_assessment = _create_geo_assessment(GEOBand.GOOD)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            generated = layer.generate(hotel_data, geo_assessment, tmpdir)
            
            for filepath in generated:
                path = Path(filepath)
                assert path.parts[-2] == "geo_enriched", f"File {filepath} not in geo_enriched/"
    
    def test_returns_list_of_generated_files(self):
        """generate() should return list of generated file paths."""
        layer = GEOEnrichmentLayer()
        hotel_data = _create_mock_hotel_data()
        geo_assessment = _create_geo_assessment(GEOBand.GOOD)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = layer.generate(hotel_data, geo_assessment, tmpdir)
            
            assert isinstance(result, list)
            assert len(result) > 0
            for filepath in result:
                assert Path(filepath).exists()
