"""
Tests de regresión: Hotel Vísperas - Caso Real de Conflictos

Basado en el análisis real del Hotel Vísperas donde se detectaron:
- WhatsApp VERIFIED en schema pero marcado como "no visible" en otro punto
- GBP existe pero marcado como "no registrado"
- Estos conflictos deben ser detectados como HARD y bloquear exportación

Fase 2: Validación de coherencia y detección de conflictos
"""

import pytest
from uuid import uuid4
from data_validation.contradiction_engine import (
    ContradictionEngine, Claim, ConflictType
)
from data_validation.consistency_checker import ConsistencyChecker, CanonicalAssessment


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def engine():
    """Fixture del ContradictionEngine."""
    return ContradictionEngine()


@pytest.fixture
def checker(engine):
    """Fixture del ConsistencyChecker con engine."""
    return ConsistencyChecker(contradiction_engine=engine)


@pytest.fixture
def visperas_whatsapp_verified():
    """Claim: WhatsApp VERIFIED en schema."""
    return Claim(
        claim_id=uuid4(),
        category="whatsapp_schema",
        message="WhatsApp VERIFIED detectado en schema: +57 311 3973744",
        confidence=0.95,
        evidence_excerpt="\"telephone\": \"+57 311 3973744\"",
        metadata={"source": "schema_org", "status": "verified"}
    )


@pytest.fixture
def visperas_whatsapp_not_visible():
    """Claim: WhatsApp no visible en página."""
    return Claim(
        claim_id=uuid4(),
        category="whatsapp_visibility",
        message="Botón WhatsApp no visible en página principal",
        confidence=0.85,
        evidence_excerpt="No se encontró elemento .whatsapp-button",
        metadata={"source": "visual_check", "status": "not_visible"}
    )


@pytest.fixture
def visperas_gbp_exists():
    """Claim: GBP existe."""
    return Claim(
        claim_id=uuid4(),
        category="gbp_presence",
        message="GBP existe y está activo",
        confidence=0.92,
        evidence_excerpt="Hotel Vísperas en Google Maps",
        metadata={"source": "places_api", "gbp_id": "ChIJ1234567890"}
    )


@pytest.fixture
def visperas_gbp_not_registered():
    """Claim: GBP no registrado."""
    return Claim(
        claim_id=uuid4(),
        category="gbp_registration",
        message="GBP no registrado en el sistema",
        confidence=0.80,
        evidence_excerpt="No se encontró registro de GBP",
        metadata={"source": "database_check", "status": "missing"}
    )


@pytest.fixture
def visperas_schema_hotel():
    """Claim: Schema Hotel detectado."""
    return Claim(
        claim_id=uuid4(),
        category="schema_presence",
        message="Schema Hotel detectado correctamente",
        confidence=0.94,
        evidence_excerpt="\"@type\": \"Hotel\"",
        metadata={"source": "schema_check", "type": "Hotel"}
    )


@pytest.fixture
def visperas_schema_no_organization():
    """Claim: Schema Organization NO detectado (no es conflicto con Hotel)."""
    return Claim(
        claim_id=uuid4(),
        category="schema_presence",
        message="Schema Organization no detectado",
        confidence=0.88,
        evidence_excerpt="No se encontró @type Organization",
        metadata={"source": "schema_check", "type": "Organization"}
    )


@pytest.fixture
def visperas_whatsapp_web_number():
    """Claim: WhatsApp desde web."""
    return Claim(
        claim_id=uuid4(),
        category="whatsapp_web",
        message="WhatsApp web: +57 311 3973744",
        confidence=0.93,
        evidence_excerpt="href=\"https://wa.me/573113973744\"",
        metadata={"source": "web_scraping", "channel": "web"}
    )


@pytest.fixture
def visperas_whatsapp_gbp_number():
    """Claim: WhatsApp diferente desde GBP."""
    return Claim(
        claim_id=uuid4(),
        category="whatsapp_gbp",
        message="WhatsApp GBP: +57 320 8888888",
        confidence=0.91,
        evidence_excerpt="phone: +57 320 8888888",
        metadata={"source": "gbp_api", "channel": "gbp"}
    )


# ============================================================================
# Test 1: WhatsApp Conflict Detected
# ============================================================================

