"""
Tests for _identify_critical_issues expansion (FASE-G G2/NR2).

Two new critical-issue criteria:
- PageSpeed ``status == "ERROR"``: the performance axis was NOT measurable,
  so "zero critical issues" cannot be affirmed from a fallen axis
  (SalentoReal 2026-08-31: critical_recall vacuo 1.0 con PageSpeed caído).
- GEO band critical (0-35) via ``geo_flow_result`` (optional param; the geo
  flow runs AFTER the audit inside the asset orchestrator, so the assessment
  builder is the wiring point — helper shared at module level).

The 4 pre-existing criteria must remain intact (no-regression).
"""

import pytest

from modules.auditors.v4_comprehensive import (
    GEO_CRITICAL_MAX_SCORE,
    CrossValidationResult,
    GBPApiResult,
    PerformanceResult,
    SchemaAuditResult,
    V4ComprehensiveAuditor,
    geo_band_critical_issue,
)
from modules.data_validation import ConfidenceLevel


# =============================================================================
# Fixtures
# =============================================================================

def make_schema(detected: bool = True, valid: bool = True) -> SchemaAuditResult:
    return SchemaAuditResult(
        hotel_schema_detected=detected,
        hotel_schema_valid=valid,
        hotel_confidence="VERIFIED" if detected else "MISSING",
        faq_schema_detected=True,
        faq_schema_valid=True,
        faq_confidence="VERIFIED",
        org_schema_detected=True,
        total_schemas=3,
    )


def make_gbp(geo_score: int = 79) -> GBPApiResult:
    return GBPApiResult(
        place_found=True,
        place_id="ChIJtest",
        name="Hotel Salento Real",
        rating=4.2,
        reviews=986,
        photos=38,
        phone="+57 6 1234567",
        website="https://hotelsalentoreal.com",
        address="Calle Real, Salento",
        geo_score=geo_score,
        geo_score_breakdown={},
        confidence="VERIFIED",
    )


def make_perf(
    status: str = "OK",
    has_field_data: bool = True,
    mobile_score: int = 72,
) -> PerformanceResult:
    return PerformanceResult(
        has_field_data=has_field_data,
        mobile_score=mobile_score,
        desktop_score=80,
        lcp=2.1,
        fid=90,
        cls=0.05,
        status=status,
        message=(
            "Invalid URL or request: API key not valid"
            if status == "ERROR"
            else ""
        ),
    )


def make_validation(
    whatsapp_status: str = "VERIFIED",
) -> CrossValidationResult:
    return CrossValidationResult(
        whatsapp_status=whatsapp_status,
        phone_web="+57 6 1234567",
        phone_gbp="+57 6 1234567",
        adr_status="OK",
        adr_web=350000.0,
        adr_benchmark=340000.0,
    )


# Fixture shape mirrors the real SalentoReal run (2026-08-31):
# gbp.geo_score=79, performance.status=ERROR ("API key not valid"),
# geo_flow_result.json = {"success": true, "case": "critical",
#   "geo_assessment": {"total_score": 29, "band": "critical"}}

SALENTOREAL_GEO_FLOW = {
    "success": True,
    "case": "critical",
    "geo_assessment": {"total_score": 29, "band": "critical"},
}


@pytest.fixture
def auditor() -> V4ComprehensiveAuditor:
    return V4ComprehensiveAuditor()


def identify(auditor, **overrides):
    return auditor._identify_critical_issues(
        schema=overrides.get("schema", make_schema()),
        gbp=overrides.get("gbp", make_gbp()),
        perf=overrides.get("perf", make_perf()),
        validation=overrides.get("validation", make_validation()),
        geo_flow_result=overrides.get("geo_flow_result"),
    )


# =============================================================================
# New criterion: PageSpeed ERROR
# =============================================================================

