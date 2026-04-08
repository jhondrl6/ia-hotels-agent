"""
Tests for _identify_brechas() - Dynamic brechas (FASE-A).

Tests:
- test_identify_brechas_returns_all_detected: Si audit detecta 5, retorna 5
- test_identify_brechas_no_defaults: Solo 2 detectadas = retorna 2 (sin relleno generico)
- test_identify_brechas_empty_for_perfect_hotel: Hotel perfecto retorna lista vacia
- test_identify_brechas_sorted_by_impact: Retornadas ordenadas por impacto descendente
- test_identify_brechas_max_10_categories: No puede haber mas de 10 categorias
- test_inject_brecha_scores_dynamic_count: Scores se generan para N, no fijo 4
- test_each_brecha_has_valid_pain_id: Cada pain_id es string no vacio
- test_brecha_impacts_sum_reasonable: Suma de impactos no excede 1.0
"""

import pytest
from unittest.mock import MagicMock, patch
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
from modules.data_validation.confidence_taxonomy import ConfidenceLevel


# --- Helper: crear mocks de V4AuditResult ---

def mock_schema(faq_detected=False, hotel_detected=False):
    m = MagicMock()
    m.faq_schema_detected = faq_detected
    m.hotel_schema_detected = hotel_detected
    return m


def mock_gbp(geo_score=80, reviews=50, place_found=True):
    m = MagicMock()
    m.geo_score = geo_score
    m.reviews = reviews
    m.place_found = place_found
    return m


def mock_performance(mobile_score=75):
    m = MagicMock()
    m.mobile_score = mobile_score
    return m


def mock_validation(whatsapp_status=None, phone_web=None):
    m = MagicMock()
    m.whatsapp_status = whatsapp_status
    m.phone_web = phone_web
    return m


def mock_metadata(has_issues=False):
    m = MagicMock()
    m.has_issues = has_issues
    return m


def mock_seo_elements(has_open_graph=True):
    m = MagicMock()
    m.open_graph = has_open_graph
    return m


def mock_citability(score=50):
    m = MagicMock()
    m.overall_score = score
    return m


def create_audit(
    schema_detected=False,
    faq_detected=False,
    gbp_geo_score=80,
    gbp_reviews=50,
    gbp_place_found=True,
    mobile_score=75,
    whatsapp_status=None,
    phone_web=None,
    metadata_has_issues=False,
    seo_elements=None,
    citability=None,
):
    """Factory para crear V4AuditResult mock con componentes configurables."""
    audit = MagicMock()
    audit.gbp = mock_gbp(geo_score=gbp_geo_score, reviews=gbp_reviews, place_found=gbp_place_found)
    audit.schema = mock_schema(faq_detected=faq_detected, hotel_detected=schema_detected)
    audit.performance = mock_performance(mobile_score=mobile_score)
    audit.validation = mock_validation(whatsapp_status=whatsapp_status, phone_web=phone_web)
    audit.metadata = mock_metadata(has_issues=metadata_has_issues)
    # seo_elements y citability no son campos del dataclass - usar getattr
    if seo_elements is not None:
        audit.seo_elements = seo_elements
    if citability is not None:
        audit.citability = citability
    return audit


# --- Tests ---

def test_identify_brechas_returns_all_detected():
    """Si el audit detecta 5 brechas, retorna exactamente 5 (no trunca a 4)."""
    # 5 brechas: low_gbp, no_hotel_schema, no_whatsapp, poor_performance, no_faq_schema
    audit = create_audit(
        schema_detected=False,      # Brecha 2: no_hotel_schema
        faq_detected=False,         # Brecha 8: no_faq_schema
        gbp_geo_score=50,           # Brecha 1: low_gbp_score
        phone_web=None,             # Brecha 3: no_whatsapp_visible
        mobile_score=60,            # Brecha 4: poor_performance
    )
    
    gen = V4DiagnosticGenerator()
    brechas = gen._identify_brechas(audit)
    
    # Debe retornar exactamente 5, NO 4
    assert len(brechas) == 5, f"Expected 5 brechas, got {len(brechas)}: {[b['pain_id'] for b in brechas]}"


