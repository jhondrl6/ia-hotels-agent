"""Tests para modules.financial_engine.opportunity_scorer (FASE-C).

14 tests obligatorios del plan FASE-C:
1.  test_severity_con_competidores
2.  test_severity_sin_competidores
3.  test_effort_faq
4.  test_effort_gbp
5.  test_impact_whatsapp
6.  test_total_score_range
7.  test_ranking
8.  test_cop_estimation
9.  test_justification
10. test_backward_compat
11. test_extractor_from_assessment
12. test_score_from_assessment
13. test_weights_summary
14. test_empty_brechas_returns_empty
"""

import pytest
import sys
import os
from dataclasses import asdict
from uuid import uuid4
from datetime import datetime

# Asegurar que el root del proyecto esta en sys.path
_PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from modules.financial_engine.opportunity_scorer import (
    OpportunityScore,
    OpportunityScorer,
)
from data_models.canonical_assessment import (
    CanonicalAssessment,
    SiteMetadata,
    SchemaAnalysis,
    PerformanceAnalysis,
    PerformanceMetrics,
    GBPAnalysis,
    Claim,
)
from enums.severity import Severity


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


@pytest.fixture()
def scorer() -> OpportunityScorer:
    return OpportunityScorer()


def _make_brecha(_id: str, _type: str, _name: str = "") -> dict:
    return {"id": _id, "type": _type, "name": _name or _id}


def _make_minimal_assessment() -> CanonicalAssessment:
    return CanonicalAssessment(
        url="https://test-hotel.com",
        site_metadata=SiteMetadata(
            title="Test Hotel",
            description="Un hotel de prueba",
            cms_detected="WordPress",
            has_default_title=True,
        ),
        schema_analysis=SchemaAnalysis(
            coverage_score=0.3,
            missing_critical_fields=["image", "aggregateRating", "faq"],
            present_fields=["name"],
            has_hotel_schema=False,
        ),
        performance_analysis=PerformanceAnalysis(
            performance_score=45.0,
            metrics=PerformanceMetrics(lcp=4.0, fcp=2.0),
        ),
        gbp_analysis=GBPAnalysis(
            profile_url="https://g.page/test",
            rating=4.0,
            review_count=8,
            photo_count=5,
            is_claimed=False,
        ),
        claims=[
            Claim(
                source_id="validation",
                evidence_excerpt="WhatsApp +573001234567 vs +573009998877",
                severity=Severity.CRITICAL,
                category="whatsapp",
                message="WhatsApp conflict between web and GBP",
                confidence=0.95,
            ),
            Claim(
                source_id="web",
                evidence_excerpt="ADR web $200 vs ADR benchmark $250",
                severity=Severity.HIGH,
                category="data",
                message="ADR inconsistent sources",
                confidence=0.70,
            ),
        ],
        coherence_score=0.75,
        evidence_coverage=0.90,
        hard_contradictions=1,
    )


# ------------------------------------------------------------------
# 1. Severidad con competidores -> 40 pts
# ------------------------------------------------------------------


def test_severity_con_competidores(scorer: OpportunityScorer):
    """40 pts cuando la mayoria de competidores tienen la brecha."""
    competitor_data = {
        "competitors_with_feature": 4,
        "total_competitors": 5,
    }
    sev = scorer._calc_severity("faq_schema_missing", competitor_data)
    assert sev == 40.0


def test_severity_sin_competidores(scorer: OpportunityScorer):
    """20-25 pts cuando nadie tiene la brecha."""
    competitor_data = {
        "competitors_with_feature": 0,
        "total_competitors": 5,
    }
    sev = scorer._calc_severity("faq_schema_missing", competitor_data)
    assert 20 <= sev <= 25.0


# ------------------------------------------------------------------
# 2-4. Esfuerzo FAQ=30, GBP=25
# ------------------------------------------------------------------


def test_effort_faq(scorer: OpportunityScorer):
    """30 pts para FAQ (asset ya generado)."""
    effort = scorer._calc_effort("faq_schema_missing")
    assert effort == 30.0


def test_effort_gbp(scorer: OpportunityScorer):
    """25 pts para GBP incompleta."""
    effort = scorer._calc_effort("gbp_incomplete")
    assert effort == 25.0


