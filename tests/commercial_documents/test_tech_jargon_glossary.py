"""FASE-SR-G: Glosario único jerga → lenguaje de negocio (L27) + CG-TECH-JARGON.

Cubre:
- Fuente única: el gate importa TECH_JARGON_TERMS del glosario (identidad).
- apply_glossary traduce los términos detectados en la corrida C
  (H6.4: "Schema, AEO, IAO, Open Graph" + guardia "sin costo (fallback)").
- Patrón de matching compartido (términos con paréntesis detectables).
- Integración: documento de diagnóstico regenerado SIN jerga en vista
  gerencia (el gate CG-TECH-JARGON pasa sobre el texto publicado).
"""

from pathlib import Path
import tempfile

from modules.commercial_documents.tech_jargon_glossary import (
    JARGON_BUSINESS_MAP,
    TECH_JARGON_TERMS,
    apply_glossary,
    jargon_pattern,
)
from modules.quality_gates.commercial_gate import CommercialGateValidator


class TestGlossarySingleSource:
    """FASE-SR-G (L27): una sola fuente consumida por generador y gate."""

    def test_gate_imports_glossary_list(self):
        """commercial_gate.TECH_JARGON_TERMS ES la lista del glosario."""
        import modules.quality_gates.commercial_gate as gate_module

        assert gate_module.TECH_JARGON_TERMS is TECH_JARGON_TERMS

    def test_map_terms_detectable_by_gate_patterns(self):
        """Todo término traducible es DETECTABLE por el gate (L27).

        No se exige identidad de colecciones: la traducción usa compuestos
        ("Schema Hotel", "FAQ Schema") que el gate ya detecta vía el término
        genérico de detección ("Schema" con boundary). La fuente única (L27)
        es el MÓDULO glosario, no la igualdad entre ambas colecciones.
        """
        import re as _re

        undetectable = [
            term
            for term in JARGON_BUSINESS_MAP
            if not any(
                _re.search(jargon_pattern(det), term, _re.IGNORECASE)
                for det in TECH_JARGON_TERMS
            )
        ]
        assert undetectable == []


class TestJargonPattern:
    """FASE-SR-G: semántica de matching compartida gate ↔ glosario."""

    def test_parenthesized_term_matches(self):
        """"sin costo (fallback)" es detectable (\\b final no se ancla tras ')')."""
        text = "Este servicio es sin costo (fallback) del sistema."
        assert jargon_pattern("sin costo (fallback)") in text or (
            __import__("re").search(
                jargon_pattern("sin costo (fallback)"), text
            ) is not None
        )

    def test_word_boundary_still_applies(self):
        """Términos de palabra completa no matchean dentro de otras palabras."""
        import re as _re

        assert _re.search(jargon_pattern("AEO"), "AEOPTIMA") is None
        assert _re.search(jargon_pattern("AEO"), "El AEO mejora") is not None


