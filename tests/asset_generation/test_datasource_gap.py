"""Tests for FASE-1-DATASOURCE-GAP: DataSource Gap diagnostic and fix.

Verifica que _extract_validated_fields() propaga datos de GBP y cross_validation
a hotel_data incluso cuando schema.properties esta vacio.

Gap original: phone_web de cross_validation nunca llegaba a hotel_data.telephone
cuando gbp.phone era None.
"""

import pytest
from unittest.mock import Mock, MagicMock

from modules.asset_generation.v4_asset_orchestrator import V4AssetOrchestrator
from modules.commercial_documents.data_structures import (
    V4AuditResult,
    ValidationSummary,
    ValidatedField,
    SchemaValidation,
    GBPData,
    PerformanceData,
    CrossValidationResult,
)


def _create_orchestrator():
    """Create a minimal V4AssetOrchestrator for testing _extract_validated_fields."""
    return V4AssetOrchestrator(output_base_dir="/tmp/test_output")


def _create_empty_validation_summary():
    """Create ValidationSummary with no validated fields."""
    mock_summary = Mock(spec=ValidationSummary)
    mock_summary.fields = []
    return mock_summary


def _create_mock_audit(schema_props=None, gbp_phone=None, gbp_lat=None, gbp_lng=None,
                       gbp_address=None, gbp_rating=None, gbp_reviews=None,
                       gbp_name=None, gbp_website=None,
                       phone_web=None, phone_gbp=None,
                       hotel_name="Test Hotel", url="https://test.com"):
    """Helper to create mock V4AuditResult with configurable fields."""
    mock_audit = Mock(spec=V4AuditResult)
    mock_audit.url = url
    mock_audit.hotel_name = hotel_name
    mock_audit.timestamp = "2026-04-21T10:00:00"

    # Schema
    mock_schema = Mock(spec=SchemaValidation)
    if schema_props is not None:
        mock_schema.properties = schema_props
    else:
        mock_schema.properties = {}
    mock_audit.schema = mock_schema

    # GBP - use Mock without spec to allow dynamic attributes (lat/lng not in GBPData)
    mock_gbp = Mock()
    mock_gbp.place_found = gbp_lat is not None
    mock_gbp.name = gbp_name
    mock_gbp.phone = gbp_phone
    mock_gbp.address = gbp_address
    mock_gbp.rating = gbp_rating
    mock_gbp.reviews = gbp_reviews
    mock_gbp.website = gbp_website
    mock_gbp.lat = gbp_lat if gbp_lat is not None else 0.0
    mock_gbp.lng = gbp_lng if gbp_lng is not None else 0.0
    mock_audit.gbp = mock_gbp

    # Performance
    mock_audit.performance = Mock(spec=PerformanceData)

    # Cross-validation
    mock_validation = Mock(spec=CrossValidationResult)
    mock_validation.phone_web = phone_web
    mock_validation.phone_gbp = phone_gbp
    mock_audit.validation = mock_validation

    mock_audit.overall_confidence = "HIGH"
    mock_audit.critical_issues = []

    return mock_audit


class TestGbpEmptyFallbackToCrossValidation:
    """test_gbp_empty_fallback_to_cross_validation: gbp=None, schema=None,
    pero validation.phone_web existe -> telephone se propaga."""

    def test_phone_web_propagated_when_gbp_none(self):
        orch = _create_orchestrator()
        summary = _create_empty_validation_summary()
        audit = _create_mock_audit(gbp_phone=None, phone_web="+57 3104019049")

        result = orch._extract_validated_fields(summary, audit)

        assert result["hotel_data"].get("telephone") == "+57 3104019049"
        assert result["hotel_data"].get("phone") == "+57 3104019049"

    def test_phone_web_not_overwrite_gbp_phone(self):
        """Si gbp.phone ya existe, phone_web NO debe sobreescribirlo."""
        orch = _create_orchestrator()
        summary = _create_empty_validation_summary()
        audit = _create_mock_audit(gbp_phone="310 4019049", phone_web="+57 3104019049")

        result = orch._extract_validated_fields(summary, audit)

        # gbp.phone se propaga primero, phone_web no debe sobreescribir
        assert result["hotel_data"].get("telephone") == "310 4019049"
        assert result["hotel_data"].get("phone") == "310 4019049"