# ------------------------------------------------------------------
# 5. Impacto WhatsApp = 30
# ------------------------------------------------------------------


def test_impact_whatsapp(scorer: OpportunityScorer):
    """30 pts para WhatsApp conflict (reserva directa)."""
    impact = scorer._calc_impact("whatsapp_conflict")
    assert impact == 30.0


# ------------------------------------------------------------------
# 6. Total score siempre 0-100
# ------------------------------------------------------------------


def test_total_score_range(scorer: OpportunityScorer):
    """Total score siempre entre 0 y 100."""
    brechas = [
        _make_brecha("b1", "faq_schema_missing", "Sin FAQ"),
        _make_brecha("b2", "gbp_incomplete", "GBP incompleta"),
        _make_brecha("b3", "whatsapp_conflict", "WhatsApp conflict"),
        _make_brecha("b4", "cms_defaults", "CMS defaults"),
        _make_brecha("b5", "poor_performance", "Performance bajo"),
    ]
    scores = scorer.score_brechas(brechas)
    for s in scores:
        assert 0 <= s.total_score <= 100, f"{s.brecha_id}={s.total_score}"


# ------------------------------------------------------------------
# 7. Ranking ordenado descendente
# ------------------------------------------------------------------


def test_ranking(scorer: OpportunityScorer):
    """Scores rankeados descendente por total_score."""
    brechas = [
        _make_brecha("b1", "cms_defaults"),
        _make_brecha("b2", "whatsapp_conflict"),
        _make_brecha("b3", "faq_schema_missing"),
    ]
    scores = scorer.score_brechas(brechas)

    # Descendente
    for i in range(len(scores) - 1):
        assert scores[i].total_score >= scores[i + 1].total_score

    # Ranks consecutivos desde 1
    ranks = [s.rank for s in scores]
    assert ranks == list(range(1, len(scores) + 1))


# ------------------------------------------------------------------
# 8. COP estimation > 0 cuando score > 0
# ------------------------------------------------------------------


def test_cop_estimation(scorer: OpportunityScorer):
    """Monto > 0 cuando score > 0."""
    brechas = [_make_brecha("b1", "whatsapp_conflict")]
    scores = scorer.score_brechas(brechas, total_monthly_loss=3_000_000)
    assert scores[0].estimated_monthly_cop > 0


def test_cop_estimation_scales(scorer: OpportunityScorer):
    """COP escalable con total_monthly_loss."""
    brechas = [_make_brecha("b1", "whatsapp_conflict")]
    scores_low = scorer.score_brechas(brechas, total_monthly_loss=1_000_000)
    scores_high = scorer.score_brechas(brechas, total_monthly_loss=5_000_000)
    assert scores_high[0].estimated_monthly_cop > scores_low[0].estimated_monthly_cop


# ------------------------------------------------------------------
# 9. Justification legible
# ------------------------------------------------------------------


def test_justification(scorer: OpportunityScorer):
    """String legible no vacio para cada tipo de brecha."""
    for brecha_type in [
        "faq_schema_missing",
        "gbp_incomplete",
        "whatsapp_conflict",
        "cms_defaults",
        "no_hotel_schema",
        "poor_performance",
        "data_inconsistent",
    ]:
        just = scorer._generate_justification(brecha_type, 30, 20, 25)
        assert isinstance(just, str)
        assert len(just) > 20, f"Justification too short for {brecha_type}"


def test_justification_competitor_note(scorer: OpportunityScorer):
    """Justification incluye nota de competidor cuando aplica."""
    competitor_data = {
        "competitors_with_feature": 3,
        "total_competitors": 5,
    }
    just = scorer._generate_justification(
        "faq_schema_missing", 30, 20, 25, competitor_data
    )
    assert "competidor" in just.lower()


# ------------------------------------------------------------------
# 10. Backward compatible (sin scores = fallback)
# ------------------------------------------------------------------


def test_backward_compat(scorer: OpportunityScorer):
    """Brechas vacias retorna lista vacia (no crash)."""
    scores = scorer.score_brechas([])
    assert scores == []


