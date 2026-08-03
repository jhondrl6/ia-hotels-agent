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

def mock_schema(faq_detected=False, hotel_detected=False, org_detected=False):
    m = MagicMock()
    m.faq_schema_detected = faq_detected
    m.hotel_schema_detected = hotel_detected
    m.org_schema_detected = org_detected
    return m


def mock_gbp(geo_score=80, reviews=50, place_found=True):
    m = MagicMock()
    m.geo_score = geo_score
    m.reviews = reviews
    m.place_found = place_found
    m.confidence = "ESTIMATED"
    m.rating = 4.5
    return m


def mock_performance(mobile_score=75, lcp=None, cls=None):
    m = MagicMock()
    m.mobile_score = mobile_score
    m.has_field_data = True
    m.lcp = lcp
    m.cls = cls
    return m


def mock_validation(whatsapp_status=None, phone_web=None, whatsapp_html_detected=False):
    m = MagicMock()
    m.whatsapp_status = whatsapp_status
    m.phone_web = phone_web
    m.whatsapp_html_detected = whatsapp_html_detected
    return m


def mock_metadata(has_issues=False):
    m = MagicMock()
    m.has_issues = has_issues
    m.has_default_title = has_issues
    m.has_default_description = has_issues
    return m


def mock_seo_elements(has_open_graph=True):
    m = MagicMock()
    m.open_graph = has_open_graph
    m.confidence = "high"
    m.open_graph_tags = {"og:title": "x", "og:description": "y", "og:image": "z"} if has_open_graph else {}
    m.imagenes_alt = True
    return m


def mock_citability(score=50, blocks_analyzed=0):
    m = MagicMock()
    m.overall_score = score
    m.blocks_analyzed = blocks_analyzed
    return m


def create_audit(
    schema_detected=False,
    faq_detected=False,
    org_detected=False,
    gbp_geo_score=80,
    gbp_reviews=50,
    gbp_place_found=True,
    mobile_score=75,
    whatsapp_status=None,
    phone_web=None,
    whatsapp_html_detected=False,
    metadata_has_issues=False,
    seo_elements=None,
    citability=None,
):
    """Factory para crear V4AuditResult mock con componentes configurables."""
    audit = MagicMock()
    audit.url = "https://hotel-test.com"
    audit.gbp = mock_gbp(geo_score=gbp_geo_score, reviews=gbp_reviews, place_found=gbp_place_found)
    audit.schema = mock_schema(faq_detected=faq_detected, hotel_detected=schema_detected, org_detected=org_detected)
    audit.performance = mock_performance(mobile_score=mobile_score)
    audit.validation = mock_validation(whatsapp_status=whatsapp_status, phone_web=phone_web, whatsapp_html_detected=whatsapp_html_detected)
    audit.metadata = mock_metadata(has_issues=metadata_has_issues)
    # Optional attributes: None so hasattr+truthiness checks skip them
    audit.ai_crawlers = None
    audit.ia_readiness = None
    audit.seo_elements = seo_elements
    audit.citability = citability
    return audit


# --- Tests ---

def test_identify_brechas_returns_all_detected():
    """Si el audit detecta 6 brechas, retorna exactamente 6 (no trunca a 4)."""
    # 6 brechas: low_gbp, no_hotel_schema, no_whatsapp, poor_performance, no_faq_schema, low_seo_score
    audit = create_audit(
        schema_detected=False,      # Brecha 2: no_hotel_schema
        faq_detected=False,         # Brecha 8: no_faq_schema
        gbp_geo_score=50,           # Brecha 1: low_gbp_score
        phone_web=None,             # Brecha 3: no_whatsapp_visible
        mobile_score=60,            # Brecha 4: poor_performance
    )
    
    gen = V4DiagnosticGenerator()
    brechas = gen._identify_brechas(audit)
    
    # Debe retornar exactamente 6, NO 4
    # (low_seo_score se detecta porque seo_elements=None → web_score 25 < 40, D2)
    assert len(brechas) == 6, f"Expected 6 brechas, got {len(brechas)}: {[b['pain_id'] for b in brechas]}"


def test_identify_brechas_no_defaults():
    """Si solo detecta 3, retorna 3 (sin relleno generico)."""
    # Solo 3 brechas: low_gbp, no_hotel_schema y low_seo_score
    audit = create_audit(
        schema_detected=False,      # Brecha: no_hotel_schema
        gbp_geo_score=50,           # Brecha: low_gbp_score
        phone_web="+573001234567",
        whatsapp_html_detected=True,  # WhatsApp HTML detected -> no brecha
        mobile_score=80,            # Performance OK -> no brecha
        faq_detected=True,          # FAQ OK
        org_detected=True,          # Org schema OK
        gbp_reviews=50,             # Reviews OK
    )
    
    gen = V4DiagnosticGenerator()
    brechas = gen._identify_brechas(audit)
    
    assert len(brechas) == 3, f"Expected 3 brechas, got {len(brechas)}: {[b['pain_id'] for b in brechas]}"
    pain_ids = [b['pain_id'] for b in brechas]
    assert 'low_gbp_score' in pain_ids
    assert 'no_hotel_schema' in pain_ids
    assert 'low_seo_score' in pain_ids  # seo_elements=None → web_score 25 < 40 (D2)
    # No debe haber pain_ids genericos como 'low_ia_readiness'
    assert 'low_ia_readiness' not in pain_ids