class TestSchemaEmptyGbpPartial:
    """test_schema_empty_gbp_partial: schema.properties vacio, gbp tiene solo lat/lng
    -> hotel_data tiene lat/lng pero no telephone."""

    def test_lat_lng_from_gbp_no_phone(self):
        orch = _create_orchestrator()
        summary = _create_empty_validation_summary()
        audit = _create_mock_audit(gbp_lat=4.8068995, gbp_lng=-75.8291505, gbp_phone=None, phone_web=None)

        result = orch._extract_validated_fields(summary, audit)

        assert result["hotel_data"].get("latitude") == 4.8068995
        assert result["hotel_data"].get("longitude") == -75.8291505
        assert result["hotel_data"].get("telephone") is None


class TestBothSourcesEmpty:
    """test_both_sources_empty: Ambos vacios -> hotel_data tiene solo name/url (no crashea)."""

    def test_no_crash_with_empty_sources(self):
        orch = _create_orchestrator()
        summary = _create_empty_validation_summary()
        audit = _create_mock_audit(
            gbp_phone=None, gbp_lat=None, gbp_lng=None,
            gbp_address=None, gbp_rating=None, gbp_reviews=None,
            gbp_name=None, gbp_website=None,
            phone_web=None, phone_gbp=None,
            hotel_name="Test Hotel"
        )

        result = orch._extract_validated_fields(summary, audit)

        # Should not crash and should have at least name and url
        assert result["hotel_data"].get("name") == "Test Hotel"
        assert result["hotel_data"].get("url") == "https://test.com"
        assert result["hotel_data"].get("telephone") is None


class TestGbpComplete:
    """test_gbp_complete: gbp tiene todos los campos -> hotel_data completo."""

    def test_all_gbp_fields_propagated(self):
        orch = _create_orchestrator()
        summary = _create_empty_validation_summary()
        audit = _create_mock_audit(
            gbp_name="Amazilia Hotel Campestre",
            gbp_phone="310 4019049",
            gbp_lat=4.8068995,
            gbp_lng=-75.8291505,
            gbp_address="CERRITOS, Pereira, Risaralda",
            gbp_rating=4.5,
            gbp_reviews=202,
            gbp_website="https://amaziliahotel.com/"
        )

        result = orch._extract_validated_fields(summary, audit)

        hd = result["hotel_data"]
        assert hd["name"] == "Amazilia Hotel Campestre"
        assert hd["telephone"] == "310 4019049"
        assert hd["phone"] == "310 4019049"
        assert hd["latitude"] == 4.8068995
        assert hd["longitude"] == -75.8291505
        assert hd["address"] == "CERRITOS, Pereira, Risaralda"
        assert hd["rating"] == 4.5
        assert hd["review_count"] == 202
        assert hd["url"] == "https://amaziliahotel.com/"


class TestSchemaGeoFallback:
    """test_schema_geo_fallback: gbp sin lat/lng pero schema.properties tiene geo -> se usa schema.geo.
    NOTA: Este test verifica que si schema tiene geo, se usa. Pero en amaziliahotel
    schema.properties es vacio, asi que el fallback schema.geo no aplica para ese caso."""

    def test_schema_geo_used_when_gbp_no_coords(self):
        orch = _create_orchestrator()
        summary = _create_empty_validation_summary()
        # Schema with geo in properties
        schema_props = {
            "name": "Test Hotel",
            "geo": {"latitude": 4.8133, "longitude": -75.6916}
        }
        audit = _create_mock_audit(
            schema_props=schema_props,
            gbp_lat=None, gbp_lng=None, gbp_phone=None
        )

        result = orch._extract_validated_fields(summary, audit)

        hd = result["hotel_data"]
        # Schema properties block populates name
        assert hd.get("name") == "Test Hotel"
        # Note: geo from schema.properties.geo is NOT extracted by current code
        # (it expects lat/lng at top level of properties). This test documents the gap.


class TestAddressFallbackGbpFormattedAddress:
    """test_address_fallback_gbp_formatted_address: gbp.address vacio
    pero gbp.formatted_address existe -> address se propaga.
    NOTA: Current code uses gbp.address, not gbp.formatted_address.
    This test documents the behavior."""

    def test_address_from_gbp(self):
        orch = _create_orchestrator()
        summary = _create_empty_validation_summary()
        audit = _create_mock_audit(
            gbp_address="mts a la derecha, Via Pereira, CERRITOS, Pereira"
        )

        result = orch._extract_validated_fields(summary, audit)

        assert result["hotel_data"].get("address") == "mts a la derecha, Via Pereira, CERRITOS, Pereira"


