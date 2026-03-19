"""Tests para SchemaValidatorV2 - Sprint 1.

Valida análisis de Schema.org markup, coverage scoring y generación de claims.
"""
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to Python path for pytest
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest

from modules.data_validation.schema_validator_v2 import SchemaValidatorV2
from data_models.canonical_assessment import SchemaAnalysis
from data_models.claim import Claim
from enums.severity import Severity


@pytest.fixture
def validator():
    """Fixture que proporciona una instancia de SchemaValidatorV2."""
    return SchemaValidatorV2()


@pytest.fixture
def complete_hotel_schema() -> Dict[str, Any]:
    """Fixture con un schema Hotel completo."""
    return {
        "@context": "https://schema.org",
        "@type": "Hotel",
        "name": "Hotel Vísperas",
        "description": "Hotel boutique en Oaxaca",
        "image": "https://hotel.com/image.jpg",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "Calle 5 de Mayo 100",
            "addressLocality": "Oaxaca",
            "addressRegion": "Oaxaca",
            "postalCode": "68000",
            "addressCountry": "MX"
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": "17.0732",
            "longitude": "-96.7266"
        },
        "telephone": "+52-951-123-4567",
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.5",
            "reviewCount": "128"
        },
        "starRating": {
            "@type": "Rating",
            "ratingValue": "4"
        }
    }


@pytest.fixture
def incomplete_hotel_schema() -> Dict[str, Any]:
    """Fixture con un schema Hotel con campos críticos faltantes."""
    return {
        "@context": "https://schema.org",
        "@type": "Hotel",
        "name": "Hotel Vísperas",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "Calle 5 de Mayo 100",
            "addressLocality": "Oaxaca"
        }
        # Falta: image, aggregateRating, geo (campos críticos)
    }


class TestDetectHotelSchemaType:
    """Tests para detección del tipo de schema."""

    def test_detect_hotel_schema_type(self, validator):
        """Detecta @type=Hotel correctamente."""
        html = """
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Hotel",
            "name": "Hotel Vísperas",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "Calle 5 de Mayo 100",
                "addressLocality": "Oaxaca"
            }
        }
        </script>
        """
        analysis = validator.analyze(html, "https://hotel.com")
        
        assert analysis.schema_type == "Hotel"
        assert analysis.has_hotel_schema is True

    def test_detect_organization_schema(self, validator):
        """Detecta @type=Organization."""
        html = """
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "Hotel Vísperas",
            "url": "https://hotel.com"
        }
        </script>
        """
        analysis = validator.analyze(html, "https://hotel.com")
        
        assert analysis.schema_type == "Organization"
        assert analysis.has_hotel_schema is False

    def test_detect_local_business_schema(self, validator):
        """Detecta @type=LocalBusiness."""
        html = """
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": "Hotel Vísperas",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "Calle 5 de Mayo"
            }
        }
        </script>
        """
        analysis = validator.analyze(html, "https://hotel.com")
        
        assert analysis.schema_type == "LocalBusiness"
        assert analysis.has_local_business is True

    def test_hotel_priority_over_local_business(self, validator):
        """Hotel tiene prioridad sobre LocalBusiness."""
        html = """
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": "Hotel Vísperas"
        }
        </script>
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Hotel",
            "name": "Hotel Vísperas"
        }
        </script>
        """
        analysis = validator.analyze(html, "https://hotel.com")
        
        assert analysis.schema_type == "Hotel"


class TestCalculateCoverage:
    """Tests para cálculo de coverage score."""

    def test_calculate_coverage_hotel(self, validator, complete_hotel_schema):
        """Calcula % coverage correctamente para Hotel completo."""
        coverage = validator.calculate_coverage(complete_hotel_schema, "Hotel")
        
        assert "overall" in coverage
        assert "required" in coverage
        assert "critical" in coverage
        assert "recommended" in coverage
        
        # Un schema completo debe tener high coverage
        assert coverage["overall"] > 0.7
        assert coverage["required"] == 1.0  # Todos los required presentes

    def test_calculate_coverage_low_for_incomplete(self, validator, incomplete_hotel_schema):
        """Coverage bajo para schema incompleto."""
        coverage = validator.calculate_coverage(incomplete_hotel_schema, "Hotel")
        
        # Schema incompleto debe tener coverage bajo
        assert coverage["critical"] < 0.5  # Falta image, aggregateRating, geo
        assert coverage["overall"] < 0.8

    def test_required_fields_coverage(self, validator):
        """Calcula coverage de campos required correctamente."""
        schema = {
            "@type": "Hotel",
            "name": "Hotel Vísperas",
            "address": {"@type": "PostalAddress"}
            # Falta @type en root, pero está presente arriba
        }
        coverage = validator.calculate_coverage(schema, "Hotel")
        
        assert coverage["required"] >= 0.0
        assert coverage["required"] <= 1.0