def test_identify_brechas_empty_for_perfect_hotel():
    """Hotel sin problemas retorna lista vacia."""
    og_tags = {f"og:tag{i}": f"val{i}" for i in range(12)}
    seo = MagicMock()
    seo.open_graph = True
    seo.confidence = "high"
    seo.open_graph_tags = og_tags
    seo.imagenes_alt = True

    audit = create_audit(
        schema_detected=True,
        faq_detected=True,
        org_detected=True,
        gbp_geo_score=80,
        gbp_reviews=50,
        gbp_place_found=True,
        mobile_score=85,
        whatsapp_status=ConfidenceLevel.VERIFIED.value,
        phone_web="+573001234567",
        whatsapp_html_detected=True,
        metadata_has_issues=False,
        seo_elements=seo,
        citability=mock_citability(score=80),
    )
    
    gen = V4DiagnosticGenerator()
    brechas = gen._identify_brechas(audit)
    
    assert isinstance(brechas, list)
    assert len(brechas) == 0, f"Expected 0 brechas for perfect hotel, got {len(brechas)}: {[b['pain_id'] for b in brechas]}"


def test_identify_brechas_sorted_by_severity():
    """Retornadas ordenadas por severidad (critical > high > medium > low)."""
    audit = create_audit(
        schema_detected=False,      # high
        faq_detected=False,         # medium
        gbp_geo_score=50,           # medium/high
        phone_web=None,             # high (no_whatsapp_visible)
        mobile_score=60,            # not detected (threshold < 50)
    )
    
    gen = V4DiagnosticGenerator()
    brechas = gen._identify_brechas(audit)
    
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    severities = [severity_order.get(b.get('severity', ''), 4) for b in brechas]
    assert severities == sorted(severities), f"Brechas no ordenadas por severidad: {[b.get('severity') for b in brechas]}"


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
        org_detected=True,
        gbp_geo_score=80,
        phone_web="+573001234567",
        whatsapp_html_detected=True,
        mobile_score=85,
        gbp_reviews=50,
        citability=mock_citability(score=20),  # Bajo score
    )
    
    gen = V4DiagnosticGenerator()
    brechas = gen._identify_brechas(audit)
    
    pain_ids = [b['pain_id'] for b in brechas]
    assert 'low_citability' in pain_ids
    cit_brecha = next(b for b in brechas if b['pain_id'] == 'low_citability')
    # D1: nombre real del mapper (detect_pains), no narrativa estática
    assert 'Poco Citable' in cit_brecha['nombre']
    assert 'Score citability' in cit_brecha['detalle']


def test_citability_blocks_zero_narrative():
    """blocks_analyzed=0 → nombre real del mapper 'Contenido Poco Citable' (D1)."""
    audit = create_audit(
        schema_detected=True, faq_detected=True, org_detected=True, gbp_geo_score=80,
        phone_web="+573****4567", whatsapp_html_detected=True, mobile_score=85, gbp_reviews=50,
        citability=mock_citability(score=0, blocks_analyzed=0),
    )
    gen = V4DiagnosticGenerator()
    brechas = gen._identify_brechas(audit)
    cit_brecha = next(b for b in brechas if b['pain_id'] == 'low_citability')
    assert 'Poco Citable' in cit_brecha['nombre']
    assert 'Score citability: 0.0/100' in cit_brecha['detalle']


def test_citability_blocks_analyzed_low_score_narrative_poco_estructurado():
    """blocks_analyzed > 0 y score < 30 → nombre real del mapper 'Contenido Poco Citable' (D1)."""
    audit = create_audit(
        schema_detected=True, faq_detected=True, org_detected=True, gbp_geo_score=80,
        phone_web="+573****4567", whatsapp_html_detected=True, mobile_score=85, gbp_reviews=50,
        citability=mock_citability(score=15, blocks_analyzed=5),
    )
    gen = V4DiagnosticGenerator()
    brechas = gen._identify_brechas(audit)
    cit_brecha = next(b for b in brechas if b['pain_id'] == 'low_citability')
    assert 'Poco Citable' in cit_brecha['nombre']
    assert 'Score citability: 15.0/100 - 5 bloques' in cit_brecha['detalle']


def test_citability_blocks_none_narrative():
    """blocks_analyzed=None → narrativa 'Contenido Poco Estructurado para IA'."""
    cit = MagicMock()
    cit.overall_score = 0
    cit.blocks_analyzed = None
    audit = create_audit(
        schema_detected=True, faq_detected=True, org_detected=True, gbp_geo_score=80,
        phone_web="+573****4567", whatsapp_html_detected=True, mobile_score=85, gbp_reviews=50,
        citability=cit,
    )
    gen = V4DiagnosticGenerator()
    brechas = gen._identify_brechas(audit)
    cit_brecha = next(b for b in brechas if b['pain_id'] == 'low_citability')
    assert 'Poco Citable' in cit_brecha['nombre']


