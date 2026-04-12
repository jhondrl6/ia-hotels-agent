"""
Tests para _calculate_aeo_score() — FASE-B: AEO Scoring Rewrite.

NUEVA LOGICA (basada en CHECKLIST_AEO de FASE-A):
  - schema_faq (25pts): FAQ Schema válido
  - open_graph (15pts): OG tags presentes
  - schema_hotel_aeo (15pts): Schema Hotel detallado
  - contenido_factual (20pts): Horarios/precios/servicios accesibles
  - speakable_schema (10pts): Markup específico para voz
  - imagenes_alt_aeo (15pts): Alt text como fuente para image snippets

  NOTA: Citabilidad fue MOVIDA a IAO (FASE-A). AEO NO incluye citability.
  Si hay datos SerpAPI: ponderación 60% checklist + 40% resultado real.
"""

import types
import pytest

from modules.commercial_documents.v4_diagnostic_generator import (
    V4DiagnosticGenerator,
    CHECKLIST_AEO,
    calcular_score_aeo,
)
from modules.commercial_documents.data_structures import (
    V4AuditResult,
    SchemaValidation,
    PerformanceData,
    GBPData,
    CrossValidationResult,
)


# ---------------------------------------------------------------------------
# Helpers para construir audit_result mock con campos opcionales
# ---------------------------------------------------------------------------

def _make_audit_result(
    hotel_schema_detected=False,
    hotel_schema_valid=False,
    faq_schema_detected=False,
    faq_schema_valid=False,
    open_graph=False,
    imagenes_alt=False,
    contenido_factual=False,
    speakable_schema=False,
    aeo_snippets_source=None,  # "serpapi" | "stub" | None (no attribute)
    snippet_score=0,
    citability_score=None,  # Ya no afecta AEO, pero existe para IAO
):
    """Crea un V4AuditResult + inyecta seo_elements y aeo_snippets."""
    schema = SchemaValidation(
        hotel_schema_detected=hotel_schema_detected,
        hotel_schema_valid=hotel_schema_valid,  # USA el parametro real
        hotel_confidence="valid" if hotel_schema_valid else ("detected" if hotel_schema_detected else "none"),
        faq_schema_detected=faq_schema_detected,
        faq_schema_valid=faq_schema_valid,  # USA el parametro real
        faq_confidence="valid" if faq_schema_valid else ("detected" if faq_schema_detected else "none"),
        org_schema_detected=False,
        total_schemas=0,
    )
    performance = PerformanceData(
        has_field_data=True,
        mobile_score=80,
        desktop_score=None,
        lcp=None,
        fid=None,
        cls=None,
        status="ok",
        message="",
    )
    gbp = GBPData(
        place_found=False,
        place_id=None,
        name="Test Hotel",
        rating=0.0,
        reviews=0,
        photos=0,
        phone=None,
        website=None,
        address="",
        geo_score=0,
        geo_score_breakdown={},
        confidence="unknown",
    )
    validation = CrossValidationResult(
        whatsapp_status="unknown",
        phone_web=None,
        phone_gbp=None,
        adr_status="unknown",
        adr_web=None,
        adr_benchmark=None,
    )

    audit = V4AuditResult(
        url="https://test-hotel.com",
        hotel_name="Test Hotel",
        timestamp="2026-04-08T00:00:00",
        schema=schema,
        gbp=gbp,
        performance=performance,
        validation=validation,
        overall_confidence="unknown",
    )

    # SEO elements (open_graph e imagenes_alt)
    seo_mock = types.SimpleNamespace(
        open_graph=open_graph,
        imagenes_alt=imagenes_alt,
        redes_activas=False,
    )
    audit.seo_elements = seo_mock

    # GBP hours para contenido_factual
    if contenido_factual:
        audit.gbp.hours = "9am-6pm"
    else:
        audit.gbp.hours = None

    # Speakable schema (nuevo, default False)
    # Se injecta via atributo opcional en el dataclass

    # Citability (ADVISORY, pero YA NO afecta AEO)
    if citability_score is not None:
        cit_mock = types.SimpleNamespace(
            overall_score=citability_score,
            blocks_analyzed=0,
            high_citability_blocks=0,
            block_scores=[],
        )
    else:
        cit_mock = None
    audit.citability = cit_mock

    # AEO Snippet Tracker (FASE-B)
    if aeo_snippets_source is not None:
        snippet_mock = types.SimpleNamespace(
            source=aeo_snippets_source,
            snippet_score=snippet_score,
            queries_tested=5,
            snippets_captured=0,
            snippets_competitor=0,
            paa_presence=0,
            hotel_url="https://test-hotel.com",
            queries=[],
            timestamp="2026-04-08T00:00:00",
        )
        audit.aeo_snippets = snippet_mock

    return audit


# ---------------------------------------------------------------------------
# Tests: _calculate_aeo_score usa CHECKLIST_AEO (NO citabilidad)
# ---------------------------------------------------------------------------