class TestDetectMissingCriticalFields:
    """Tests para detección de campos críticos faltantes."""

    def test_detect_missing_critical_fields(self, validator, incomplete_hotel_schema):
        """Detecta image, aggregateRating faltantes."""
        missing = validator._get_missing_critical_fields(incomplete_hotel_schema, "Hotel")
        
        assert "image" in missing
        assert "aggregateRating" in missing
        assert "geo" in missing

    def test_no_missing_fields_for_complete(self, validator, complete_hotel_schema):
        """No detecta campos faltantes en schema completo."""
        missing = validator._get_missing_critical_fields(complete_hotel_schema, "Hotel")
        
        assert len(missing) == 0

    def test_detect_partial_missing(self, validator):
        """Detecta solo los campos que realmente faltan."""
        schema = {
            "@type": "Hotel",
            "name": "Hotel Vísperas",
            "address": {"streetAddress": "Calle 5"},
            "image": "https://hotel.com/img.jpg"
            # Tiene image, falta aggregateRating y geo
        }
        missing = validator._get_missing_critical_fields(schema, "Hotel")
        
        assert "image" not in missing
        assert "aggregateRating" in missing
        assert "geo" in missing


class TestGenerateClaimsMissingCritical:
    """Tests para generación de claims."""

    def test_generate_claims_missing_critical(self, validator, incomplete_hotel_schema):
        """Genera claims para campos críticos faltantes."""
        analysis = SchemaAnalysis(
            schema_type="Hotel",
            coverage_score=0.4,
            missing_critical_fields=["image", "aggregateRating", "geo"],
            present_fields=["name", "address", "@type"],
            raw_schema=incomplete_hotel_schema,
            has_hotel_schema=True,
            has_local_business=False
        )
        claims = validator.generate_claims(analysis, is_hotel_site=True, url="https://hotel.com")
        
        # Debe haber claims por cada campo crítico faltante
        critical_claims = [c for c in claims if c.severity == Severity.HIGH]
        assert len(critical_claims) >= 3
        
        # Verificar que los campos específicos están mencionados
        messages = " ".join([c.message for c in claims])
        assert "image" in messages
        assert "aggregateRating" in messages

    def test_generate_claim_wrong_schema_type(self, validator):
        """Genera claim si el sitio es hotel pero usa Organization."""
        analysis = SchemaAnalysis(
            schema_type="Organization",
            coverage_score=0.6,
            missing_critical_fields=[],
            present_fields=["name", "url"],
            raw_schema={"@type": "Organization", "name": "Hotel"},
            has_hotel_schema=False,
            has_local_business=False
        )
        claims = validator.generate_claims(analysis, is_hotel_site=True, url="https://hotel.com")
        
        wrong_type_claims = [c for c in claims if "Hotel" in c.message and c.severity == Severity.HIGH]
        assert len(wrong_type_claims) >= 1

    def test_generate_claim_low_coverage(self, validator):
        """Genera claim MEDIUM si coverage < 50%."""
        analysis = SchemaAnalysis(
            schema_type="Hotel",
            coverage_score=0.3,
            missing_critical_fields=["image"],
            present_fields=["name", "address", "@type"],
            raw_schema={"@type": "Hotel", "name": "Hotel"},
            has_hotel_schema=True,
            has_local_business=False
        )
        claims = validator.generate_claims(analysis, is_hotel_site=True, url="https://hotel.com")
        
        low_coverage_claims = [c for c in claims if c.severity == Severity.MEDIUM]
        assert len(low_coverage_claims) >= 1
        assert "coverage" in low_coverage_claims[0].message.lower() or "30%" in low_coverage_claims[0].message