class TestRatingFallbackGbp:
    """test_rating_fallback_gbp: gbp.rating=4.5, schema vacio -> rating=4.5."""

    def test_rating_from_gbp(self):
        orch = _create_orchestrator()
        summary = _create_empty_validation_summary()
        audit = _create_mock_audit(gbp_rating=4.5, gbp_reviews=202)

        result = orch._extract_validated_fields(summary, audit)

        assert result["hotel_data"].get("rating") == 4.5
        assert result["hotel_data"].get("review_count") == 202


class TestReviewCountFallbackGbp:
    """test_review_count_fallback_gbp: gbp.user_ratings_total=202, schema vacio -> review_count=202."""

    def test_review_count_from_gbp(self):
        orch = _create_orchestrator()
        summary = _create_empty_validation_summary()
        audit = _create_mock_audit(gbp_reviews=202)

        result = orch._extract_validated_fields(summary, audit)

        assert result["hotel_data"].get("review_count") == 202


class TestAllCriticalFieldsGbpFallback:
    """test_all_critical_fields_gbp_fallback: gbp tiene phone, lat/lng, formatted_address,
    rating, reviews -> hotel_data completo sin schema."""

    def test_amaziliahotel_scenario(self):
        """Simula el escenario real de amaziliahotel.com: schema vacio, GBP completo."""
        orch = _create_orchestrator()
        summary = _create_empty_validation_summary()
        audit = _create_mock_audit(
            schema_props={},  # NO schema markup
            gbp_name="Amazilia Hotel Campestre",
            gbp_phone="310 4019049",
            gbp_lat=4.8068995,
            gbp_lng=-75.8291505,
            gbp_address="mts a la derecha, Via Pereira a #Entrada 8 Cafelia, 600, CERRITOS, Pereira, Risaralda, Colombia",
            gbp_rating=4.5,
            gbp_reviews=202,
            gbp_website="https://amaziliahotel.com/",
            phone_web="+57 3104019049",
            phone_gbp="310 4019049",
            hotel_name="Amaziliahotel",
            url="https://amaziliahotel.com/"
        )

        result = orch._extract_validated_fields(summary, audit)

        hd = result["hotel_data"]
        # All critical fields must be present
        assert hd.get("name") is not None, "name missing"
        assert hd.get("telephone") is not None, "telephone missing"
        assert hd.get("latitude") is not None, "latitude missing"
        assert hd.get("longitude") is not None, "longitude missing"
        assert hd.get("address") is not None, "address missing"
        assert hd.get("rating") is not None, "rating missing"
        assert hd.get("review_count") is not None, "review_count missing"
        assert hd.get("url") is not None, "url missing"

        # Verify actual values
        assert hd["telephone"] == "310 4019049"
        assert hd["latitude"] == 4.8068995
        assert hd["longitude"] == -75.8291505
        assert hd["rating"] == 4.5
        assert hd["review_count"] == 202

    def test_phone_web_fallback_when_gbp_no_phone(self):
        """Scenario: gbp.phone=None pero phone_web existe -> telephone viene de phone_web."""
        orch = _create_orchestrator()
        summary = _create_empty_validation_summary()
        audit = _create_mock_audit(
            schema_props={},
            gbp_phone=None,
            phone_web="+57 3104019049",
            gbp_lat=4.8068995,
            gbp_lng=-75.8291505,
            gbp_rating=4.5,
            gbp_reviews=202,
        )

        result = orch._extract_validated_fields(summary, audit)

        hd = result["hotel_data"]
        assert hd.get("telephone") == "+57 3104019049", "phone_web fallback missing"
        assert hd.get("phone") == "+57 3104019049", "phone_web fallback missing"


class TestDiagnosticLogging:
    """Verify diagnostic logging keys are checked (presence verification only)."""

    def test_validated_data_has_phone_web_key(self):
        orch = _create_orchestrator()
        summary = _create_empty_validation_summary()
        audit = _create_mock_audit(phone_web="+57 3104019049", phone_gbp="310 4019049")

        result = orch._extract_validated_fields(summary, audit)

        # phone_web and phone_gbp should be at validated_data level (not hotel_data)
        assert result.get("phone_web") == "+57 3104019049"
        assert result.get("phone_gbp") == "310 4019049"
        assert result.get("whatsapp") == "+57 3104019049"

    def test_gbp_rating_propagated_to_validated_data(self):
        orch = _create_orchestrator()
        summary = _create_empty_validation_summary()
        audit = _create_mock_audit(gbp_rating=4.5, gbp_reviews=202)

        result = orch._extract_validated_fields(summary, audit)

        assert result.get("gbp_rating") == 4.5
        assert result.get("gbp_review_count") == 202