class TestPageSpeedErrorCriterion:
    def test_pagespeed_error_qualifies(self, auditor):
        """perf.status=ERROR → critical issue (eje de rendimiento no medible)."""
        issues = identify(auditor, perf=make_perf(status="ERROR"))
        assert any("PageSpeed API ERROR" in i for i in issues)

    def test_pagespeed_ok_does_not_qualify(self, auditor):
        issues = identify(auditor, perf=make_perf(status="OK"))
        assert not any("PageSpeed API ERROR" in i for i in issues)

    def test_salentoreal_fixture_single_new_issue(self, auditor):
        """Fixture SalentoReal: schema OK, geo_score 79, perf ERROR, sin geo
        flow → exactamente 1 issue (el PageSpeed ERROR)."""
        issues = identify(
            auditor,
            gbp=make_gbp(geo_score=79),
            perf=make_perf(status="ERROR"),
            geo_flow_result=None,
        )
        assert len(issues) == 1
        assert "PageSpeed API ERROR" in issues[0]


# =============================================================================
# New criterion: GEO band critical
# =============================================================================

class TestGeoBandCriticalCriterion:
    def test_geo_band_critical_qualifies(self, auditor):
        """band='critical' (score 29) → critical issue."""
        issues = identify(
            auditor, geo_flow_result=dict(SALENTOREAL_GEO_FLOW)
        )
        assert any("GEO readiness critical" in i for i in issues)

    def test_geo_score_below_threshold_qualifies_even_without_band(self, auditor):
        """score <= 35 sin banda explícita → critical (GEOBand.CRITICAL = 0-35)."""
        issues = identify(
            auditor,
            geo_flow_result={"geo_assessment": {"total_score": 20, "band": ""}},
        )
        assert any("GEO readiness critical" in i for i in issues)

    def test_geo_not_critical_no_issue(self, auditor):
        """band sólida con score alto → no emite."""
        issues = identify(
            auditor,
            geo_flow_result={"geo_assessment": {"total_score": 79, "band": "solid"}},
        )
        assert not any("GEO readiness critical" in i for i in issues)

    def test_geo_absent_no_issue(self, auditor):
        """Sin geo flow result → no emite (vacío ≠ ausente, L-SR5)."""
        issues = identify(auditor, geo_flow_result=None)
        assert not any("GEO readiness critical" in i for i in issues)

    def test_geo_no_assessment_key_no_issue(self, auditor):
        issues = identify(
            auditor, geo_flow_result={"success": True, "case": "ok"}
        )
        assert not any("GEO readiness critical" in i for i in issues)

    def test_helper_accepts_to_dict_object(self, auditor):
        """El helper también acepta objetos con to_dict() (no dict)."""

        class _GeoResult:
            def to_dict(self):
                return dict(SALENTOREAL_GEO_FLOW)

        issue = geo_band_critical_issue(_GeoResult())
        assert issue is not None
        assert "GEO readiness critical" in issue

    def test_threshold_matches_sync_contract(self):
        """GEO_CRITICAL_MAX_SCORE replica GEOBand.CRITICAL = 0-35."""
        assert GEO_CRITICAL_MAX_SCORE == 35


# =============================================================================
# No-regression: pre-existing criteria intact
# =============================================================================

class TestLegacyCriteriaIntact:
    def test_no_hotel_schema_detected(self, auditor):
        issues = identify(auditor, schema=make_schema(detected=False))
        assert any("No Hotel schema detected" in i for i in issues)

    def test_hotel_schema_invalid(self, auditor):
        issues = identify(auditor, schema=make_schema(detected=True, valid=False))
        assert any("Hotel schema has validation errors" in i for i in issues)

    def test_whatsapp_conflict(self, auditor):
        issues = identify(
            auditor,
            validation=make_validation(
                whatsapp_status=ConfidenceLevel.CONFLICT.value
            ),
        )
        assert any("WhatsApp number conflict" in i for i in issues)

    def test_low_geo_score(self, auditor):
        issues = identify(auditor, gbp=make_gbp(geo_score=42))
        assert any("Low GBP geo_score" in i for i in issues)

    def test_poor_mobile_performance(self, auditor):
        issues = identify(
            auditor, perf=make_perf(status="OK", has_field_data=True, mobile_score=38)
        )
        assert any("Poor mobile performance" in i for i in issues)

    def test_healthy_audit_yields_no_issues(self, auditor):
        """Audit sano completo → lista vacía (favorable SR-H2 no contaminado)."""
        issues = identify(auditor)
        assert issues == []
