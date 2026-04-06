"""Tests for LLMs.txt Generator - FASE-3 validation."""

import pytest
import tempfile
from pathlib import Path

from data_models.canonical_assessment import (
    CanonicalAssessment, SiteMetadata, GBPAnalysis,
    SchemaAnalysis, PerformanceAnalysis, PerformanceMetrics
)
from modules.geo_enrichment.llms_txt_generator import LLMsTxtGenerator


def _create_mock_hotel_data() -> CanonicalAssessment:
    """Create mock CanonicalAssessment for testing."""
    return CanonicalAssessment(
        url="https://hotelvisperas.com",
        name="Hotel Visperas",
        site_metadata=SiteMetadata(
            title="Hotel Visperas - Boutique",
            description="Hotel boutique con encanto colonial en el centro histórico de Cartagena",
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
            categories=["Hotel", "Boutique Hotel", "Alojamiento", "WiFi", "Piscina"],
        ),
    )


class TestLLMsTxtGenerator:
    """Test LLMs.txt generation."""

    def test_generates_h1_with_hotel_name(self):
        """Generated content should have H1 with hotel name."""
        generator = LLMsTxtGenerator()
        hotel_data = _create_mock_hotel_data()
        
        content = generator.generate(hotel_data)
        
        assert "# Hotel Visperas" in content

    def test_generates_url(self):
        """Generated content should include URL."""
        generator = LLMsTxtGenerator()
        hotel_data = _create_mock_hotel_data()
        
        content = generator.generate(hotel_data)
        
        assert "https://hotelvisperas.com" in content

    def test_generates_about_section(self):
        """Generated content should have About section."""
        generator = LLMsTxtGenerator()
        hotel_data = _create_mock_hotel_data()
        
        content = generator.generate(hotel_data)
        
        assert "## Acerca de" in content
        assert "Cartagena" in content  # From description

    def test_generates_location_section(self):
        """Generated content should have Location section."""
        generator = LLMsTxtGenerator()
        hotel_data = _create_mock_hotel_data()
        
        content = generator.generate(hotel_data)
        
        assert "## Ubicacion" in content

    def test_generates_amenities_section(self):
        """Generated content should have Amenities section."""
        generator = LLMsTxtGenerator()
        hotel_data = _create_mock_hotel_data()
        
        content = generator.generate(hotel_data)
        
        assert "## Amenities y Servicios" in content
        # Should list categories
        assert "Hotel" in content or "Boutique" in content

    def test_generates_contact_section(self):
        """Generated content should have Contact section."""
        generator = LLMsTxtGenerator()
        hotel_data = _create_mock_hotel_data()
        
        content = generator.generate(hotel_data)
        
        assert "## Contacto" in content

    def test_generates_cta_section(self):
        """Generated content should have CTA section."""
        generator = LLMsTxtGenerator()
        hotel_data = _create_mock_hotel_data()
        
        content = generator.generate(hotel_data)
        
        assert "## Reserva" in content

    def test_output_is_valid_utf8(self):
        """Output should be valid UTF-8."""
        generator = LLMsTxtGenerator()
        hotel_data = _create_mock_hotel_data()
        
        content = generator.generate(hotel_data)
        
        # Should not raise
        content.encode("utf-8")

    def test_content_is_markdown_formatted(self):
        """Output should be markdown formatted with headers."""
        generator = LLMsTxtGenerator()
        hotel_data = _create_mock_hotel_data()
        
        content = generator.generate(hotel_data)
        
        # Check markdown elements
        assert content.startswith("#")  # H1
        assert "##" in content  # H2 sections