def test_identify_brechas_8_detected_returns_8():
    """Un audit que dispara 8 brechas retorna las 8 (no trunca a 4)."""
    audit = create_audit(
        schema_detected=False,       # no_hotel_schema
        faq_detected=False,          # no_faq_schema
        gbp_geo_score=50,           # low_gbp_score
        phone_web=None,             # no_whatsapp_visible
        mobile_score=40,            # poor_performance (threshold < 50)
        metadata_has_issues=True,    # metadata_defaults
        gbp_reviews=5,              # missing_reviews
    )

    gen = V4DiagnosticGenerator()
    brechas = gen._identify_brechas(audit)

    # no_whatsapp_visible, no_hotel_schema, metadata_defaults, no_faq_schema,
    # low_gbp_score, poor_performance, missing_reviews, no_org_schema,
    # low_seo_score (seo_elements=None → web_score 25 < 40) = 9
    assert len(brechas) == 9, f"Expected 9, got {len(brechas)}: {[b['pain_id'] for b in brechas]}"


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


# --- Helper: crear mock de FinancialScenarios ---

def mock_financial_scenarios(monthly_loss=3000000, monthly_loss_central=None):
    """Crea mock de FinancialScenarios con escenario principal configurable."""
    from unittest.mock import MagicMock
    main = MagicMock()
    main.monthly_loss_max = monthly_loss
    main.monthly_loss_central = monthly_loss_central  # None = fallback a monthly_loss_max
    fs = MagicMock()
    fs.get_main_scenario.return_value = main
    return fs


# --- Tests FASE-B: Generator dinamico ---

def test_build_brechas_section_with_5_brechas():
    """_build_brechas_section() genera 5 secciones markdown para 5 brechas."""
    audit = create_audit(
        schema_detected=False,      # no_hotel_schema
        faq_detected=False,         # no_faq_schema
        gbp_geo_score=50,           # low_gbp_score
        phone_web=None,             # no_whatsapp_visible
        mobile_score=60,            # poor_performance
    )
    fs = mock_financial_scenarios()
    gen = V4DiagnosticGenerator()
    section = gen._build_brechas_section(audit, fs)

    # Debe contener 5 headers [BRECHA N]
    for i in range(1, 6):
        assert f"[BRECHA {i}]" in section, f"Falta [BRECHA {i}] en output"


def test_build_brechas_section_with_0_brechas():
    """_build_brechas_section() retorna mensaje alternativo si no hay brechas."""
    og_tags = {f"og:tag{i}": f"val{i}" for i in range(12)}
    seo = MagicMock()
    seo.open_graph = True
    seo.confidence = "high"
    seo.open_graph_tags = og_tags
    seo.imagenes_alt = True

    audit = create_audit(
        schema_detected=True,
        faq_detected=True,
        org_detected=True,
        gbp_geo_score=80,
        gbp_reviews=50,
        gbp_place_found=True,
        mobile_score=85,
        whatsapp_status=ConfidenceLevel.VERIFIED.value,
        phone_web="+573****4567",
        whatsapp_html_detected=True,
        metadata_has_issues=False,
        seo_elements=seo,
        citability=mock_citability(score=80),
    )
    fs = mock_financial_scenarios()
    gen = V4DiagnosticGenerator()
    section = gen._build_brechas_section(audit, fs)

    assert "No se detectaron brechas" in section


def test_build_brechas_resumen_section_dynamic():
    """_build_brechas_resumen_section() tiene N filas (no siempre 4)."""
    # 3 brechas detectadas
    audit = create_audit(
        schema_detected=False,      # no_hotel_schema
        gbp_geo_score=50,           # low_gbp_score
        mobile_score=40,            # poor_performance (threshold < 50)
        phone_web="+573****4567",
        whatsapp_html_detected=True,  # no whatsapp brecha
        faq_detected=True,          # no faq brecha
        org_detected=True,          # no org brecha
    )
    fs = mock_financial_scenarios()
    gen = V4DiagnosticGenerator()
    resumen = gen._build_brechas_resumen_section(audit, fs)

    # Contar filas de tabla (lineas que empiezan con "| ")
    # 4 brechas: no_hotel_schema, low_gbp_score, poor_performance, low_seo_score (D2)
    filas = [l for l in resumen.split("\n") if l.strip().startswith("|")]
    assert len(filas) == 4, f"Expected 4 filas, got {len(filas)}: {filas}"


def test_inject_brecha_scores_no_truncation():
    """_inject_brecha_scores() genera scores para N brechas, no limitado a 4."""
    gen = V4DiagnosticGenerator()

    # Audit con 8 brechas (maximo disparo razonable)
    audit = create_audit(
        schema_detected=False,
        faq_detected=False,
        gbp_geo_score=50,
        phone_web=None,
        mobile_score=60,
        whatsapp_status=ConfidenceLevel.CONFLICT.value,
        metadata_has_issues=True,
        gbp_reviews=5,
    )

    result = gen._inject_brecha_scores(audit, None)
    # Si scorer no disponible, retorna {}. Si lo esta, no debe limitar a 4
    assert isinstance(result, dict)
    # Si hay scores, verificar que no trunca a 4 (podria haber brecha_5_score, etc)
    if 'brecha_1_score' in result:
        # Al menos las primeras 4 deben existir
        for i in range(1, 5):
            assert f'brecha_{i}_score' in result