class TestAEOScoreChecklistAEO:
    """AEO score basado en CHECKLIST_AEO (6 elementos, 100pts total)."""

    def test_aeo_all_true(self):
        """Todos los elementos del checklist AEO presentes → 100.

        NOTA: speakable_schema siempre es False en _extraer_elementos_aeo
        (sin detector implementado). El maximo real es 90.
        """
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result(
            hotel_schema_detected=True, hotel_schema_valid=True,
            faq_schema_detected=True, faq_schema_valid=True,
            open_graph=True,
            imagenes_alt=True,
            contenido_factual=True,
            # speakable_schema: siempre False en extractor actual
        )
        result = gen._calculate_aeo_score(audit)
        # speakable_schema no se puede activar (sin detector), maximo 90
        assert result == "90", f"Esperaba '90', obtuve '{result}'"

    def test_aeo_no_citability(self):
        """Citabilidad NO debe afectar AEO score (movida a IAO en FASE-A)."""
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        # Solo citability presente, nada del checklist AEO
        audit = _make_audit_result(citability_score=100)
        result = gen._calculate_aeo_score(audit)
        # Sin elementos AEO, score debe ser 0
        assert result == "0", f"Citabilidad NO debe dar puntos AEO. Esperaba '0', obtuve '{result}'"

    def test_aeo_only_schema_faq(self):
        """Solo FAQ schema → 25pts."""
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result(
            faq_schema_detected=True, faq_schema_valid=True,
        )
        result = gen._calculate_aeo_score(audit)
        assert result == "25", f"Esperaba '25', obtuve '{result}'"

    def test_aeo_only_open_graph(self):
        """Solo Open Graph → 15pts (open_graph=15 en CHECKLIST_AEO)."""
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result(open_graph=True)
        result = gen._calculate_aeo_score(audit)
        assert result == "15", f"Esperaba '15', obtuve '{result}'"

    def test_aeo_only_schema_hotel_aeo(self):
        """Solo Schema Hotel válido → 15pts."""
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result(
            hotel_schema_detected=True, hotel_schema_valid=True,
        )
        result = gen._calculate_aeo_score(audit)
        assert result == "15", f"Esperaba '15', obtuve '{result}'"

    def test_aeo_only_contenido_factual(self):
        """contenido_factual requiere schema_hotel_valid=True + hours.

        Escenario: schema valido + hours, sin FAQ ni OG.
        → schema_hotel_aeo(15) + contenido_factual(20) = 35
        """
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result(
            hotel_schema_detected=True, hotel_schema_valid=True,
            contenido_factual=True,  # necesita schema_valid=True + hours
        )
        result = gen._calculate_aeo_score(audit)
        # schema_hotel_aeo(15) + contenido_factual(20) = 35
        assert result == "35", f"Esperaba '35', obtuve '{result}'"

    def test_aeo_speakable_schema_not_implemented(self):
        """speakable_schema siempre False (sin detector implementado)."""
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result(
            faq_schema_detected=True, faq_schema_valid=True,
            speakable_schema=True,  # parametro existe pero no tiene efecto
        )
        result = gen._calculate_aeo_score(audit)
        # Solo FAQ: 25 (speakable_schema no se puede activar)
        assert result == "25", f"Esperaba '25', obtuve '{result}'"

    def test_aeo_only_imagenes_alt(self):
        """Solo imagenes con alt → 15pts."""
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result(imagenes_alt=True)
        result = gen._calculate_aeo_score(audit)
        assert result == "15", f"Esperaba '15', obtuve '{result}'"

    def test_aeo_partial(self):
        """Combinación parcial: schema_faq(25) + open_graph(15) = 40."""
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result(
            faq_schema_detected=True, faq_schema_valid=True,
            open_graph=True,
        )
        result = gen._calculate_aeo_score(audit)
        assert result == "40", f"Esperaba '40', obtuve '{result}'"


class TestAEOScoreSerpAPIIntegration:
    """Integración con SerpAPI: ponderación 60/40."""

    def test_aeo_sin_serpapi_usa_checklist(self):
        """Sin datos SerpAPI, usa solo checklist score."""
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result(
            faq_schema_detected=True, faq_schema_valid=True,  # 25pts
            open_graph=True,  # 15pts
        )
        result = gen._calculate_aeo_score(audit)
        assert result == "40"

    def test_aeo_con_serpapi_pondera_60_40(self):
        """Con SerpAPI real, pondera 60% checklist + 40% snippet_score."""
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        # Checklist: faq(25) + og(15) = 40
        # SerpAPI snippet_score: 50
        # Esperado: 40*0.6 + 50*0.4 = 24 + 20 = 44
        audit = _make_audit_result(
            faq_schema_detected=True, faq_schema_valid=True,
            open_graph=True,
            aeo_snippets_source="serpapi",
            snippet_score=50,
        )
        result = gen._calculate_aeo_score(audit)
        assert result == "44", f"Esperaba '44', obtuve '{result}'"

    def test_aeo_serpapi_stub_no_pondera(self):
        """Con source=stub, NO se aplica ponderación (usa solo checklist)."""
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result(
            faq_schema_detected=True, faq_schema_valid=True,
            open_graph=True,
            aeo_snippets_source="stub",
            snippet_score=80,  # Ignorado porque es stub
        )
        result = gen._calculate_aeo_score(audit)
        # Debe dar 40 (checklist), no ponderado
        assert result == "40", f"Con stub, no debe ponderar. Esperaba '40', obtuve '{result}'"