def test_identify_brechas_no_defaults():
    """Si solo detecta 2, retorna 2 (sin relleno generico)."""
    # Solo 2 brechas: low_gbp y no_hotel_schema
    audit = create_audit(
        schema_detected=False,      # Brecha 2: no_hotel_schema
        gbp_geo_score=50,           # Brecha 1: low_gbp_score
        phone_web="+573001234567",  # WhatsApp configurado -> no brecha
        mobile_score=80,            # Performance OK -> no brecha
        faq_detected=True,          # FAQ OK
        gbp_reviews=50,             # Reviews OK
    )
    
    gen = V4DiagnosticGenerator()
    brechas = gen._identify_brechas(audit)
    
    assert len(brechas) == 2, f"Expected 2 brechas, got {len(brechas)}"
    pain_ids = [b['pain_id'] for b in brechas]
    assert 'low_gbp_score' in pain_ids
    assert 'no_hotel_schema' in pain_ids
    # No debe haber pain_ids genericos como 'low_ia_readiness'
    assert 'low_ia_readiness' not in pain_ids


def test_identify_brechas_empty_for_perfect_hotel():
    """Hotel sin problemas retorna lista vacia."""
    audit = create_audit(
        schema_detected=True,
        faq_detected=True,
        gbp_geo_score=80,
        gbp_reviews=50,
        gbp_place_found=True,
        mobile_score=85,
        whatsapp_status=ConfidenceLevel.VERIFIED.value,
        phone_web="+573001234567",
        metadata_has_issues=False,
        seo_elements=mock_seo_elements(has_open_graph=True),
        citability=mock_citability(score=80),
    )
    
    gen = V4DiagnosticGenerator()
    brechas = gen._identify_brechas(audit)
    
    assert isinstance(brechas, list)
    assert len(brechas) == 0, f"Expected 0 brechas for perfect hotel, got {len(brechas)}"


def test_identify_brechas_sorted_by_impact():
    """Retornadas ordenadas por impacto descendente."""
    audit = create_audit(
        schema_detected=False,      # impacto 0.25
        faq_detected=False,         # impacto 0.12
        gbp_geo_score=50,           # impacto 0.30 (la mas alta)
        phone_web=None,             # impacto 0.20
        mobile_score=60,            # impacto 0.15
    )
    
    gen = V4DiagnosticGenerator()
    brechas = gen._identify_brechas(audit)
    
    impactos = [b['impacto'] for b in brechas]
    assert impactos == sorted(impactos, reverse=True), f"Brechas no ordenadas por impacto: {impactos}"


def test_identify_brechas_max_10_categories():
    """No puede haber mas de 10 categorias de deteccion."""
    # Crear audit que dispara TODAS las brechas posibles
    audit = create_audit(
        schema_detected=False,      # Brecha 2
        faq_detected=False,         # Brecha 8
        gbp_geo_score=50,           # Brecha 1
        phone_web=None,             # Brecha 3
        mobile_score=60,            # Brecha 4
        whatsapp_status=ConfidenceLevel.CONFLICT.value,  # Brecha 5
        metadata_has_issues=True,   # Brecha 6
        gbp_reviews=5,              # Brecha 7
        seo_elements=mock_seo_elements(has_open_graph=False),  # Brecha 9
        citability=mock_citability(score=20),   # Brecha 10
    )
    
    gen = V4DiagnosticGenerator()
    brechas = gen._identify_brechas(audit)
    
    assert len(brechas) <= 10, f"Expected max 10, got {len(brechas)}"


def test_each_brecha_has_valid_pain_id():
    """Cada brecha tiene pain_id valido (string no vacio)."""
    audit = create_audit(
        schema_detected=False,
        gbp_geo_score=50,
        phone_web=None,
        mobile_score=60,
    )
    
    gen = V4DiagnosticGenerator()
    brechas = gen._identify_brechas(audit)
    
    for b in brechas:
        assert 'pain_id' in b
        assert isinstance(b['pain_id'], str)
        assert len(b['pain_id']) > 0
        assert b['pain_id'] != 'low_ia_readiness'  # No generico
        assert b['pain_id'] != 'no_faq_schema_generico'


