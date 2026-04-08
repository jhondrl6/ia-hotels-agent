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