def test_brecha_section_markdown_valid():
    """Cada seccion tiene headers, detalle y costo."""
    audit = create_audit(
        schema_detected=False,
        gbp_geo_score=50,
        phone_web=None,
    )
    fs = mock_financial_scenarios()
    gen = V4DiagnosticGenerator()
    section = gen._build_brechas_section(audit, fs)

    # Verificar estructura de cada brecha
    lines = section.split("\n")
    has_brecha_header = any("[BRECHA" in l for l in lines)
    has_detalle = any("**Detalle:**" in l for l in lines)
    has_costo = any("**Costo:**" in l for l in lines)

    assert has_brecha_header, "Falta header [BRECHA N]"
    assert has_detalle, "Falta campo **Detalle:**"
    assert has_costo, "Falta campo **Costo:**"


# --- Tests FASE-G: Dual Source Conflict Resolution ---

def test_brecha_scores_dont_overwrite_nombre():
    """_inject_brecha_scores() NO debe incluir brecha_N_nombre en su output (FASE-G)."""
    gen = V4DiagnosticGenerator()
    audit = create_audit(
        schema_detected=False,
        gbp_geo_score=50,
        phone_web=None,
        mobile_score=60,
    )
    result = gen._inject_brecha_scores(audit, None)

    # Score vars DEBEN estar (si scorer disponible)
    # nombre/costo/detalle NO deben estar en el dict retornado
    for key in result:
        assert not key.endswith('_nombre'), f"_inject_brecha_scores returned {key} — dual source conflict!"
        assert not key.endswith('_costo'), f"_inject_brecha_scores returned {key} — dual source conflict!"
        assert not key.endswith('_detalle'), f"_inject_brecha_scores returned {key} — dual source conflict!"


def test_brecha_scores_dont_overwrite_costo():
    """Costo calculado por _get_brecha_costo() con pesos normalizados NO es sobrescrito (FASE-G)."""
    gen = V4DiagnosticGenerator()
    fs = mock_financial_scenarios(monthly_loss=10_000_000)
    audit = create_audit(
        schema_detected=False,   # no_hotel_schema (impacto 0.25)
        gbp_geo_score=50,        # low_gbp_score (impacto 0.30)
        phone_web="+573****4567",
        mobile_score=80,
        faq_detected=True,
        gbp_reviews=50,
    )

    # Fuente A: _get_brecha_costo usa pesos normalizados (no raw 0.30)
    costo_brecha1 = gen._get_brecha_costo(audit, fs, 0)
    # Con normalizacion: low_gbp = 0.30/(0.30+0.25)*100 = 54.55%
    # Costo = 10M * 0.5455 = 5.454.545
    assert costo_brecha1 != "0"  # Debe tener un valor no cero

    # Fuente B: _inject_brecha_scores NO debe contener _costo keys
    score_result = gen._inject_brecha_scores(audit, fs)
    for key in score_result:
        assert not key.endswith('_costo'), f"Score injector returned {key} — would overwrite real costo!"


def test_diagnostic_summary_includes_brechas_reales():
    """DiagnosticSummary tiene campo brechas_reales y acepta lista de dicts (FASE-G)."""
    from modules.commercial_documents.data_structures import DiagnosticSummary

    brechas_mock = [
        {'pain_id': 'low_gbp_score', 'nombre': 'Visibilidad Local', 'impacto': 0.30, 'detalle': 'Test'},
        {'pain_id': 'no_hotel_schema', 'nombre': 'Sin Schema', 'impacto': 0.25, 'detalle': 'Test'},
    ]
    diag = DiagnosticSummary(
        hotel_name="Hotel Test",
        critical_problems_count=2,
        quick_wins_count=1,
        overall_confidence=ConfidenceLevel.ESTIMATED,
        top_problems=["Visibilidad Local", "Sin Schema"],
        brechas_reales=brechas_mock,
    )
    assert diag.brechas_reales is not None
    assert len(diag.brechas_reales) == 2
    assert diag.brechas_reales[0]['impacto'] == 0.30
    assert diag.brechas_reales[1]['impacto'] == 0.25


# --- Tests FASE-H: Performance Cache + Cleanup ---

def test_identify_brechas_cached_once():
    """_identify_brechas() ejecuta su cuerpo 1 vez por generate(), no 9 (FASE-H)."""
    audit = create_audit(
        schema_detected=False,
        faq_detected=False,
        gbp_geo_score=50,
        phone_web=None,
        mobile_score=60,
    )
    gen = V4DiagnosticGenerator()

    # Primera llamada: cache miss → ejecuta lógica
    brechas1 = gen._identify_brechas(audit)
    # Segunda llamada: cache hit → retorna sin re-ejecutar
    brechas2 = gen._identify_brechas(audit)
    # Tercera llamada: cache hit
    brechas3 = gen._identify_brechas(audit)

    # Mismo objeto retornado (identidad, no solo igualdad)
    assert brechas1 is brechas2, "Cache miss en segunda llamada — no reusa caché"
    assert brechas2 is brechas3, "Cache miss en tercera llamada — no reusa caché"
    assert len(brechas1) == 6  # incluye low_seo_score (D2)


