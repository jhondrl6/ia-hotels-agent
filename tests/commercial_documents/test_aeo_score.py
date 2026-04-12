"""
Tests para _calculate_aeo_score() — FASE-B: AEO Scoring Rewrite.

4 componentes × 25pts = 100pts:
  1. Schema Hotel válido (25pts)
  2. FAQ Schema válido (25pts)
  3. Open Graph detectado (25pts)
  4. Citabilidad (25pts)

TDD RED phase: estos tests definen el comportamiento esperado
antes de reescribir _calculate_aeo_score().
"""

import types
import pytest

from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
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
    citability_score=None,
    mobile_score=None,
):
    """Crea un V4AuditResult + inyecta seo_elements y citability como attrs dinámicos."""
    schema = SchemaValidation(
        hotel_schema_detected=hotel_schema_detected,
        hotel_schema_valid=hotel_schema_valid,
        hotel_confidence="detected" if hotel_schema_detected else "none",
        faq_schema_detected=faq_schema_detected,
        faq_schema_valid=faq_schema_valid,
        faq_confidence="detected" if faq_schema_detected else "none",
        org_schema_detected=False,
        total_schemas=0,
    )
    performance = PerformanceData(
        has_field_data=mobile_score is not None,
        mobile_score=mobile_score,
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

    # Inyectar seo_elements (Optional, existe si FASE-A corrió)
    seo_mock = types.SimpleNamespace(open_graph=open_graph, imagenes_alt=False, redes_activas=False)
    audit.seo_elements = seo_mock

    # Inyectar citability (Optional, advisory)
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

    return audit


# ---------------------------------------------------------------------------
# Tests RED — definidos ANTES de la implementación
# ---------------------------------------------------------------------------

class TestAEOScoreAllValid:
    """Todos los componentes presentes y válidos → 100."""

    def test_aeo_all_valid(self):
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result(
            hotel_schema_detected=True, hotel_schema_valid=True,
            faq_schema_detected=True, faq_schema_valid=True,
            open_graph=True,
            citability_score=85,
        )
        result = gen._calculate_aeo_score(audit)
        assert result == "100", f"Esperaba '100', obtuve '{result}'"


class TestAEOScoreOnlySchemaValid:
    """Solo schema hotel válido, resto ausente → 25."""

    def test_aeo_only_schema_valid(self):
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result(
            hotel_schema_detected=True, hotel_schema_valid=True,
        )
        result = gen._calculate_aeo_score(audit)
        assert result == "25", f"Esperaba '25', obtuve '{result}'"


class TestAEOScoreSchemaDetectedNotValid:
    """Schema detectado pero NO válido → +10, no +25."""

    def test_aeo_schema_detected_not_valid(self):
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result(
            hotel_schema_detected=True, hotel_schema_valid=False,
        )
        result = gen._calculate_aeo_score(audit)
        assert result == "10", f"Esperaba '10', obtuve '{result}'"


class TestAEOScoreOnlyOG:
    """Solo Open Graph presente → 25."""

    def test_aeo_only_og(self):
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result(open_graph=True)
        result = gen._calculate_aeo_score(audit)
        assert result == "25", f"Esperaba '25', obtuve '{result}'"


class TestAEOScoreCitabilityTiers:
    """Citabilidad con tiers: >=70→+25, >=40→+15, >0→+5, None→0."""

    def test_citability_high(self):
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result(citability_score=80)
        result = gen._calculate_aeo_score(audit)
        assert result == "25", f"Esperaba '25' (cit>=70), obtuve '{result}'"

    def test_citability_mid(self):
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result(citability_score=50)
        result = gen._calculate_aeo_score(audit)
        assert result == "15", f"Esperaba '15' (cit>=40), obtuve '{result}'"

    def test_citability_low(self):
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result(citability_score=10)
        result = gen._calculate_aeo_score(audit)
        assert result == "5", f"Esperaba '5' (cit>0), obtuve '{result}'"

    def test_citability_none(self):
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result(citability_score=None)
        result = gen._calculate_aeo_score(audit)
        assert result == "0", f"Esperaba '0' (cit=None), obtuve '{result}'"


class TestAEOScoreNoData:
    """audit_result con todo None/False → '0'."""

    def test_aeo_no_data(self):
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result()
        result = gen._calculate_aeo_score(audit)
        assert result == "0", f"Esperaba '0', obtuve '{result}'"


class TestAEOScoreNoneAuditResult:
    """audit_result=None → '0'."""

    def test_aeo_none_audit_result(self):
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        result = gen._calculate_aeo_score(None)
        assert result == "0", f"Esperaba '0', obtuve '{result}'"


class TestAEOScoreMax100:
    """Score nunca supera 100."""

    def test_aeo_max_100(self):
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        # Si hubiera lógica que sumara >100, debe capar a 100
        audit = _make_audit_result(
            hotel_schema_detected=True, hotel_schema_valid=True,
            faq_schema_detected=True, faq_schema_valid=True,
            open_graph=True,
            citability_score=100,
        )
        result = gen._calculate_aeo_score(audit)
        assert int(result) <= 100, f"Score supera 100: {result}"


class TestAEOScoreCompatibleWithStatus:
    """Retorno compatible con _get_score_status() (int() no falla)."""

    def test_int_conversion(self):
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result(open_graph=True)
        result = gen._calculate_aeo_score(audit)
        # No debe lanzar ValueError
        as_int = int(result)
        assert as_int == 25

    def test_get_score_status_works(self):
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        # Simular _get_score_status con score "50"
        status = gen._get_score_status("50", 20)
        assert status == "✅ Superior", f"Esperaba '✅ Superior', obtuve '{status}'"

    def test_get_score_status_bajo(self):
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        status = gen._get_score_status("0", 20)
        assert status == "❌ Bajo", f"Esperaba '❌ Bajo', obtuve '{status}'"


class TestAEOScoreRealisticHotel:
    """Hotel típico: schema sí, FAQ no, OG sí, cit=None → 50."""

    def test_aeo_realistic_hotel(self):
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result(
            hotel_schema_detected=True, hotel_schema_valid=True,
            open_graph=True,
            citability_score=None,
        )
        result = gen._calculate_aeo_score(audit)
        assert result == "50", f"Esperaba '50', obtuve '{result}'"


# ===========================================================================
# FASE-A: Tests 4-Pilar Scoring
# ===========================================================================

from modules.commercial_documents.v4_diagnostic_generator import (
    CHECKLIST_SEO, CHECKLIST_GEO, CHECKLIST_AEO, CHECKLIST_IAO,
    calcular_score_seo, calcular_score_geo, calcular_score_aeo, calcular_score_iao,
    calcular_score_global, calcular_cumplimiento, sugerir_paquete,
    ELEMENTO_KB_TO_PAIN_ID,
)


class TestChecklistWeights:
    """Cada diccionario de checklist suma exactamente 100pts."""

    def test_seo_sums_100(self):
        assert sum(CHECKLIST_SEO.values()) == 100, f"SEO suma {sum(CHECKLIST_SEO.values())}"

    def test_geo_sums_100(self):
        assert sum(CHECKLIST_GEO.values()) == 100, f"GEO suma {sum(CHECKLIST_GEO.values())}"

    def test_aeo_sums_100(self):
        assert sum(CHECKLIST_AEO.values()) == 100, f"AEO suma {sum(CHECKLIST_AEO.values())}"

    def test_iao_sums_100(self):
        assert sum(CHECKLIST_IAO.values()) == 100, f"IAO suma {sum(CHECKLIST_IAO.values())}"


class TestCalcularScorePilar:
    """calcular_score_* retorna 0-100."""

    def test_seo_all_true(self):
        elems = {k: True for k in CHECKLIST_SEO}
        assert calcular_score_seo(elems) == 100

    def test_seo_all_false(self):
        elems = {k: False for k in CHECKLIST_SEO}
        assert calcular_score_seo(elems) == 0

    def test_seo_empty(self):
        assert calcular_score_seo({}) == 0
        assert calcular_score_seo(None) == 0

    def test_seo_partial(self):
        elems = {k: False for k in CHECKLIST_SEO}
        elems["ssl"] = True  # 15pts
        assert calcular_score_seo(elems) == 15

    def test_geo_all_true(self):
        elems = {k: True for k in CHECKLIST_GEO}
        assert calcular_score_geo(elems) == 100

    def test_aeo_all_true(self):
        elems = {k: True for k in CHECKLIST_AEO}
        assert calcular_score_aeo(elems) == 100

    def test_iao_all_true(self):
        elems = {k: True for k in CHECKLIST_IAO}
        assert calcular_score_iao(elems) == 100

    def test_score_cap_100(self):
        """Score nunca supera 100."""
        elems = {k: True for k in CHECKLIST_SEO}
        elems["extra_key"] = True  # Key extra no afecta
        assert calcular_score_seo(elems) == 100

    def test_ignore_unknown_keys(self):
        """Keys desconocidas se ignoran."""
        elems = {"unknown_key": True}
        assert calcular_score_seo(elems) == 0


class TestCalcularScoreGlobal:
    """Score global = promedio ponderado 4 pilares."""

    def test_all_100(self):
        assert calcular_score_global(100, 100, 100, 100) == 100

    def test_all_0(self):
        assert calcular_score_global(0, 0, 0, 0) == 0

    def test_equal_scores(self):
        assert calcular_score_global(50, 50, 50, 50) == 50

    def test_one_pilar_zero(self):
        assert calcular_score_global(100, 0, 0, 0) == 25

    def test_asymmetric(self):
        # (80*0.25 + 60*0.25 + 40*0.25 + 20*0.25) = 20+15+10+5 = 50
        assert calcular_score_global(80, 60, 40, 20) == 50


class TestBackwardCompat:
    """calcular_cumplimiento() sigue funcionando igual."""

    def test_legacy_all_true(self):
        """Los 12 elementos originales True = 100."""
        elems = {k: True for k in ELEMENTO_KB_TO_PAIN_ID}
        assert calcular_cumplimiento(elems) == 100

    def test_legacy_empty(self):
        assert calcular_cumplimiento({}) == 0
        assert calcular_cumplimiento(None) == 0

    def test_legacy_ssl_only(self):
        elems = {k: False for k in ELEMENTO_KB_TO_PAIN_ID}
        elems["ssl"] = True  # 10pts legacy
        assert calcular_cumplimiento(elems) == 10

    def test_sugerir_paquete_acepta_score_global(self):
        """sugerir_paquete funciona con score_global (0-100)."""
        assert sugerir_paquete(20) == "basico"
        assert sugerir_paquete(50) == "avanzado"
        assert sugerir_paquete(80) == "premium"


class TestExtraerElementosPilar:
    """_extraer_elementos_* extrae correctamente."""

    def test_seo_extraction(self):
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result(
            hotel_schema_detected=True, hotel_schema_valid=True,
            mobile_score=80,
        )
        # Simular LCP/CLS
        audit.performance.lcp = 1.5
        audit.performance.cls = 0.05
        elems = gen._extraer_elementos_seo(audit)
        assert elems["ssl"] is True  # https URL
        assert elems["schema_hotel"] is True
        assert elems["LCP_ok"] is True
        assert elems["CLS_ok"] is True
        assert elems["blog_activo"] is False

    def test_seo_none_audit(self):
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        elems = gen._extraer_elementos_seo(None)
        assert all(v is False for v in elems.values())

    def test_geo_extraction(self):
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result()
        audit.gbp.place_found = True
        audit.gbp.geo_score = 80
        audit.gbp.photos = 5
        audit.gbp.hours = "9am-6pm"
        elems = gen._extraer_elementos_geo(audit)
        assert elems["geo_score_gbp"] is True  # >=70
        assert elems["fotos_gbp"] is True  # >=3
        assert elems["horario_gbp"] is True

    def test_aeo_extraction(self):
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result(
            hotel_schema_detected=True, hotel_schema_valid=True,
            faq_schema_detected=True, faq_schema_valid=True,
            open_graph=True,
        )
        audit.gbp.hours = "9am-6pm"
        elems = gen._extraer_elementos_aeo(audit)
        assert elems["schema_faq"] is True
        assert elems["open_graph"] is True
        assert elems["schema_hotel_aeo"] is True
        assert elems["contenido_factual"] is True
        assert elems["speakable_schema"] is False  # sin detector

    def test_iao_extraction(self):
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result(citability_score=80)
        elems = gen._extraer_elementos_iao(audit)
        assert elems["citability_score"] is True
        assert elems["contenido_extenso"] is True
        assert elems["llms_txt_exists"] is False  # sin detector
        assert elems["crawler_access"] is False  # sin detector

    def test_wrapper_backward_compat(self):
        """_extraer_elementos_de_audit contiene los 12 elementos originales."""
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = _make_audit_result(
            hotel_schema_detected=True,
            open_graph=True,
        )
        elems = gen._extraer_elementos_de_audit(audit)
        for key in ELEMENTO_KB_TO_PAIN_ID:
            assert key in elems, f"Falta elemento original: {key}"


class TestDiagnosticSummaryFields:
    """DiagnosticSummary acepta nuevos campos sin error."""

    def test_new_fields_default_none(self):
        from modules.commercial_documents.data_structures import DiagnosticSummary
        ds = DiagnosticSummary(
            hotel_name="Test",
            critical_problems_count=0,
            quick_wins_count=0,
            overall_confidence="unknown",
        )
        assert ds.score_seo is None
        assert ds.score_geo is None
        assert ds.score_aeo is None
        assert ds.score_iao is None
        assert ds.score_global is None
        assert ds.elementos_seo is None

    def test_new_fields_accept_values(self):
        from modules.commercial_documents.data_structures import DiagnosticSummary
        ds = DiagnosticSummary(
            hotel_name="Test",
            critical_problems_count=0,
            quick_wins_count=0,
            overall_confidence="unknown",
            score_seo=80,
            score_geo=60,
            score_aeo=40,
            score_iao=20,
            score_global=50,
            elementos_seo={"ssl": True},
        )
        assert ds.score_seo == 80
        assert ds.score_global == 50
        assert ds.elementos_seo["ssl"] is True