def test_visperas_whatsapp_conflict_detected(
    engine,
    visperas_whatsapp_verified,
    visperas_whatsapp_not_visible
):
    """
    Test 1: Detectar conflicto de WhatsApp específico del Hotel Vísperas.
    
    Escenario:
    - WhatsApp detectado en schema: +57 311 3973744 (VERIFIED, confidence 0.95)
    - Algún punto dice "no visible" (confidence 0.85)
    
    Esperado:
    - Debe detectar conflicto HARD de whatsapp_visibility
    - El conflicto debe ser del tipo ConflictType.HARD
    """
    claims = [
        visperas_whatsapp_verified,
        visperas_whatsapp_not_visible
    ]
    
    conflicts = engine.detect_conflicts(claims)
    hard_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.HARD]
    
    # Debe haber al menos un conflicto HARD
    assert len(hard_conflicts) >= 1, "Se esperaba al menos un conflicto HARD"
    
    # El conflicto debe ser de tipo whatsapp_visibility
    whatsapp_conflicts = [c for c in hard_conflicts if "whatsapp" in c.field]
    assert len(whatsapp_conflicts) >= 1, "Se esperaba conflicto en campo whatsapp"
    
    # Verificar que el conflicto relaciona VERIFIED con no visible
    conflict = whatsapp_conflicts[0]
    assert "visible" in conflict.description.lower() or "whatsapp" in conflict.description.lower()
    assert conflict.conflict_type == ConflictType.HARD


# ============================================================================
# Test 2: GBP Conflict Detected
# ============================================================================

def test_visperas_gbp_conflict_detected(
    engine,
    visperas_gbp_exists,
    visperas_gbp_not_registered
):
    """
    Test 2: Detectar conflicto de GBP del Hotel Vísperas.
    
    Escenario:
    - Un validador dice que GBP existe (confidence 0.92)
    - Otro dice que no está registrado (confidence 0.80)
    
    Esperado:
    - Debe detectar conflicto HARD de gbp_registration
    """
    claims = [
        visperas_gbp_exists,
        visperas_gbp_not_registered
    ]
    
    conflicts = engine.detect_conflicts(claims)
    hard_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.HARD]
    
    # Debe haber al menos un conflicto HARD
    assert len(hard_conflicts) >= 1, "Se esperaba al menos un conflicto HARD"
    
    # El conflicto debe ser relacionado a GBP
    gbp_conflicts = [c for c in hard_conflicts if "gbp" in c.field.lower()]
    assert len(gbp_conflicts) >= 1, "Se esperaba conflicto en campo GBP"
    
    # Verificar que el conflicto menciona la contradicción
    conflict = gbp_conflicts[0]
    assert "gbp" in conflict.description.lower()
    assert conflict.conflict_type == ConflictType.HARD


# ============================================================================
# Test 3: No False Positives
# ============================================================================

def test_visperas_no_false_positives(
    engine,
    visperas_schema_hotel,
    visperas_schema_no_organization,
    visperas_whatsapp_verified
):
    """
    Test 3: No generar falsos positivos.
    
    Escenario:
    - Schema Hotel detectado vs Schema Organization NO detectado (NO es conflicto)
    - WhatsApp consistente en múltiples claims (mismo número)
    
    Esperado:
    - No debe haber conflictos HARD de schema (tipos diferentes son normales)
    - No debe haber conflictos de whatsapp si los números coinciden
    """
    # Crear un segundo claim de WhatsApp con el mismo número
    whatsapp_consistent = Claim(
        claim_id=uuid4(),
        category="whatsapp_footer",
        message="WhatsApp verificado: +57 311 3973744",
        confidence=0.91,
        evidence_excerpt="+57 311 3973744",
        metadata={"source": "footer_check"}
    )
    
    claims = [
        visperas_schema_hotel,
        visperas_schema_no_organization,
        visperas_whatsapp_verified,
        whatsapp_consistent
    ]
    
    conflicts = engine.detect_conflicts(claims)
    hard_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.HARD]
    
    # No debe haber conflictos HARD de schema (son tipos diferentes)
    schema_conflicts = [c for c in hard_conflicts if "schema" in c.field.lower()]
    assert len(schema_conflicts) == 0, "No debe haber conflictos HARD de schema para tipos diferentes"
    
    # No debe haber conflictos de whatsapp (números coinciden)
    whatsapp_conflicts = [c for c in hard_conflicts if "whatsapp" in c.field.lower()]
    assert len(whatsapp_conflicts) == 0, "No debe haber conflictos de WhatsApp si los números coinciden"


# ============================================================================
# Test 4: WhatsApp Number Mismatch
# ============================================================================