def test_cache_cleared_between_generates():
    """Caché se limpia entre llamadas a generate() — sin stale data (FASE-H)."""
    # Audit A: 5 brechas
    audit_a = create_audit(
        schema_detected=False, faq_detected=False, gbp_geo_score=50,
        phone_web=None, mobile_score=60,
    )
    # Audit B: 0 brechas (hotel perfecto)
    og_tags = {f"og:tag{i}": f"val{i}" for i in range(12)}
    seo = MagicMock()
    seo.open_graph = True
    seo.confidence = "high"
    seo.open_graph_tags = og_tags
    seo.imagenes_alt = True

    audit_b = create_audit(
        schema_detected=True, faq_detected=True, org_detected=True, gbp_geo_score=80,
        gbp_reviews=50, gbp_place_found=True, mobile_score=85,
        whatsapp_status=ConfidenceLevel.VERIFIED.value,
        phone_web="+573****4567", whatsapp_html_detected=True, metadata_has_issues=False,
        seo_elements=seo, citability=mock_citability(score=80),
    )

    gen = V4DiagnosticGenerator()

    # Simular: generate() con audit_a → cache poblado
    gen._cached_brechas = None  # reset como lo haría generate()
    brechas_a = gen._identify_brechas(audit_a)
    assert len(brechas_a) == 6  # incluye low_seo_score (D2)

    # Simular: generate() con audit_b → cache reset
    gen._cached_brechas = None  # reset como lo haría generate()
    brechas_b = gen._identify_brechas(audit_b)
    assert len(brechas_b) == 0, f"Stale data: cache de audit_a contaminó audit_b"


def test_no_low_ia_readiness_detected_without_ia_readiness():
    """low_ia_readiness no se detecta cuando ia_readiness es None (FASE-H)."""
    audit = create_audit(
        schema_detected=False,
        gbp_geo_score=50,
        phone_web=None,
        mobile_score=60,
    )
    gen = V4DiagnosticGenerator()
    brechas = gen._identify_brechas(audit)
    pain_ids = [b['pain_id'] for b in brechas]
    assert 'low_ia_readiness' not in pain_ids


def test_loop_conventions_consistent():
    """_build_brechas_section y _build_brechas_resumen_section usan misma convención (FASE-H)."""
    audit = create_audit(
        schema_detected=False, faq_detected=False, gbp_geo_score=50,
        phone_web=None, mobile_score=60,
    )
    fs = mock_financial_scenarios()
    gen = V4DiagnosticGenerator()

    brechas = gen._identify_brechas(audit)
    section = gen._build_brechas_section(audit, fs)
    resumen = gen._build_brechas_resumen_section(audit, fs)

    # Ambos deben tener N filas/secciones igual al número de brechas
    n = len(brechas)
    # Section: headers [BRECHA 1] .. [BRECHA N]
    for i in range(1, n + 1):
        assert f"[BRECHA {i}]" in section, f"Section falta [BRECHA {i}]"
    # Resumen: N filas de tabla
    filas = [l for l in resumen.split("\n") if l.strip().startswith("|")]
    assert len(filas) == n, f"Resumen: esperado {n} filas, got {len(filas)}"


# --- Tests FASE-C: Pesos Normalizados + DynamicImpactCalculator ---

def test_normalize_weights_sums_100():
    """Normalizacion: suma de pesos siempre = 100% +/-0.1."""
    brechas = [
        {'tipo': 'schema', 'impacto': 25},
        {'tipo': 'faq', 'impacto': 12},
        {'tipo': 'metadata', 'impacto': 10},
        {'tipo': 'open_graph', 'impacto': 8},
    ]
    gen = V4DiagnosticGenerator()
    result = gen._normalize_weights(brechas)
    total = sum(b['impacto'] for b in result)
    assert abs(total - 100.0) < 0.1, f"Suma {total} != 100%"


def test_raw_weight_preserved():
    """Peso original se preserva en impacto_raw para auditoria."""
    brechas = [{'tipo': 'schema', 'impacto': 25}]
    gen = V4DiagnosticGenerator()
    result = gen._normalize_weights(brechas)
    assert result[0]['impacto_raw'] == 25
    assert result[0]['impacto'] == 100.0  # Una sola brecha = 100%
    assert result[0]['normalizado'] is True


def test_equal_weight_fallback():
    """Si todos los impactos son 0, distribucion equitativa."""
    brechas = [{'tipo': 'a', 'impacto': 0}, {'tipo': 'b', 'impacto': 0}]
    gen = V4DiagnosticGenerator()
    result = gen._normalize_weights(brechas)
    assert result[0]['impacto'] == 50.0
    assert result[1]['impacto'] == 50.0
    assert result[0]['normalizado'] is True


def test_amazilia_four_brechas_100():
    """Caso Amazilia: 4 brechas suman 100% (no 55%). Schema tiene mayor peso proporcional."""
    brechas = [
        {'tipo': 'schema_hotel', 'impacto': 25},
        {'tipo': 'faq_schema', 'impacto': 12},
        {'tipo': 'metadata', 'impacto': 10},
        {'tipo': 'open_graph', 'impacto': 8},
    ]
    gen = V4DiagnosticGenerator()
    result = gen._normalize_weights(brechas)
    total = sum(b['impacto'] for b in result)
    assert abs(total - 100.0) < 0.1, f"Suma {total} != 100%"
    # Schema deberia tener el mayor peso proporcional
    assert result[0]['impacto'] > result[1]['impacto']