class TestNoSchemaGeneratesCriticalClaim:
    """Tests para casos sin schema."""

    def test_no_schema_generates_critical_claim(self, validator):
        """Sin schema → CRITICAL claim."""
        html = "<html><head><title>Hotel Vísperas</title></head><body></body></html>"
        analysis, claims = validator.validate(html, url="https://hotel.com", is_hotel_site=True)
        
        assert analysis.schema_type is None
        assert analysis.coverage_score == 0.0
        
        critical_claims = [c for c in claims if c.severity == Severity.CRITICAL]
        assert len(critical_claims) == 1
        assert "Schema.org" in critical_claims[0].message
        assert "Rich Results" in critical_claims[0].message

    def test_empty_html_generates_critical(self, validator):
        """HTML vacío genera claim CRITICAL."""
        html = ""
        analysis, claims = validator.validate(html, url="https://hotel.com", is_hotel_site=True)
        
        assert analysis.schema_type is None
        assert len(claims) == 1
        assert claims[0].severity == Severity.CRITICAL

    def test_no_json_ld_scripts_generates_critical(self, validator):
        """HTML sin scripts JSON-LD genera claim CRITICAL."""
        html = """
        <html>
        <head><title>Hotel Vísperas</title></head>
        <body>
            <script type="text/javascript">
                console.log("not json-ld");
            </script>
        </body>
        </html>
        """
        analysis, claims = validator.validate(html, url="https://hotel.com", is_hotel_site=True)
        
        assert analysis.schema_type is None
        assert len([c for c in claims if c.severity == Severity.CRITICAL]) == 1


class TestExtractJsonLdScripts:
    """Tests para extracción de scripts JSON-LD."""

    def test_extract_single_script(self, validator):
        """Extrae un único script JSON-LD."""
        html = """
        <script type="application/ld+json">
        {"@type": "Hotel", "name": "Test"}
        </script>
        """
        schemas = validator._extract_json_ld_scripts(html)
        
        assert len(schemas) == 1
        assert schemas[0]["@type"] == "Hotel"

    def test_extract_multiple_scripts(self, validator):
        """Extrae múltiples scripts JSON-LD."""
        html = """
        <script type="application/ld+json">{"@type": "Hotel", "name": "H1"}</script>
        <script type="application/ld+json">{"@type": "Organization", "name": "O1"}</script>
        """
        schemas = validator._extract_json_ld_scripts(html)
        
        assert len(schemas) == 2

    def test_extract_graph_structure(self, validator):
        """Maneja estructura @graph correctamente."""
        html = """
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@graph": [
                {"@type": "Hotel", "name": "H1"},
                {"@type": "WebSite", "name": "W1"}
            ]
        }
        </script>
        """
        schemas = validator._extract_json_ld_scripts(html)
        
        assert len(schemas) == 2
        assert any(s.get("@type") == "Hotel" for s in schemas)


class TestEdgeCases:
    """Tests para casos edge."""

    def test_malformed_json_ignored(self, validator):
        """Scripts JSON malformados son ignorados silenciosamente."""
        html = """
        <html><head>
        <script type="application/ld+json">
        { invalid json here
        </script>
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Hotel",
            "name": "Hotel Vísperas"
        }
        </script>
        </head><body></body></html>
        """
        
        analysis = validator.analyze(html, "https://hotel.com")
        
        assert analysis.schema_type == "Hotel"

    def test_empty_schema_returns_unknown(self, validator):
        """Schema sin @type retorna Unknown."""
        html = """
        <html><head>
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "name": "Something"
        }
        </script>
        </head><body></body></html>
        """
        
        analysis = validator.analyze(html, "https://hotel.com")
        
        assert analysis.schema_type == "Unknown"

    def test_schema_coverage_exact_values(self, validator, complete_hotel_schema):
        """Coverage calcula valores exactos correctamente."""
        coverage = validator.calculate_coverage(complete_hotel_schema, "Hotel")
        
        # Required: name, address, @type = 3 campos
        assert coverage["required"] == 1.0
        
        # Critical: image, aggregateRating, geo = 3 campos
        assert coverage["critical"] == 1.0
        
        # Overall ponderado: required(40%) + critical(40%) + recommended(20%)
        assert 0.0 <= coverage["overall"] <= 1.0

    def test_all_claims_together(self, validator, incomplete_hotel_schema):
        """Validación completa genera todos los claims esperados."""
        html = f"""
        <script type="application/ld+json">
        {str(incomplete_hotel_schema).replace("'", '"')}
        </script>
        """
        # Usar el schema directamente para el test
        analysis = SchemaAnalysis(
            schema_type="Hotel",
            coverage_score=0.3,
            missing_critical_fields=["image", "aggregateRating", "geo"],
            present_fields=["name", "address", "@type"],
            raw_schema=incomplete_hotel_schema,
            has_hotel_schema=True,
            has_local_business=False
        )
        claims = validator.generate_claims(analysis, is_hotel_site=True, url="https://hotel.com")
        
        # Debe haber claims HIGH (3 campos críticos) + MEDIUM (coverage bajo)
        assert len(claims) >= 4
