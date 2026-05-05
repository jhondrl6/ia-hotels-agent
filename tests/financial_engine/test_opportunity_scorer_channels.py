"""Tests para OpportunityScorer + Channel Weights (CHAN-2).

8 tests obligatorios del plan CHAN-2:
1.  test_scorer_without_channel_context_unchanged
2.  test_whatsapp_breaches_weighted_when_whatsapp_dominant
3.  test_gbp_breaches_weighted_when_gbp_dominant
4.  test_base_total_score_preserved
5.  test_channel_multiplier_stored
6.  test_neutral_weights_no_change
7.  test_channel_reason_populated
8.  test_backwards_compatible_existing_tests
"""

import pytest
import sys
import os

_PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from modules.financial_engine.opportunity_scorer import (
    OpportunityScore,
    OpportunityScorer,
)


@pytest.fixture()
def scorer() -> OpportunityScorer:
    return OpportunityScorer()


def _make_brecha(_id: str, _type: str, _name: str = "") -> dict:
    return {"id": _id, "type": _type, "name": _name or _id}


# ------------------------------------------------------------------
# Test 1: Sin channel_context -> comportamiento original
# ------------------------------------------------------------------
def test_scorer_without_channel_context_unchanged(scorer):
    """Sin channel_context, el scorer retorna el mismo output que antes.
    
    Los campos de canal tienen valores neutros (multiplier=1.0, reason='')
    y base_total_score == total_score original."""
    brechas = [
        _make_brecha("whatsapp_conflict", "whatsapp_conflict"),
        _make_brecha("faq_schema_missing", "faq_schema_missing"),
    ]
    scores = scorer.score_brechas(brechas)

    assert len(scores) == 2
    for s in scores:
        # Campos de canal tienen valores neutrales
        assert s.channel_multiplier == 1.0
        assert s.channel_reason == ""
        # base_total_score == total_score original (preserve)
        assert s.base_total_score == s.total_score
        # adjusted_total_score == base_total_score * 1.0 == total_score
        assert s.adjusted_total_score == s.total_score


# ------------------------------------------------------------------
# Test 2: WhatsApp dominante -> brechas WhatsApp suben
# ------------------------------------------------------------------
def test_whatsapp_breaches_weighted_when_whatsapp_dominant(scorer):
    """Cuando WhatsApp es el canal dominante, las brechas WhatsApp reciben
    multiplicador > 1.0 (ej: 1.5x) y suben su adjusted_total_score."""
    channel_context = {
        "dominant_channel": "whatsapp",
        "confidence": "medium",
        "channel_weights": {
            "whatsapp": 1.5,
            "gbp_local": 1.0,
            "iao_schema": 1.0,
            "direct_conversion": 1.0,
            "seo_content": 1.0,
            "performance_mobile": 1.0,
        },
    }
    brechas = [
        _make_brecha("whatsapp_conflict", "whatsapp_conflict"),
        _make_brecha("faq_schema_missing", "faq_schema"),
    ]
    scores = scorer.score_brechas(brechas, channel_context=channel_context)

    whatsapp_score = next(s for s in scores if s.brecha_id == "whatsapp_conflict")
    faq_score = next(s for s in scores if s.brecha_id == "faq_schema_missing")

    # whatsapp_conflict -> canal whatsapp -> multiplier 1.5
    assert whatsapp_score.channel_multiplier == 1.5
    assert whatsapp_score.base_total_score > 0
    assert whatsapp_score.adjusted_total_score == pytest.approx(
        whatsapp_score.base_total_score * 1.5
    )

    # faq_schema_missing -> canal iao_schema -> multiplier 1.0
    assert faq_score.channel_multiplier == 1.0
    assert faq_score.adjusted_total_score == faq_score.base_total_score


# ------------------------------------------------------------------
# Test 3: GBP dominante -> brechas GBP suben
# ------------------------------------------------------------------
def test_gbp_breaches_weighted_when_gbp_dominant(scorer):
    """Cuando GBP es el canal dominante, las brechas GBP reciben
    multiplicador > 1.0."""
    channel_context = {
        "dominant_channel": "gbp_local",
        "confidence": "high",
        "channel_weights": {
            "whatsapp": 1.0,
            "gbp_local": 1.8,
            "iao_schema": 1.0,
            "direct_conversion": 1.0,
            "seo_content": 1.0,
            "performance_mobile": 1.0,
        },
    }
    brechas = [
        _make_brecha("low_gbp_score", "low_gbp_score"),
        _make_brecha("gbp_incomplete", "gbp_incomplete"),
        _make_brecha("whatsapp_conflict", "whatsapp_conflict"),
    ]
    scores = scorer.score_brechas(brechas, channel_context=channel_context)

    gbp_brechas = [s for s in scores if s.brecha_id in ("low_gbp_score", "gbp_incomplete")]
    whatsapp = next(s for s in scores if s.brecha_id == "whatsapp_conflict")

    for s in gbp_brechas:
        assert s.channel_multiplier == 1.8
        assert s.adjusted_total_score == pytest.approx(s.base_total_score * 1.8)

    assert whatsapp.channel_multiplier == 1.0


