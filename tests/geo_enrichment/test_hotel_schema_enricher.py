"""Tests for Hotel Schema Enricher - FASE-3 validation."""

import pytest
import json

from data_models.canonical_assessment import (
    CanonicalAssessment, SiteMetadata, GBPAnalysis,
    SchemaAnalysis, PerformanceAnalysis, PerformanceMetrics
)
from modules.geo_enrichment.hotel_schema_enricher import HotelSchemaEnricher


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
            categories=["Hotel", "Boutique Hotel", "Alojamiento", "WiFi"],
            lat=4.8133,
            lng=-75.6916,
        ),
    )


class TestHotelSchemaEnricher:
    """Test Hotel schema enrichment."""

    def test_generates_valid_json(self):
        """Output should be valid JSON."""
        enricher = HotelSchemaEnricher()
        hotel_data = _create_mock_hotel_data()
        
        output = enricher.enrich(hotel_data)
        
        # Should not raise
        parsed = json.loads(output)
        assert parsed is not None

    def test_generates_json_ld_format(self):
        """Output should be JSON-LD format with @context."""
        enricher = HotelSchemaEnricher()
        hotel_data = _create_mock_hotel_data()
        
        output = enricher.enrich(hotel_data)
        parsed = json.loads(output)
        
        assert "@context" in parsed
        assert parsed["@context"] == "https://schema.org"

    def test_schema_has_hotel_type(self):
        """Schema should have @type Hotel."""
        enricher = HotelSchemaEnricher()
        hotel_data = _create_mock_hotel_data()
        
        output = enricher.enrich(hotel_data)
        parsed = json.loads(output)
        
        assert "@graph" in parsed
        hotel_schema = parsed["@graph"][0]
        assert hotel_schema["@type"] == "Hotel"

    def test_schema_has_name(self):
        """Schema should include hotel name."""
        enricher = HotelSchemaEnricher()
        hotel_data = _create_mock_hotel_data()
        
        output = enricher.enrich(hotel_data)
        parsed = json.loads(output)
        
        hotel_schema = parsed["@graph"][0]
        assert "Hotel Visperas" in hotel_schema["name"]

    def test_schema_has_url(self):
        """Schema should include URL."""
        enricher = HotelSchemaEnricher()
        hotel_data = _create_mock_hotel_data()
        
        output = enricher.enrich(hotel_data)
        parsed = json.loads(output)
        
        hotel_schema = parsed["@graph"][0]
        assert hotel_schema["url"] == "https://hotelvisperas.com"

    def test_schema_has_16_plus_fields(self):
        """Schema should have 16+ fields for rich schema."""
        enricher = HotelSchemaEnricher()
        hotel_data = _create_mock_hotel_data()
        
        output = enricher.enrich(hotel_data)
        parsed = json.loads(output)
        
        hotel_schema = parsed["@graph"][0]
        
        # Count non-meta fields
        field_count = len([k for k in hotel_schema.keys() if not k.startswith("@")])
        
        assert field_count >= 16, f"Expected 16+ fields, got {field_count}: {list(hotel_schema.keys())}"

    def test_schema_has_description(self):
        """Schema should include description field."""
        enricher = HotelSchemaEnricher()
        hotel_data = _create_mock_hotel_data()
        
        output = enricher.enrich(hotel_data)
        parsed = json.loads(output)
        
        hotel_schema = parsed["@graph"][0]
        assert "description" in hotel_schema

    def test_schema_has_geo(self):
        """Schema should include geo coordinates."""
        enricher = HotelSchemaEnricher()
        hotel_data = _create_mock_hotel_data()
        
        output = enricher.enrich(hotel_data)
        parsed = json.loads(output)
        
        hotel_schema = parsed["@graph"][0]
        assert "geo" in hotel_schema
        assert hotel_schema["geo"]["@type"] == "GeoCoordinates"

    def test_schema_has_amenity_features(self):
        """Schema should include amenityFeature array."""
        enricher = HotelSchemaEnricher()
        hotel_data = _create_mock_hotel_data()
        
        output = enricher.enrich(hotel_data)
        parsed = json.loads(output)
        
        hotel_schema = parsed["@graph"][0]
        assert "amenityFeature" in hotel_schema
        assert isinstance(hotel_schema["amenityFeature"], list)
        assert len(hotel_schema["amenityFeature"]) > 0

    def test_amenity_features_have_correct_structure(self):
        """Amenity features should have correct @type."""
        enricher = HotelSchemaEnricher()
        hotel_data = _create_mock_hotel_data()
        
        output = enricher.enrich(hotel_data)
        parsed = json.loads(output)
        
        hotel_schema = parsed["@graph"][0]
        amenity = hotel_schema["amenityFeature"][0]
        
        assert amenity["@type"] == "LocationFeatureSpecification"
        assert "name" in amenity
        assert "value" in amenity


class TestFAQSchemaGeneration:
    """Test FAQ Schema generation."""

    def test_generates_faq_schema(self):
        """Should generate valid FAQ schema."""
        enricher = HotelSchemaEnricher()
        hotel_data = _create_mock_hotel_data()
        
        output = enricher.generate_faq_schema(hotel_data)
        parsed = json.loads(output)
        
        assert parsed["@type"] == "FAQPage"
        assert "mainEntity" in parsed
        assert isinstance(parsed["mainEntity"], list)

    def test_faq_has_questions(self):
        """FAQ should have at least one question."""
        enricher = HotelSchemaEnricher()
        hotel_data = _create_mock_hotel_data()
        
        output = enricher.generate_faq_schema(hotel_data)
        parsed = json.loads(output)
        
        assert len(parsed["mainEntity"]) >= 1

    def test_faq_questions_have_name_and_answer(self):
        """Each FAQ question should have name and acceptedAnswer."""
        enricher = HotelSchemaEnricher()
        hotel_data = _create_mock_hotel_data()
        
        output = enricher.generate_faq_schema(hotel_data)
        parsed = json.loads(output)
        
        for question in parsed["mainEntity"]:
            assert "name" in question
            assert "acceptedAnswer" in question
            assert question["acceptedAnswer"]["@type"] == "Answer"
            assert "text" in question["acceptedAnswer"]


class TestSchemaValidation:
    """Test schema validation."""

    def test_validate_accepts_valid_schema(self):
        """validate_schema should accept valid schema."""
        enricher = HotelSchemaEnricher()
        hotel_data = _create_mock_hotel_data()
        
        output = enricher.enrich(hotel_data)
        is_valid, errors = enricher.validate_schema(output)
        
        assert is_valid, f"Schema should be valid but got errors: {errors}"

    def test_validate_rejects_invalid_json(self):
        """validate_schema should reject invalid JSON."""
        enricher = HotelSchemaEnricher()
        
        is_valid, errors = enricher.validate_schema("not valid json")
        
        assert not is_valid
        assert len(errors) > 0