class TestApplyGlossary:
    """Traducción jerga → lenguaje de negocio (H6.4)."""

    def test_translates_corrida_c_terms(self):
        """Los términos detectados en la corrida C quedan traducidos."""
        text = (
            "| **Schema Hotel** | ✅ |\n"
            "| **Meta Tags Sociales (Open Graph)** | ✅ |\n"
            "| **AEO** (Para que te CITEN) | 34/100 |\n"
            "| **IAO** (Para que te RECOMIENDEN) | 21/100 |\n"
            "El estándar schema.org estructura los datos."
        )
        translated = apply_glossary(text)
        for term in ("Schema", "Open Graph", "AEO", "IAO", "schema.org"):
            assert term not in translated

    def test_compound_replaced_before_bare_term(self):
        """"Schema Hotel" NO colapsa en "Ficha técnica Hotel"."""
        translated = apply_glossary("Servicio: Schema Hotel mejorado.")
        assert "Ficha técnica Hotel" not in translated
        assert "Ficha del Hotel en Google e IA" in translated

    def test_sin_costo_fallback_guard(self):
        """Guardia H6.4: el patrón histórico se traduce a lenguaje de negocio."""
        translated = apply_glossary("Optimización IA — sin costo (fallback).")
        assert "fallback" not in translated
        assert "incluido sin costo adicional" in translated

    def test_idempotent(self):
        """Aplicar el glosario dos veces no cambia el resultado."""
        text = "Curva de Maduración 4 Pilares (GEO → SEO → AEO → IAO)."
        once = apply_glossary(text)
        assert apply_glossary(once) == once

    def test_preserves_tier_legend(self):
        """El glosario NO toca los tokens canónicos de tier (L30, fix T2)."""
        text = "> *Nivel de evidencia: **Tier B** · Precisión: **Tier C***"
        assert apply_glossary(text) == text

    def test_unmapped_detection_terms_left_intact(self):
        """"iahotels.co" (email de contacto) y "UTM" no se traducen."""
        text = "Email: contacto@iahoteles.co — campañas con UTM."
        assert apply_glossary(text) == text


class TestGateAfterGlossary:
    """CG-TECH-JARGON sobre texto traducido: la vista gerencia pasa."""

    def test_translated_management_view_passes_gate(self):
        """Texto con jerga de la corrida C → glosario → gate CG-TECH-JARGON PASS."""
        raw = (
            "# PROPUESTA COMERCIAL\n\n"
            "## 😟 EL PROBLEMA\n\n"
            "| **Schema Hotel** | ⏳ Pendiente |\n"
            "| **AEO** (Para que te CITEN) | 34/100 |\n"
            "| **IAO** (Para que te RECOMIENDEN) | 21/100 |\n"
            "Nota: se construye sobre Schema FAQ + Open Graph.\n"
            "El estándar schema.org estructura los datos.\n"
        )
        validator = CommercialGateValidator()
        result = validator._check_tech_jargon(apply_glossary(raw))
        assert result.passed is True, result.message

    def test_raw_jargon_still_detected_by_gate(self):
        """Test negativo: el gate sigue detectando la jerga SIN traducir."""
        validator = CommercialGateValidator()
        result = validator._check_tech_jargon(
            "| **Schema Hotel** | ⏳ |\nEl estándar schema.org estructura los datos."
        )
        assert result.passed is False
        assert "Schema" in result.message

    def test_sin_costo_fallback_detected_by_gate(self):
        """FASE-SR-G: el patrón histórico es detectable por el gate (guardia)."""
        validator = CommercialGateValidator()
        result = validator._check_tech_jargon(
            "SEO Local — sin costo (fallback) del sistema."
        )
        assert result.passed is False
        assert "sin costo (fallback)" in result.message


class TestDiagnosticGenerateWithoutJargon:
    """Integración: documento regenerado sin jerga en vista gerencia."""

    def test_generated_diagnostic_management_view_passes_jargon_gate(self):
        """generate() aplica el glosario: el texto publicado pasa el gate."""
        from tests.commercial_documents.test_diagnostic_generator import (
            _make_minimal_audit,
            _make_minimal_financial_scenarios,
            _make_minimal_validation_summary,
        )
        from modules.commercial_documents.v4_diagnostic_generator import (
            V4DiagnosticGenerator,
        )

        gen = V4DiagnosticGenerator()
        audit = _make_minimal_audit()
        validation = _make_minimal_validation_summary()
        financial = _make_minimal_financial_scenarios()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = gen.generate(
                audit_result=audit,
                validation_summary=validation,
                financial_scenarios=financial,
                hotel_name="Hotel Test",
                hotel_url="https://example.com",
                output_dir=tmpdir,
                coherence_score=0.85,
                gate_status="PASSED",
            )
            content = Path(path).read_text(encoding="utf-8")

        validator = CommercialGateValidator()
        result = validator._check_tech_jargon(content)
        assert result.passed is True, result.message