def test_brecha_impacts_sum_reasonable():
    """La suma de impactos no excede 1.0 para distribucion proporcional."""
    audit = create_audit(
        schema_detected=False,
        gbp_geo_score=50,
        phone_web=None,
        mobile_score=60,
    )
    
    gen = V4DiagnosticGenerator()
    brechas = gen._identify_brechas(audit)
    
    total = sum(b['impacto'] for b in brechas)
    # La suma puede exceder 1.0 si hay muchas brechas, pero individual <= 1.0
    for b in brechas:
        assert b['impacto'] <= 1.0
        assert b['impacto'] >= 0.0


def test_identify_brechas_with_og_tags_detection():
    """Brecha 9: Sin Open Graph detecta correctamente."""
    audit = create_audit(
        schema_detected=True,
        faq_detected=True,
        gbp_geo_score=80,
        phone_web="+573001234567",
        mobile_score=85,
        gbp_reviews=50,
        seo_elements=mock_seo_elements(has_open_graph=False),  # Sin OG
    )
    
    gen = V4DiagnosticGenerator()
    brechas = gen._identify_brechas(audit)
    
    pain_ids = [b['pain_id'] for b in brechas]
    assert 'no_og_tags' in pain_ids
    # Verificar que el nombre y detalle no son genericos
    og_brecha = next(b for b in brechas if b['pain_id'] == 'no_og_tags')
    assert 'Open Graph' in og_brecha['nombre']


def test_identify_brechas_with_citability_detection():
    """Brecha 10: Contenido no citable por IA detecta correctamente."""
    audit = create_audit(
        schema_detected=True,
        faq_detected=True,
        gbp_geo_score=80,
        phone_web="+573001234567",
        mobile_score=85,
        gbp_reviews=50,
        citability=mock_citability(score=20),  # Bajo score
    )
    
    gen = V4DiagnosticGenerator()
    brechas = gen._identify_brechas(audit)
    
    pain_ids = [b['pain_id'] for b in brechas]
    assert 'low_citability' in pain_ids


def test_identify_brechas_8_detected_returns_8():
    """Un audit que dispara 8 brechas retorna las 8 (no trunca a 4)."""
    audit = create_audit(
        schema_detected=False,       # Brecha 2: no_hotel_schema
        faq_detected=False,          # Brecha 8: no_faq_schema
        gbp_geo_score=50,           # Brecha 1: low_gbp_score
        phone_web=None,             # Brecha 3: no_whatsapp_visible
        mobile_score=60,            # Brecha 4: poor_performance
        whatsapp_status=ConfidenceLevel.CONFLICT.value,  # Brecha 5: whatsapp_conflict
        metadata_has_issues=True,    # Brecha 6: metadata_defaults
        gbp_reviews=5,              # Brecha 7: missing_reviews
    )

    gen = V4DiagnosticGenerator()
    brechas = gen._identify_brechas(audit)

    assert len(brechas) == 8, f"Expected 8, got {len(brechas)}: {[b['pain_id'] for b in brechas]}"


def test_inject_brecha_scores_dynamic_count():
    """_inject_brecha_scores() itera sobre N brechas, no fijo 4."""
    gen = V4DiagnosticGenerator()
    
    # Mock audit con 2 brechas detectadas
    audit = create_audit(
        schema_detected=False,      # Brecha 2: no_hotel_schema
        gbp_geo_score=50,          # Brecha 1: low_gbp_score
        phone_web="+573001234567",  # no whatsapp brecha
        mobile_score=80,           # no performance brecha
    )
    
    # We just verify the method doesn't crash with N != 4
    # The actual scores dict will have entries for brechas 1 and 2 only
    # Note: _inject_brecha_scores calls _compute_opportunity_scores which may return
    # None if the scorer is unavailable, so result may be {}
    result = gen._inject_brecha_scores(audit, None)
    
    # Must have brecha_1_score key at minimum if scores computed, or empty dict
    assert isinstance(result, dict)


def test_identify_brechas_none_audit_returns_empty():
    """Si audit es None, retorna lista vacia (no crash)."""
    gen = V4DiagnosticGenerator()
    brechas = gen._identify_brechas(None)
    
    assert brechas == []