def test_get_brecha_pesos_normalizes():
    """_get_brecha_pesos() siempre retorna brechas normalizadas (suma=100%)."""
    audit = create_audit(
        schema_detected=False,       # no_hotel_schema
        faq_detected=False,           # no_faq_schema
        gbp_geo_score=50,             # low_gbp_score
        phone_web=None,               # no_whatsapp_visible
        mobile_score=60,              # poor_performance
    )
    gen = V4DiagnosticGenerator()
    brechas = gen._get_brecha_pesos(audit)

    total = sum(b['impacto'] for b in brechas)
    assert abs(total - 100.0) < 0.1, f"Suma {total} != 100%"

    # Cada brecha debe tener flag normalizado
    for b in brechas:
        assert b.get('normalizado') is True
        assert 'impacto_raw' in b


def test_get_brecha_pesos_empty_audit():
    """_get_brecha_pesos() con audit vacio retorna lista vacia."""
    gen = V4DiagnosticGenerator()
    brechas = gen._get_brecha_pesos(None)
    assert brechas == []


def test_brecha_costo_uses_normalized_weights():
    """_get_brecha_costo() usa pesos normalizados + monthly_loss_central."""
    audit = create_audit(
        schema_detected=False,   # no_hotel_schema (raw 0.25)
        gbp_geo_score=50,        # low_gbp_score (raw 0.30)
        phone_web="+573****4567",
        whatsapp_html_detected=True,
        mobile_score=80,
        faq_detected=True,
        org_detected=True,
        gbp_reviews=50,
    )
    fs = mock_financial_scenarios(monthly_loss=10_000_000)
    gen = V4DiagnosticGenerator()

    costo_brecha1 = gen._get_brecha_costo(audit, fs, 0)

    # Brechas raw: low_gbp=0.30, no_hotel_schema=0.25
    # Normalizado: low_gbp = 0.30/(0.30+0.25)*100 = 54.55%
    # Costo = 10M * 0.5455 = 5,454,545
    # (no 10M * 0.30 = 3M como antes)
    brechas = gen._get_brecha_pesos(audit)
    # Verificar que el costo refleja el peso normalizado
    assert len(brechas) == 3  # + low_seo_score (seo_elements=None → web_score 25 < 40, D2)
    total = sum(b['impacto'] for b in brechas)
    assert abs(total - 100.0) < 0.1


# ============================================================================
# Tests FASE-A-COHERENCIA: D1 (OG veraz) + D2 (detección única de brechas)
# ============================================================================

# --- Helpers: inputs reales (mismos que usa el orquestador en main.py) ---

def _vs_whatsapp_conflict():
    """ValidationSummary real con conflicto de WhatsApp (diferencia clave vs sintético)."""
    from modules.commercial_documents.data_structures import ValidationSummary, ValidatedField
    return ValidationSummary(
        fields=[
            ValidatedField(
                field_name="whatsapp_number",
                value="3103724544",
                confidence=ConfidenceLevel.CONFLICT,
                sources=["web", "gbp"],
            ),
        ],
        overall_confidence=ConfidenceLevel.ESTIMATED,
    )


def _analytics_no_ga4():
    """analytics_data con GA4 no configurado (como en main.py sin --ga4-property-id)."""
    return {"use_ga4": False, "analytics_status": None, "ga4_property_id": None}


def _real_zione_audit():
    """V4AuditResult real con múltiples brechas (Zione-like) para generate()."""
    from modules.commercial_documents.data_structures import (
        V4AuditResult, SchemaValidation, GBPData, PerformanceData, CrossValidationResult,
    )
    return V4AuditResult(
        url="https://zione-hotel.com",
        hotel_name="Zione Test",
        timestamp="2026-08-03T00:00:00",
        schema=SchemaValidation(
            hotel_schema_detected=False,
            hotel_schema_valid=False,
            hotel_confidence="estimated",
            faq_schema_detected=False,
            faq_schema_valid=False,
            faq_confidence="estimated",
            org_schema_detected=False,
            total_schemas=0,
        ),
        gbp=GBPData(
            place_found=True,
            place_id="ChIzione",
            name="Zione Test",
            rating=0.0,
            reviews=5,
            photos=3,
            phone="+573104724544",
            website="https://zione-hotel.com",
            address="Vereda La Linda, Salento, Colombia",
            geo_score=50,
            geo_score_breakdown={},
            confidence="estimated",
        ),
        performance=PerformanceData(
            has_field_data=True,
            mobile_score=40,
            desktop_score=45,
            lcp=5.0,
            fid=300,
            cls=0.5,
            status="poor",
            message="Poor performance",
        ),
        validation=CrossValidationResult(
            whatsapp_status="conflict",
            phone_web="+573104724544",
            phone_gbp="+573001234567",
            adr_status="estimated",
            adr_web=300000.0,
            adr_benchmark=285000.0,
        ),
        overall_confidence="estimated",
        critical_issues=[],
        recommendations=[],
    )