def test_unknown_type(scorer: OpportunityScorer):
    """Tipo desconocido usa defaults y no crashea."""
    brechas = [_make_brecha("b1", "tipo_desconocido_x")]
    scores = scorer.score_brechas(brechas)
    assert len(scores) == 1
    assert 0 <= scores[0].total_score <= 100


# ------------------------------------------------------------------
# 11. Extractor from assessment
# ------------------------------------------------------------------


def test_extractor_from_assessment(scorer: OpportunityScorer):
    """Extrae brechas detectables desde un CanonicalAssessment."""
    assessment = _make_minimal_assessment()
    brechas = scorer._extract_brechas_from_assessment(assessment)

    types = {b["type"] for b in brechas}
    assert len(brechas) >= 2

    # WhatsApp conflict
    assert "whatsapp_conflict" in types
    # CMS defaults (has_default_title=True)
    assert "cms_defaults" in types
    # No hotel schema
    assert "no_hotel_schema" in types


def test_extractor_empty_assessment(scorer: OpportunityScorer):
    """Assessment sin problemas retorna lista vacia."""
    assessment = CanonicalAssessment(
        url="https://perfect-hotel.com",
        site_metadata=SiteMetadata(
            title="Perfect Hotel",
            has_default_title=False,
        ),
        schema_analysis=SchemaAnalysis(
            coverage_score=0.95,
            missing_critical_fields=[],
            present_fields=["name", "image", "aggregateRating"],
            has_hotel_schema=True,
        ),
        performance_analysis=PerformanceAnalysis(
            performance_score=95.0,
            metrics=PerformanceMetrics(lcp=1.0, fcp=0.5),
        ),
        gbp_analysis=GBPAnalysis(
            photo_count=50,
            is_claimed=True,
        ),
        claims=[],
    )
    brechas = scorer._extract_brechas_from_assessment(assessment)
    assert len(brechas) == 0


# ------------------------------------------------------------------
# 12. Score from assessment (end-to-end)
# ------------------------------------------------------------------


def test_score_from_assessment(scorer: OpportunityScorer):
    """score_from_assessment retorna scores rankeados."""
    assessment = _make_minimal_assessment()
    scores = scorer.score_from_assessment(assessment)

    assert len(scores) >= 1
    for s in scores:
        assert isinstance(s.brecha_id, str)
        assert isinstance(s.brecha_name, str)
        assert 0 <= s.severity_score <= 40
        assert 0 <= s.effort_score <= 30
        assert 0 <= s.impact_score <= 30
        assert 0 <= s.total_score <= 100
        assert isinstance(s.rank, int) and s.rank >= 1


# ------------------------------------------------------------------
# 13. Weights summary
# ------------------------------------------------------------------


def test_weights_summary(scorer: OpportunityScorer):
    """Retorna dict correcto con pesos del modelo."""
    summary = scorer.get_weights_summary()
    assert "severidad" in summary
    assert "esfuerzo" in summary
    assert "impacto" in summary
    assert summary["total"] == 100
    assert summary["severidad"]["max"] == 40
    assert summary["esfuerzo"]["max"] == 30
    assert summary["impacto"]["max"] == 30


# ------------------------------------------------------------------
# 14. Empty brechas returns empty
# ------------------------------------------------------------------


def test_empty_brechas_returns_empty(scorer: OpportunityScorer):
    """Lista vacia genera lista vacia de scores."""
    assert scorer.score_brechas([]) == []


# ------------------------------------------------------------------
# 15-20. Tests para mappings faltantes (FASE-C BRECHAS-DINAMICAS)
# ------------------------------------------------------------------


def test_score_brechas_with_low_gbp_score(scorer: OpportunityScorer):
    """Score para GBP bajo — severity 35, effort 25, impact 30 = 90."""
    brechas = [_make_brecha("b1", "low_gbp_score", "Visibilidad Local")]
    scores = scorer.score_brechas(brechas)
    assert len(scores) == 1
    s = scores[0]
    assert 0 <= s.total_score <= 100
    assert s.severity_score == 35.0
    assert s.effort_score == 25.0
    assert s.impact_score == 30.0
    assert "GBP" in s.justification or "Google Maps" in s.justification