def test_visperas_whatsapp_number_mismatch(
    engine,
    visperas_whatsapp_web_number,
    visperas_whatsapp_gbp_number
):
    """
    Test 4: Detectar números de WhatsApp diferentes.
    
    Escenario:
    - Web: +57 311 3973744
    - GBP: +57 320 8888888
    
    Esperado:
    - Debe detectar conflicto HARD de whatsapp_number
    - La descripción debe mencionar ambos números
    """
    claims = [
        visperas_whatsapp_web_number,
        visperas_whatsapp_gbp_number
    ]
    
    conflicts = engine.detect_conflicts(claims)
    hard_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.HARD]
    
    # Debe haber conflicto de mismatch de números
    number_conflicts = [c for c in hard_conflicts if "number" in c.field.lower()]
    assert len(number_conflicts) >= 1, "Se esperaba conflicto de número de WhatsApp"
    
    # Verificar que el conflicto menciona ambos números
    conflict = number_conflicts[0]
    assert "573113973744" in conflict.description.replace(" ", "").replace("+", "") or \
           "3113973744" in conflict.description.replace(" ", "")
    assert "573208888888" in conflict.description.replace(" ", "").replace("+", "") or \
           "3208888888" in conflict.description.replace(" ", "")


# ============================================================================
# Test 5: Assessment Blocks Export
# ============================================================================

def test_visperas_assessment_blocked_export(
    checker,
    visperas_whatsapp_verified,
    visperas_whatsapp_not_visible,
    visperas_gbp_exists,
    visperas_gbp_not_registered
):
    """
    Test 5: Assessment completo bloquea exportación.
    
    Escenario:
    - Simula assessment completo de Vísperas con conflictos reales
    - WhatsApp conflict + GBP conflict
    
    Esperado:
    - can_export debe retornar (False, "BLOQUEADO...")
    """
    claims = [
        visperas_whatsapp_verified,
        visperas_whatsapp_not_visible,
        visperas_gbp_exists,
        visperas_gbp_not_registered
    ]
    
    assessment = CanonicalAssessment(
        assessment_id=uuid4(),
        hotel_name="Hotel Vísperas",
        claims=claims
    )
    
    can_export, message = checker.can_export(assessment)
    
    # Debe bloquear exportación
    assert can_export is False, "La exportación debe estar bloqueada con conflictos HARD"
    
    # El mensaje debe indicar BLOQUEADO
    assert "BLOQUEADO" in message.upper(), "El mensaje debe indicar que está bloqueado"
    
    # Debe mencionar conflictos HARD
    assert "HARD" in message.upper() or "conflicto" in message.lower(), \
        "El mensaje debe mencionar conflictos HARD"


# ============================================================================
# Test 6: Consistency Report
# ============================================================================

def test_visperas_consistency_report(
    checker,
    visperas_whatsapp_verified,
    visperas_whatsapp_not_visible,
    visperas_gbp_exists,
    visperas_gbp_not_registered
):
    """
    Test 6: Reporte de consistencia con conflictos de Vísperas.
    
    Escenario:
    - Assessment con conflictos de Vísperas
    
    Esperado:
    - is_consistent = False
    - hard_conflicts_count >= 1
    - El reporte tiene formato correcto
    """
    claims = [
        visperas_whatsapp_verified,
        visperas_whatsapp_not_visible,
        visperas_gbp_exists,
        visperas_gbp_not_registered
    ]
    
    assessment = CanonicalAssessment(
        assessment_id=uuid4(),
        hotel_name="Hotel Vísperas",
        claims=claims
    )
    
    report = checker.check_assessment_consistency(assessment)
    
    # El assessment no debe ser consistente
    assert report.is_consistent is False, "El assessment con conflictos HARD no debe ser consistente"
    
    # Debe tener al menos un conflicto HARD
    assert report.hard_conflicts_count >= 1, "Debe haber al menos un conflicto HARD"
    
    # Debe tener inconsistencias documentadas
    assert len(report.inconsistencies) >= 1, "Debe haber inconsistencias documentadas"
    
    # Debe tener recomendaciones
    assert len(report.recommendations) >= 1, "Debe haber recomendaciones"
    
    # El reporte debe poder convertirse a dict
    report_dict = report.to_dict()
    assert "is_consistent" in report_dict
    assert "hard_conflicts_count" in report_dict
    assert "soft_conflicts_count" in report_dict
    assert "inconsistencies" in report_dict
    assert "recommendations" in report_dict
    assert "confidence_score" in report_dict
    assert "summary" in report_dict
    
    # Verificar que el summary refleja los conflictos
    assert "conflicto" in report_dict["summary"].lower() or "conflict" in report_dict["summary"].lower(), \
        "El summary debe mencionar los conflictos"