# ------------------------------------------------------------------
# Test 4: base_total_score preserva el total_score original
# ------------------------------------------------------------------
def test_base_total_score_preserved(scorer):
    """base_total_score debe ser igual al total_score original
    (antes de aplicar multiplicador de canal)."""
    channel_context = {
        "dominant_channel": "whatsapp",
        "confidence": "high",
        "channel_weights": {
            "whatsapp": 2.0,
            "gbp_local": 1.0,
            "iao_schema": 1.0,
            "direct_conversion": 1.0,
            "seo_content": 1.0,
            "performance_mobile": 1.0,
        },
    }
    brechas = [
        _make_brecha("whatsapp_conflict", "whatsapp_conflict"),
        _make_brecha("no_whatsapp_visible", "no_whatsapp_visible"),
    ]
    scores = scorer.score_brechas(brechas, channel_context=channel_context)

    for s in scores:
        assert s.base_total_score == s.total_score
        assert s.total_score > 0


# ------------------------------------------------------------------
# Test 5: channel_multiplier almacenado en OpportunityScore
# ------------------------------------------------------------------
def test_channel_multiplier_stored(scorer):
    """El channel_multiplier se almacena correctamente en el OpportunityScore."""
    channel_context = {
        "dominant_channel": "booking_engine",
        "confidence": "high",
        "channel_weights": {
            "whatsapp": 0.8,
            "gbp_local": 0.9,
            "iao_schema": 1.2,
            "direct_conversion": 1.5,
            "seo_content": 1.0,
            "performance_mobile": 1.0,
        },
    }
    brechas = [
        _make_brecha("data_inconsistent", "data_inconsistent"),
        _make_brecha("missing_reviews", "missing_reviews"),
    ]
    scores = scorer.score_brechas(brechas, channel_context=channel_context)

    # data_inconsistent -> direct_conversion -> 1.5
    data_score = next(s for s in scores if s.brecha_id == "data_inconsistent")
    assert data_score.channel_multiplier == 1.5

    # missing_reviews -> direct_conversion -> 1.5
    reviews_score = next(s for s in scores if s.brecha_id == "missing_reviews")
    assert reviews_score.channel_multiplier == 1.5


# ------------------------------------------------------------------
# Test 6: Pesos neutrales (1.0) -> sin cambio en adjusted_total_score
# ------------------------------------------------------------------
def test_neutral_weights_no_change(scorer):
    """Con channel_weights todos en 1.0, adjusted_total_score == base_total_score."""
    channel_context = {
        "dominant_channel": "unknown",
        "confidence": "low",
        "channel_weights": {
            "whatsapp": 1.0,
            "gbp_local": 1.0,
            "iao_schema": 1.0,
            "direct_conversion": 1.0,
            "seo_content": 1.0,
            "performance_mobile": 1.0,
        },
    }
    brechas = [
        _make_brecha("whatsapp_conflict", "whatsapp_conflict"),
        _make_brecha("low_gbp_score", "low_gbp_score"),
        _make_brecha("no_hotel_schema", "no_hotel_schema"),
    ]
    scores = scorer.score_brechas(brechas, channel_context=channel_context)

    for s in scores:
        assert s.channel_multiplier == 1.0
        assert s.adjusted_total_score == s.base_total_score


# ------------------------------------------------------------------
# Test 7: channel_reason se llena con string no vacío
# ------------------------------------------------------------------
def test_channel_reason_populated(scorer):
    """Cuando hay channel_context, channel_reason es un string no vacío
    que describe el ajuste aplicado."""
    channel_context = {
        "dominant_channel": "whatsapp",
        "confidence": "high",
        "channel_weights": {
            "whatsapp": 1.5,
            "gbp_local": 1.0,
            "iao_schema": 1.0,
            "direct_conversion": 1.0,
            "seo_content": 1.0,
            "performance_mobile": 1.0,
        },
    }
    brechas = [
        _make_brecha("whatsapp_conflict", "whatsapp_conflict"),
    ]
    scores = scorer.score_brechas(brechas, channel_context=channel_context)

    assert len(scores) == 1
    assert scores[0].channel_reason != ""
    assert "whatsapp" in scores[0].channel_reason.lower()
    assert "1.5" in scores[0].channel_reason


# ------------------------------------------------------------------
# Test 8: Backwards compatibility con tests existentes
# ------------------------------------------------------------------
def test_backwards_compatible_existing_tests(scorer):
    """Los tests existentes de opportunity_scorer que NO usan channel_context
    siguen funcionando sin regresión."""
    brechas = [
        _make_brecha("whatsapp_conflict", "whatsapp_conflict"),
        _make_brecha("faq_schema_missing", "faq_schema_missing"),
        _make_brecha("low_gbp_score", "low_gbp_score"),
    ]

    # Sin channel_context (None por defecto)
    scores_none = scorer.score_brechas(brechas, channel_context=None)
    assert len(scores_none) == 3

    # Sin channel_context (dict vacío)
    scores_empty = scorer.score_brechas(brechas, channel_context={})
    assert len(scores_empty) == 3

    # Verificar que ambos retornan scores normales
    for s in scores_none:
        assert s.total_score > 0
        assert s.rank > 0
        assert s.justification != ""
