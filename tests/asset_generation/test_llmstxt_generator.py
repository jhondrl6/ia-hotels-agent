"""Tests for LLMSTXTGenerator — FASE-LLMSTXT-FIX fallback behavior."""

import logging
import tempfile
from pathlib import Path

import pytest

from modules.asset_generation.llmstxt_generator import LLMSTXTGenerator


GEO_ENRICHED_LLMS_CONTENT = """\
# Amaziliahotel

**URL:** https://amaziliahotel.com/

## Acerca de
Amaziliahotel es un hotel boutique en Salento, Eje Cafetero, Colombia.
Ofreciendo una experiencia unica para viajeros que buscan comodidad.

**Perfil de Google Business:** https://g.page/amaziliahotel

## Ubicacion
**Sitio web:** https://amaziliahotel.com/

**Pais:** Colombia

## Amenities y Servicios
**Servicios destacados:**

- Hospedaje
- Restaurante
- WiFi
- Recepcion 24 horas

## Contacto
**Sitio web:** https://amaziliahotel.com/

Para reservas directas y consultas especificas,
visite nuestro sitio web o contacte directamente.

## Reserva y Contacto
## Reserva tu experiencia

**Reserva en linea:** Visite nuestro sitio web
**URL:** https://amaziliahotel.com/

Para obtener la mejor tarifa garantizada, reserve directamente
a traves de nuestro sitio web oficial.
"""


class TestGeneratorUsesGeoEnrichedFallback:
    """Test that the generator uses geo_enriched/llms.txt when available."""

    def test_generator_uses_geo_enriched_fallback(self, tmp_path):
        """If geo_enriched_path given with llms.txt, use that content."""
        geo_dir = tmp_path / "geo_enriched"
        geo_dir.mkdir()
        llms_file = geo_dir / "llms.txt"
        llms_file.write_text(GEO_ENRICHED_LLMS_CONTENT, encoding="utf-8")

        generator = LLMSTXTGenerator()
        result = generator.generate(
            {"name": "Hotel", "website": ""},
            geo_enriched_path=geo_dir,
        )

        # Should return the enriched content, not generate placeholders
        assert "# Amaziliahotel" in result
        assert "https://amaziliahotel.com/" in result
        assert "Salento" in result
        # Should NOT contain placeholder values
        assert "# Hotel" not in result or "# Amaziliahotel" in result
        assert "N/A" not in result


class TestGeneratorSkipsGeoEnrichedIfMissing:
    """Test that the generator falls back to normal generation when geo_enriched is absent."""

    def test_generator_skips_geo_enriched_if_file_missing(self, tmp_path):
        """If geo_enriched_path given but llms.txt does not exist, use normal generation."""
        geo_dir = tmp_path / "geo_enriched"
        geo_dir.mkdir()
        # No llms.txt in geo_enriched dir

        generator = LLMSTXTGenerator()
        result = generator.generate(
            {
                "name": "Test Hotel",
                "website": "https://testhotel.com",
                "city": "Bogota",
                "region": "Cundinamarca",
                "phone": "+57 1234567890",
                "email": "info@testhotel.com",
                "address": "Calle 123, Bogota",
            },
            geo_enriched_path=geo_dir,
        )

        # Should generate from hotel_data, not from geo_enriched
        assert "# Test Hotel" in result
        assert "https://testhotel.com" in result
        assert "Bogota" in result

    def test_generator_works_without_geo_enriched_path(self):
        """If no geo_enriched_path given, normal generation works as before."""
        generator = LLMSTXTGenerator()
        result = generator.generate(
            {
                "name": "Sample Hotel",
                "website": "https://sample.com",
                "city": "Medellin",
            }
        )

        assert "# Sample Hotel" in result
        assert "https://sample.com" in result
        assert "Medellin" in result


class TestGeneratorWarnsOnGenericName:
    """Test that the generator emits a warning when the hotel name is generic."""

    def test_generator_warns_on_generic_name(self, caplog):
        """If name='Hotel', should emit a warning log message."""
        generator = LLMSTXTGenerator()

        with caplog.at_level(logging.WARNING):
            result = generator.generate({"name": "Hotel", "website": ""})

        assert any(
            "Hotel name is generic" in msg for msg in caplog.messages
        ), "Expected a warning about generic hotel name"

    def test_generator_warns_on_empty_name(self, caplog):
        """If name is empty string, should emit a warning log message."""
        generator = LLMSTXTGenerator()

        with caplog.at_level(logging.WARNING):
            result = generator.generate({"name": "", "website": ""})

        assert any(
            "generic or missing" in msg for msg in caplog.messages
        ), "Expected a warning about missing hotel name"


class TestGeneratorProducesValidFormat:
    """Test that generated llms.txt follows the llmstxt.org standard."""

    def test_generator_produces_valid_llms_txt_format(self):
        """Output should start with # title and contain ## sections."""
        generator = LLMSTXTGenerator()
        result = generator.generate(
            {
                "name": "Format Test Hotel",
                "website": "https://formattest.com",
                "city": "Cartagena",
                "region": "Caribe",
                "phone": "+57 9876543210",
                "amenities": ["WiFi", "Pool", "Restaurant"],
            }
        )

        # Should start with H1 title
        assert result.strip().startswith("# ")
        # Should contain standard sections
        assert "## Important Pages" in result
        assert "## Services" in result
        assert "## Contact" in result
        # Should contain linked URLs
        assert "- [Homepage](https://formattest.com)" in result
        assert "- [Rooms](" in result
        # Should contain amenities
        assert "- WiFi" in result
        assert "- Pool" in result

    def test_generator_skips_geo_enriched_if_too_short(self, tmp_path):
        """If geo_enriched/llms.txt is too short (< 50 chars), fall back to hotel_data."""
        geo_dir = tmp_path / "geo_enriched"
        geo_dir.mkdir()
        llms_file = geo_dir / "llms.txt"
        llms_file.write_text("# X\n", encoding="utf-8")  # Too short

        generator = LLMSTXTGenerator()
        result = generator.generate(
            {
                "name": "Fallback Hotel",
                "website": "https://fallback.com",
                "city": "Cali",
            },
            geo_enriched_path=geo_dir,
        )

        # Should NOT use the short geo_enriched content
        assert "# Fallback Hotel" in result
        assert "# X" not in result


class TestGenerateFromAssessment:
    """Test generate_from_assessment with geo_enriched fallback."""

    def test_generate_from_assessment_passes_geo_enriched_path(self, tmp_path):
        """generate_from_assessment should forward geo_enriched_path to generate."""
        geo_dir = tmp_path / "geo_enriched"
        geo_dir.mkdir()
        llms_file = geo_dir / "llms.txt"
        llms_file.write_text(GEO_ENRICHED_LLMS_CONTENT, encoding="utf-8")

        generator = LLMSTXTGenerator()
        result = generator.generate_from_assessment(
            {"hotel_name": "Hotel", "url": ""},
            geo_enriched_path=geo_dir,
        )

        # Should use enriched content
        assert "# Amaziliahotel" in result
        assert "Salento" in result
