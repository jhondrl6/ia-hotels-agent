"""Tests for ContentScrubber — idempotent fixes for LLM output issues."""
import pytest
from modules.postprocessors.content_scrubber import (
    ContentScrubber,
    ScrubResult,
    PT_TO_ES,
    EN_TO_ES,
)


@pytest.fixture
def scrubber():
    return ContentScrubber()


# ==============================================================================
# FIX 1: Region placeholders ("default" -> real city)
# ==============================================================================
class TestFixRegionPlaceholders:
    def test_replaces_en_default(self, scrubber):
        doc = "Lo que esta pasando en default es preocupante."
        hotel = {"city": "Santa Rosa de Cabal", "state": "Risaralda"}
        result = scrubber.scrub(doc, hotel, "diagnostico")
        assert "in default" not in result.scrubbed.lower()
        assert "en Santa Rosa de Cabal" in result.scrubbed

    def test_replaces_region_de_default(self, scrubber):
        doc = "El mercado region de default muestra caida."
        hotel = {"city": "Medellin", "region": "Eje Cafetero"}
        result = scrubber.scrub(doc, hotel, "diagnostico")
        assert "region del Eje Cafetero" in result.scrubbed or "region de default" not in result.scrubbed.lower()

    def test_skips_without_hotel_data(self, scrubber):
        doc = "Lo que pasa en default es grave."
        result = scrubber.scrub(doc, None, "diagnostico")
        assert "en default" in result.scrubbed.lower()
        assert result.fix_count == 0

    def test_does_not_alter_valor_por_defecto(self, scrubber):
        doc = "El valor por defecto es 100."
        hotel = {"city": "Bogota"}
        result = scrubber.scrub(doc, hotel, "diagnostico")
        assert "valor por defecto" in result.scrubbed
        # "por defecto" is NOT a "en default" pattern so should not be changed

    def test_logs_fix_when_applied(self, scrubber):
        doc = "en default"
        hotel = {"city": "Cali"}
        result = scrubber.scrub(doc, hotel, "diagnostico")
        assert result.fix_count >= 1
        assert any("default" in f.lower() and "cali" in f.lower() for f in result.fixes_applied)


# ==============================================================================
# FIX 2: Duplicate currency ("COP COP" -> "COP")
# ==============================================================================
class TestFixDuplicateCurrency:
    def test_fixes_cop_cop(self, scrubber):
        doc = "Costo: $3.132.000 COP COP por mes."
        result = scrubber.scrub(doc, {}, "diagnostico")
        assert "COP COP" not in result.scrubbed
        assert "COP" in result.scrubbed

    def test_single_cop_unchanged(self, scrubber):
        doc = "Costo: $3.132.000 COP por mes."
        result = scrubber.scrub(doc, {}, "diagnostico")
        assert "COP" in result.scrubbed

    def test_logs_fix(self, scrubber):
        doc = "COP COP"
        result = scrubber.scrub(doc, {}, "diagnostico")
        assert result.fix_count >= 1
        assert any("Moneda" in f or "moneda" in f for f in result.fixes_applied)


# ==============================================================================
# FIX 3: Zero confidence statement
# ==============================================================================
class TestFixConfidenceStatement:
    def test_fixes_zero_confidence_diagnostico(self, scrubber):
        doc = "Con 0% de confianza en el analisis."
        result = scrubber.scrub(doc, {}, "diagnostico")
        assert "0% de confianza" not in result.scrubbed
        assert "disponibles" in result.scrubbed  # part of replacement text

    def test_fixes_zero_confidence_propuesta(self, scrubber):
        doc = "Con 0% confianza."
        result = scrubber.scrub(doc, {}, "propuesta")
        assert "0% confianza" not in result.scrubbed

    def test_does_not_fix_in_asset_doc(self, scrubber):
        doc = "Con 0% de confianza en datos internos."
        result = scrubber.scrub(doc, {}, "asset")
        assert "0% de confianza" in result.scrubbed

    def test_logs_fix(self, scrubber):
        doc = "Con 0% de confianza."
        result = scrubber.scrub(doc, {}, "diagnostico")
        assert any("Confianza" in f or "confianza" in f for f in result.fixes_applied)


# ==============================================================================
# FIX 4: Mixed language (pt->es, en->es)
# ==============================================================================
class TestFixMixedLanguage:
    def test_fixes_passo_to_paso(self, scrubber):
        doc = "El proximo passo es revisar."
        result = scrubber.scrub(doc, {}, "diagnostico")
        assert "passo" not in result.scrubbed.lower()
        assert "paso" in result.scrubbed or "pasO" in result.scrubbed

    def test_fixes_protecao_to_proteccion(self, scrubber):
        doc = "La protecao de datos es clave."
        result = scrubber.scrub(doc, {}, "diagnostico")
        assert "protecao" not in result.scrubbed.lower()

    def test_fixes_guests_to_huespedes(self, scrubber):
        doc = "Los guests son internacionales."
        result = scrubber.scrub(doc, {}, "diagnostico")
        assert "guests" not in result.scrubbed.lower()
        assert "huespedes" in result.scrubbed

    def test_logs_fix_for_language(self, scrubber):
        result = scrubber.scrub("guests", {}, "diagnostico")
        assert any("Idioma" in f or "idioma" in f for f in result.fixes_applied)


# ==============================================================================
# FIX 5: Generic AI phrases
# ==============================================================================
class TestFixGenericAIPhrases:
    def test_softens_generic_phrases(self, scrubber):
        doc = "Hay oportunidades de crecimiento en presencia digital hotelera."
        result = scrubber.scrub(doc, {}, "diagnostico")
        assert "oportunidades de crecimiento en presencia digital hotelera" not in result.scrubbed.lower()


# ==============================================================================
# IDEMPOTENCY
# ==============================================================================
class TestIdempotency:
    def test_double_scrub_same_result(self, scrubber):
        doc = "en default COP COP passo guests"
        hotel = {"city": "Cali", "region": "Valle"}
        first = scrubber.scrub(doc, hotel, "diagnostico")
        second = scrubber.scrub(first.scrubbed, hotel, "diagnostico")
        assert first.scrubbed == second.scrubbed
        # Second run should find nothing to fix
        assert second.fix_count == 0

    def test_triple_scrub_same(self, scrubber):
        doc = "COP COP"
        first = scrubber.scrub(doc, {}, "diagnostico")
        second = scrubber.scrub(first.scrubbed, {}, "diagnostico")
        third = scrubber.scrub(second.scrubbed, {}, "diagnostico")
        assert first.scrubbed == second.scrubbed == third.scrubbed
