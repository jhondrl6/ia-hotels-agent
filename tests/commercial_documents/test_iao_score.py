"""
Tests for IAO Score calculation — FASE-C IAO Restoration.

Tests cover:
- IAO score básico (sin datos = 0)
- IAO con citabilidad alta
- IAO con LLM report data (ponderación 50/50)
- IAO no confunde con AEO (citabilidad está en IAO)
- _extraer_elementos_iao con datos reales
"""

import pytest
from unittest.mock import MagicMock, patch
from modules.commercial_documents.v4_diagnostic_generator import (
    calcular_score_iao,
    calcular_score_global,
    CHECKLIST_IAO,
    V4DiagnosticGenerator,
)


class TestCalcularScoreIao:
    """Tests for calcular_score_iao() function."""

    def test_empty_elements_returns_zero(self):
        """Sin elementos, score = 0."""
        score = calcular_score_iao({})
        assert score == 0

    def test_all_false_returns_zero(self):
        """Todos los elementos en False, score = 0."""
        elementos = {k: False for k in CHECKLIST_IAO}
        score = calcular_score_iao(elementos)
        assert score == 0

    def test_all_true_returns_100(self):
        """Todos los elementos en True, score = 100."""
        elementos = {k: True for k in CHECKLIST_IAO}
        score = calcular_score_iao(elementos)
        assert score == 100

    def test_partial_elements(self):
        """Solo algunos elementos activos."""
        elementos = {k: False for k in CHECKLIST_IAO}
        elementos["citability_score"] = True  # 20pts
        elementos["contenido_extenso"] = True  # 15pts
        score = calcular_score_iao(elementos)
        assert score == 35  # 20 + 15

    def test_citability_in_iao_not_aeo(self):
        """Citabilidad está en CHECKLIST_IAO, NO en CHECKLIST_AEO."""
        assert "citability_score" in CHECKLIST_IAO
        from modules.commercial_documents.v4_diagnostic_generator import CHECKLIST_AEO
        assert "citability_score" not in CHECKLIST_AEO


class TestCalcularScoreGlobal:
    """Tests for calcular_score_global() — 4-pillar average."""

    def test_equal_scores(self):
        """4 pilares iguales = mismo score."""
        score = calcular_score_global(50, 50, 50, 50)
        assert score == 50

    def test_zero_iao_brings_down_global(self):
        """IAO = 0 reduce score global."""
        score_with = calcular_score_global(80, 80, 80, 80)
        score_without = calcular_score_global(80, 80, 80, 0)
        assert score_without < score_with

    def test_all_zeros(self):
        """Todos en 0 = 0."""
        score = calcular_score_global(0, 0, 0, 0)
        assert score == 0

    def test_all_max(self):
        """Todos en 100 = 100."""
        score = calcular_score_global(100, 100, 100, 100)
        assert score == 100


class TestExtraerElementosIao:
    """Tests for _extraer_elementos_iao() with real audit data."""

    def _make_mock_audit(self, **kwargs):
        """Create mock V4AuditResult with configurable fields."""
        audit = MagicMock()
        audit.citability = kwargs.get('citability', None)
        audit.ai_crawlers = kwargs.get('ai_crawlers', None)
        audit.schema = kwargs.get('schema', None)
        audit.llm_report = kwargs.get('llm_report', None)
        return audit

    def test_no_audit_result_returns_all_false(self):
        """Sin audit_result, todos los elementos son False."""
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        elementos = gen._extraer_elementos_iao(None)
        assert all(v is False for v in elementos.values())

    def test_high_citability(self):
        """Citabilidad > 50 activa citability_score y contenido_extenso."""
        cit = MagicMock()
        cit.overall_score = 75

        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = self._make_mock_audit(citability=cit)
        elementos = gen._extraer_elementos_iao(audit)

        assert elementos["citability_score"] is True
        assert elementos["contenido_extenso"] is True

    def test_low_citability(self):
        """Citabilidad <= 50 no activa elementos."""
        cit = MagicMock()
        cit.overall_score = 30

        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = self._make_mock_audit(citability=cit)
        elementos = gen._extraer_elementos_iao(audit)

        assert elementos["citability_score"] is False
        assert elementos["contenido_extenso"] is False

    def test_crawler_access_from_ai_crawlers(self):
        """ai_crawlers.overall_score > 50 activa crawler_access."""
        crawlers = MagicMock()
        crawlers.overall_score = 80

        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = self._make_mock_audit(ai_crawlers=crawlers)
        elementos = gen._extraer_elementos_iao(audit)

        assert elementos["crawler_access"] is True

    def test_schema_advanced_from_org_schema(self):
        """schema.org_schema_detected activa schema_advanced."""
        schema = MagicMock()
        schema.org_schema_detected = True
        schema.properties = {}

        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = self._make_mock_audit(schema=schema)
        elementos = gen._extraer_elementos_iao(audit)

        assert elementos["schema_advanced"] is True

    def test_brand_signals_from_sameas(self):
        """SameAs en schema.properties activa brand_signals."""
        schema = MagicMock()
        schema.org_schema_detected = False
        schema.properties = {"sameAs": ["https://facebook.com/hotel"]}

        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)
        audit = self._make_mock_audit(schema=schema)
        elementos = gen._extraer_elementos_iao(audit)

        assert elementos["brand_signals"] is True


class TestIaoScoreWithLlmReport:
    """Tests for IAO score adjustment with LLM report data."""

    def test_stub_report_no_adjustment(self):
        """LLM report con source='stub' no ajusta score."""
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)

        # Mock _extraer_elementos_iao to return known elements
        gen._extraer_elementos_iao = MagicMock(return_value={
            "citability_score": True,
            "contenido_extenso": True,
            "llms_txt_exists": False,
            "crawler_access": False,
            "brand_signals": False,
            "ga4_indirect": False,
            "schema_advanced": False,
        })

        audit = MagicMock()
        llm_report = MagicMock()
        llm_report.source = "stub"
        llm_report.mention_score = 80
        audit.llm_report = llm_report

        score = gen._calculate_iao_score_from_audit(audit)
        # Base score = 20 + 15 = 35. Stub doesn't adjust.
        assert score == "35"

    def test_real_llm_report_50_50_ponderation(self):
        """LLM report con datos reales aplica ponderación 50/50."""
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)

        gen._extraer_elementos_iao = MagicMock(return_value={
            "citability_score": True,
            "contenido_extenso": True,
            "llms_txt_exists": False,
            "crawler_access": False,
            "brand_signals": False,
            "ga4_indirect": False,
            "schema_advanced": False,
        })

        audit = MagicMock()
        llm_report = MagicMock()
        llm_report.source = "llm_check"
        llm_report.mention_score = 60  # Real LLM data
        audit.llm_report = llm_report

        score = gen._calculate_iao_score_from_audit(audit)
        # Base = 35, real = 60
        # Pondered: 35*0.5 + 60*0.5 = 17.5 + 30 = 47.5 → int = 47
        assert score == "47"

    def test_no_llm_report_uses_base_score(self):
        """Sin llm_report, usa solo checklist score."""
        gen = V4DiagnosticGenerator.__new__(V4DiagnosticGenerator)

        gen._extraer_elementos_iao = MagicMock(return_value={
            "citability_score": True,
            "contenido_extenso": True,
            "llms_txt_exists": False,
            "crawler_access": False,
            "brand_signals": False,
            "ga4_indirect": False,
            "schema_advanced": False,
        })

        audit = MagicMock()
        audit.llm_report = None

        score = gen._calculate_iao_score_from_audit(audit)
        # Base score = 20 + 15 = 35, no LLM adjustment
        assert score == "35"