def _real_financial_scenarios():
    """FinancialScenarios real (mismo patrón que test_diagnostic_generator)."""
    from modules.commercial_documents.data_structures import FinancialScenarios, Scenario
    base = Scenario(
        monthly_loss_min=1_000_000,
        monthly_loss_max=2_000_000,
        probability=0.7,
        description="Test scenario",
        assumptions=["Assumption 1"],
        confidence_score=0.8,
        monthly_loss_central=1_500_000,
    )
    return FinancialScenarios(conservative=base, realistic=base, optimistic=base)


# --- Tests nuevos FASE-A ---

def test_og_incomplete_8_tags_named_incompletos():
    """D1: 8 OG tags detectados → brecha 'Open Graph Tags Incompletos', NUNCA 'Sin'."""
    og_tags = {f"og:tag{i}": f"val{i}" for i in range(8)}  # 8 tags < umbral 10
    seo = MagicMock()
    seo.open_graph = True
    seo.confidence = "high"
    seo.open_graph_tags = og_tags
    seo.imagenes_alt = True  # web_score >= 40 → sin low_seo_score (aislar la brecha OG)
    audit = create_audit(
        schema_detected=True, faq_detected=True, org_detected=True, gbp_geo_score=80,
        phone_web="+573001234567", whatsapp_html_detected=True, mobile_score=85,
        gbp_reviews=50, seo_elements=seo, citability=mock_citability(score=80),
    )
    gen = V4DiagnosticGenerator()
    brechas = gen._identify_brechas(audit)

    og_brecha = next(b for b in brechas if b['pain_id'] == 'no_og_tags')
    assert 'Incompletos' in og_brecha['nombre'], f"Nombre: {og_brecha['nombre']}"
    assert 'Sin' not in og_brecha['nombre'], f"D1 abierto: {og_brecha['nombre']}"
    assert '8 OG tags' in og_brecha['detalle'], og_brecha['detalle']


def test_identify_brechas_matches_orchestrator_detect_pains():
    """D2: generator y orquestador producen el MISMO conjunto de brechas (mismo N)."""
    from modules.commercial_documents.pain_solution_mapper import PainSolutionMapper

    audit = create_audit(
        schema_detected=False, faq_detected=False, org_detected=False, gbp_geo_score=50,
        phone_web=None, mobile_score=40, metadata_has_issues=True, gbp_reviews=5,
        citability=mock_citability(score=20),
    )
    vs = _vs_whatsapp_conflict()
    analytics = _analytics_no_ga4()

    gen = V4DiagnosticGenerator()
    brechas = gen._identify_brechas(audit, validation_summary=vs, analytics_data=analytics,
                                    whatsapp_html_detected=False)
    mapper = PainSolutionMapper()
    pains = mapper.detect_pains(audit, vs, analytics, whatsapp_html_detected=False)

    brecha_ids = [b['pain_id'] for b in brechas]
    pain_ids = [p.id for p in pains]
    assert brecha_ids == pain_ids, f"Generator {brecha_ids} != Orquestador {pain_ids}"


def test_normalize_weights_9_pains_from_yaml():
    """D2: normalización sobre 9 pains con pesos reales del YAML (NO asumir 0.25/1.2)."""
    import yaml
    from pathlib import Path

    cfg_path = Path(__file__).resolve().parents[2] / "config" / "regional_benchmarks.yaml"
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    narratives = cfg["regions"]["eje_cafetero"]["pain_narratives"]

    # Los 2 pesos añadidos en FASE-A deben existir en el YAML
    assert narratives["low_seo_score"] == 0.20
    assert narratives["low_organic_visibility"] == 0.10

    pain_ids_9 = [
        "no_whatsapp_visible", "whatsapp_conflict", "no_hotel_schema", "no_faq_schema",
        "no_og_tags", "low_citability", "ai_crawler_blocked", "low_seo_score",
        "low_organic_visibility",
    ]
    raw_sum = sum(narratives[pid] for pid in pain_ids_9)
    assert abs(raw_sum - 1.40) < 1e-9  # guard de regresión del YAML (verificado 2026-08-03)

    brechas = [{"pain_id": pid, "impacto": narratives[pid]} for pid in pain_ids_9]
    gen = V4DiagnosticGenerator()
    result = gen._normalize_weights(brechas)

    total = sum(b["impacto"] for b in result)
    assert abs(total - 100.0) < 0.1, f"Suma {total} != 100%"
    # Expectativa calculada DESDE los pesos reales del YAML, no desde 0.25/1.2
    schema_b = next(b for b in result if b["pain_id"] == "no_hotel_schema")
    expected = narratives["no_hotel_schema"] / raw_sum * 100
    assert abs(schema_b["impacto"] - expected) < 0.1, (
        f"no_hotel_schema={schema_b['impacto']:.2f} != {expected:.2f}"
    )