def test_score_brechas_with_no_whatsapp_visible(scorer: OpportunityScorer):
    """Score para WhatsApp ausente — severity 35, effort 25, impact 30 = 90."""
    brechas = [_make_brecha("b1", "no_whatsapp_visible", "Sin WhatsApp")]
    scores = scorer.score_brechas(brechas)
    assert len(scores) == 1
    s = scores[0]
    assert s.severity_score == 35.0
    assert s.effort_score == 25.0
    assert s.impact_score == 30.0
    assert "WhatsApp" in s.justification


def test_score_brechas_with_no_og_tags(scorer: OpportunityScorer):
    """Score para Open Graph faltante — severity 15, effort 25, impact 15 = 55."""
    brechas = [_make_brecha("b1", "no_og_tags", "Sin OG Tags")]
    scores = scorer.score_brechas(brechas)
    assert len(scores) == 1
    s = scores[0]
    assert s.severity_score == 15.0
    assert s.effort_score == 25.0
    assert s.impact_score == 15.0
    assert "Open Graph" in s.justification or "WhatsApp/Facebook" in s.justification


def test_score_brechas_with_low_citability(scorer: OpportunityScorer):
    """Score para citabilidad baja — severity 20, effort 15, impact 25 = 60."""
    brechas = [_make_brecha("b1", "low_citability", "No Citable")]
    scores = scorer.score_brechas(brechas)
    assert len(scores) == 1
    s = scores[0]
    assert s.severity_score == 20.0
    assert s.effort_score == 15.0
    assert s.impact_score == 25.0
    assert "ChatGPT" in s.justification or "IA" in s.justification


def test_score_brechas_with_missing_reviews(scorer: OpportunityScorer):
    """Score para reviews faltantes — severity 25, effort 20, impact 20 = 65."""
    brechas = [_make_brecha("b1", "missing_reviews", "Falta Reviews")]
    scores = scorer.score_brechas(brechas)
    assert len(scores) == 1
    s = scores[0]
    assert s.severity_score == 25.0
    assert s.effort_score == 20.0
    assert s.impact_score == 20.0
    assert "reviews" in s.justification.lower()


def test_all_identify_brechas_types_have_scorer_mapping(scorer: OpportunityScorer):
    """Verifica que TODOS los pain_ids de _identify_brechas() tienen mapping en scorer."""
    # Pain_ids que _identify_brechas() genera (v4_diagnostic_generator.py)
    all_pain_ids = [
        "low_gbp_score",
        "no_hotel_schema",
        "no_whatsapp_visible",
        "poor_performance",
        "whatsapp_conflict",
        "metadata_defaults",
        "missing_reviews",
        "no_faq_schema",
        "no_og_tags",
        "low_citability",
    ]
    # pain_to_type mapper actualizado (sin aliases forzados)
    pain_to_type = {
        "no_faq_schema": "faq_schema_missing",
        "low_gbp_score": "low_gbp_score",
        "whatsapp_conflict": "whatsapp_conflict",
        "metadata_defaults": "cms_defaults",
        "missing_reviews": "missing_reviews",
        "poor_performance": "poor_performance",
        "no_hotel_schema": "no_hotel_schema",
        "no_whatsapp_visible": "no_whatsapp_visible",
        "no_og_tags": "no_og_tags",
        "low_citability": "low_citability",
    }
    for pain_id in all_pain_ids:
        scorer_type = pain_to_type.get(pain_id)
        assert scorer_type is not None, f"pain_id {pain_id} sin mapping en pain_to_type"
        assert scorer_type in scorer.BRECHA_SEVERITY_MAP, (
            f"scorer_type '{scorer_type}' (from {pain_id}) missing in BRECHA_SEVERITY_MAP"
        )
        assert scorer_type in scorer.BRECHA_EFFORT_MAP, (
            f"scorer_type '{scorer_type}' (from {pain_id}) missing in BRECHA_EFFORT_MAP"
        )
        assert scorer_type in scorer.BRECHA_IMPACT_MAP, (
            f"scorer_type '{scorer_type}' (from {pain_id}) missing in BRECHA_IMPACT_MAP"
        )
        assert scorer_type in scorer._JUSTIFICATION_TEMPLATES, (
            f"scorer_type '{scorer_type}' (from {pain_id}) missing in _JUSTIFICATION_TEMPLATES"
        )