class TestAEOScoreEdgeCases:
    """Casos borde."""

    def test_aeo_no_data(self):
        """audit_result sin elementos AEO → '0'."""
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result()
        result = gen._calculate_aeo_score(audit)
        assert result == "0", f"Esperaba '0', obtuve '{result}'"

    def test_aeo_none_audit_result(self):
        """audit_result=None → '0'."""
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        result = gen._calculate_aeo_score(None)
        assert result == "0", f"Esperaba '0', obtuve '{result}'"

    def test_aeo_max_100(self):
        """Score nunca supera 100."""
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result(
            hotel_schema_detected=True, hotel_schema_valid=True,
            faq_schema_detected=True, faq_schema_valid=True,
            open_graph=True,
            imagenes_alt=True,
            contenido_factual=True,
            speakable_schema=True,
            aeo_snippets_source="serpapi",
            snippet_score=100,
        )
        result = gen._calculate_aeo_score(audit)
        assert int(result) <= 100, f"Score supera 100: {result}"

    def test_aeo_int_conversion(self):
        """Retorno compatible con _get_score_status() (int() no falla)."""
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result(open_graph=True)
        result = gen._calculate_aeo_score(audit)
        as_int = int(result)  # No debe lanzar ValueError
        assert as_int == 15

    def test_aeo_realistic_hotel(self):
        """Hotel típico: schema sí, FAQ no, OG sí, horas GBP sí → 50."""
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result(
            hotel_schema_detected=True, hotel_schema_valid=True,
            faq_schema_detected=False, faq_schema_valid=False,
            open_graph=True,
            contenido_factual=True,
        )
        result = gen._calculate_aeo_score(audit)
        # schema_hotel_aeo(15) + open_graph(15) + contenido_factual(20) = 50
        assert result == "50", f"Esperaba '50', obtuve '{result}'"


# ===========================================================================
# Tests para calcular_score_aeo() (función pura, independiente)
# ===========================================================================

class TestCalcularScoreAEOFUNCION:
    """Tests para la función pura calcular_score_aeo()."""

    def test_calcular_score_aeo_all_true(self):
        """Todos los elementos del checklist True = 100."""
        elems = {k: True for k in CHECKLIST_AEO}
        assert calcular_score_aeo(elems) == 100

    def test_calcular_score_aeo_all_false(self):
        """Todos False = 0."""
        elems = {k: False for k in CHECKLIST_AEO}
        assert calcular_score_aeo(elems) == 0

    def test_calcular_score_aeo_empty(self):
        """Diccionario vacío = 0."""
        assert calcular_score_aeo({}) == 0
        assert calcular_score_aeo(None) == 0

    def test_calcular_score_aeo_partial(self):
        """Algunos elementos True."""
        elems = {k: False for k in CHECKLIST_AEO}
        elems["schema_faq"] = True  # 25pts
        elems["open_graph"] = True  # 15pts
        assert calcular_score_aeo(elems) == 40

    def test_calcular_score_aeo_cap_100(self):
        """Score nunca supera 100."""
        elems = {k: True for k in CHECKLIST_AEO}
        elems["extra_key"] = True  # Key extra no afecta
        assert calcular_score_aeo(elems) == 100

    def test_calcular_score_aeo_ignore_unknown(self):
        """Keys desconocidas se ignoran."""
        elems = {"unknown_key": True}
        assert calcular_score_aeo(elems) == 0


# ===========================================================================
# Tests CHECKLIST_AEO
# ===========================================================================

class TestChecklistAEO:
    """CHECKLIST_AEO tiene los pesos correctos."""

    def test_aeo_sums_100(self):
        """CHECKLIST_AEO suma exactamente 100pts."""
        assert sum(CHECKLIST_AEO.values()) == 100, \
            f"AEO suma {sum(CHECKLIST_AEO.values())}, no 100"

    def test_aeo_keys(self):
        """CHECKLIST_AEO tiene las 6 keys esperadas."""
        expected_keys = {
            "schema_faq", "open_graph", "schema_hotel_aeo",
            "contenido_factual", "speakable_schema", "imagenes_alt_aeo",
        }
        assert set(CHECKLIST_AEO.keys()) == expected_keys

    def test_aeo_no_citability(self):
        """Citabilidad NO está en CHECKLIST_AEO (movida a IAO)."""
        assert "citability_score" not in CHECKLIST_AEO, \
            "citability_score NO debe estar en CHECKLIST_AEO (pertenece a IAO)"