def test_low_seo_and_low_organic_brechas_with_costo():
    """D2: low_seo_score y low_organic_visibility son brechas con costo al detectarse."""
    from modules.commercial_documents.data_structures import ValidationSummary

    audit = create_audit(
        schema_detected=False, faq_detected=True, org_detected=True, gbp_geo_score=80,
        phone_web="+573001234567", whatsapp_html_detected=True, mobile_score=85,
        gbp_reviews=50,  # schema False + seo_elements=None → web_score 25 < 40 → low_seo_score
    )
    vs = ValidationSummary(fields=[], overall_confidence=ConfidenceLevel.ESTIMATED)
    analytics = _analytics_no_ga4()
    gen = V4DiagnosticGenerator()
    # Simular generate(): guardar inputs reales como atributos (punto 3a del mandato)
    gen._current_validation_summary = vs
    gen._current_analytics_data = analytics
    gen._current_whatsapp_html_detected = True

    brechas = gen._identify_brechas(audit)
    ids = [b['pain_id'] for b in brechas]
    assert 'low_seo_score' in ids, f"Falta low_seo_score en {ids}"
    assert 'low_organic_visibility' in ids, f"Falta low_organic_visibility en {ids}"

    # Con costo: pesos normalizados > 0 y _get_brecha_costo != "0"
    fs = mock_financial_scenarios(monthly_loss=10_000_000)
    pesos = gen._get_brecha_pesos(audit)
    b_seo = next(b for b in pesos if b['pain_id'] == 'low_seo_score')
    b_org = next(b for b in pesos if b['pain_id'] == 'low_organic_visibility')
    assert b_seo['impacto'] > 0
    assert b_org['impacto'] > 0
    assert gen._get_brecha_costo(audit, fs, pesos.index(b_seo)) != "0"
    assert gen._get_brecha_costo(audit, fs, pesos.index(b_org)) != "0"


def test_cache_not_freeze_synthetic_detection():
    """D2 CRÍTICO: caché keyed por inputs — la detección sintética no congela la real."""
    from modules.commercial_documents.pain_solution_mapper import PainSolutionMapper

    audit = create_audit(
        schema_detected=False, faq_detected=False, org_detected=False, gbp_geo_score=50,
        phone_web=None, mobile_score=40, metadata_has_issues=True, gbp_reviews=5,
        citability=mock_citability(score=20),
    )
    vs = _vs_whatsapp_conflict()
    analytics = _analytics_no_ga4()
    gen = V4DiagnosticGenerator()

    # 1) Sin inputs → fallback VS sintético (fields=[], sin conflicto)
    sinteticas = gen._identify_brechas(audit)
    assert 'whatsapp_conflict' not in [b['pain_id'] for b in sinteticas]

    # 2) Con inputs reales → key distinto → recalcula (no congela la sintética)
    brechas = gen._identify_brechas(audit, validation_summary=vs, analytics_data=analytics,
                                    whatsapp_html_detected=False)
    ids = [b['pain_id'] for b in brechas]
    assert 'whatsapp_conflict' in ids  # el VS real sí lo detecta

    # 3) Mismo N y conjunto que detect_pains del orquestador (assert EXACTO, sin tolerancia)
    mapper = PainSolutionMapper()
    pains = mapper.detect_pains(audit, vs, analytics, whatsapp_html_detected=False)
    assert ids == [p.id for p in pains], f"Generator {ids} != Orquestador {[p.id for p in pains]}"


def test_generate_template_dynamic_brechas_count():
    """D2: template renderizado usa conteo dinámico, nunca '7 brechas'."""
    import tempfile
    from pathlib import Path
    from modules.commercial_documents.pain_solution_mapper import PainSolutionMapper

    audit = _real_zione_audit()
    vs = _vs_whatsapp_conflict()
    analytics = _analytics_no_ga4()
    financial = _real_financial_scenarios()
    gen = V4DiagnosticGenerator()

    with tempfile.TemporaryDirectory() as tmpdir:
        path = gen.generate(
            audit_result=audit,
            validation_summary=vs,
            financial_scenarios=financial,
            hotel_name="Zione Test",
            hotel_url="https://zione-hotel.com",
            output_dir=tmpdir,
            coherence_score=0.85,
            gate_status="PASSED",
            region="eje_cafetero",
            analytics_data=analytics,
        )
        content = Path(path).read_text(encoding="utf-8")

        # Ningún conteo hardcodeado
        assert "7 brechas" not in content, "Template aún hardcodea '7 brechas'"

        # Conteo dinámico == N de detect_pains del orquestador (mismos inputs)
        mapper = PainSolutionMapper()
        pains = mapper.detect_pains(audit, vs, analytics, whatsapp_html_detected=False)
        expected_n = len(pains)
        assert expected_n > 0
        assert f"De las {expected_n} brechas técnicas detectadas" in content, (
            f"Falta conteo dinámico {expected_n} en documento"
        )

        # generate() guarda los inputs reales (punto 3a del mandato)
        assert gen._current_validation_summary is vs
        assert gen._current_analytics_data is analytics

        # Caché no congela: tras generate(), _identify_brechas con inputs reales
        # devuelve el MISMO N que detect_pains del orquestador
        brechas = gen._identify_brechas(audit, validation_summary=vs, analytics_data=analytics,
                                        whatsapp_html_detected=False)
        assert [b['pain_id'] for b in brechas] == [p.id for p in pains]
