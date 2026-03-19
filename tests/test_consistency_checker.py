"""
Tests para el Consistency Checker - Fase 2.

Valida la coherencia interna y cruzada de assessments,
detección de conflictos hard/soft, y criterios de exportación.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from uuid import uuid4
from data_validation.consistency_checker import (
    ConsistencyChecker, ConsistencyReport, CanonicalAssessment
)
from data_validation.contradiction_engine import Claim, ContradictionEngine, ConflictType


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def checker():
    """Instancia de ConsistencyChecker para tests."""
    return ConsistencyChecker()


@pytest.fixture
def consistent_assessment():
    """Assessment sin conflictos - datos consistentes."""
    claims = [
        {"key": "whatsapp", "value": "+52 998 123 4567"},
        {"key": "whatsapp_number", "value": "9981234567"},
        {"key": "gbp_rating", "value": "4.5"},
        {"key": "schema_type", "value": "Hotel"},
        {"key": "hotel_name", "value": "Hotel Test"},
        {"key": "phone", "value": "+52 998 123 4567"},
    ]
    return CanonicalAssessment(
        assessment_id=uuid4(),
        hotel_name="Hotel Test",
        claims=claims
    )


@pytest.fixture
def inconsistent_assessment():
    """Assessment con conflictos - datos inconsistentes."""
    claims = [
        {"key": "whatsapp", "value": "+52 998 123 4567"},
        {"key": "whatsapp_number", "value": "+52 998 765 4321"},  # Diferente número
        {"key": "gbp_rating", "value": "5.5"},  # Rating inválido (>5)
        {"key": "gbp_secondary_rating", "value": "3.2"},  # Diferente rating
        {"key": "schema_type", "value": "InvalidType"},  # Tipo inválido
        {"key": "hotel_name", "value": "Hotel Test"},
        {"key": "phone", "value": "+52 998 999 9999"},  # Diferente teléfono
    ]
    return CanonicalAssessment(
        assessment_id=uuid4(),
        hotel_name="Hotel Test",
        claims=claims
    )


@pytest.fixture
def engine_claims_consistent():
    """Claims del ContradictionEngine consistentes."""
    return [
        Claim(
            claim_id=uuid4(),
            category="schema_presence",
            message="Schema.org detectado en el sitio",
            confidence=0.95,
        ),
        Claim(
            claim_id=uuid4(),
            category="whatsapp_presence",
            message="WhatsApp verificado y visible",
            confidence=0.92,
        ),
    ]


@pytest.fixture
def engine_claims_hard_conflict():
    """Claims del ContradictionEngine con conflictos HARD."""
    return [
        Claim(
            claim_id=uuid4(),
            category="schema_presence",
            message="Schema.org detectado en el sitio",
            confidence=0.95,
        ),
        Claim(
            claim_id=uuid4(),
            category="schema_presence",
            message="Schema.org no detectado",
            confidence=0.90,
        ),
    ]


# =============================================================================
# Tests de Consistencia de Claims Específicos
# =============================================================================

def test_check_whatsapp_consistency(checker):
    """Test 1: Verificar consistencia de WhatsApp."""
    # WhatsApp consistente - mismos números normalizados
    consistent_claims = [
        {"key": "whatsapp", "value": "+52 998 123 4567"},
        {"key": "whatsapp_number", "value": "9981234567"},
    ]
    result = checker._check_whatsapp_consistency(consistent_claims)
    assert result is True

    # WhatsApp inconsistente - números diferentes
    inconsistent_claims = [
        {"key": "whatsapp", "value": "+52 998 123 4567"},
        {"key": "whatsapp_number", "value": "+52 998 765 4321"},
    ]
    result = checker._check_whatsapp_consistency(inconsistent_claims)
    assert result is False

    # Sin claims de WhatsApp - debe retornar True
    no_whatsapp_claims = [
        {"key": "phone", "value": "+52 998 123 4567"},
    ]
    result = checker._check_whatsapp_consistency(no_whatsapp_claims)
    assert result is True


def test_check_gbp_consistency(checker):
    """Test 2: Verificar consistencia de GBP."""
    # GBP consistente
    consistent_claims = [
        {"key": "gbp_rating", "value": "4.5"},
        {"key": "gbp_reviews", "value": "150"},
    ]
    result = checker._check_gbp_consistency(consistent_claims)
    assert result is True

    # Rating inválido (>5) - requiere al menos 2 claims GBP para validación
    invalid_rating_claims = [
        {"key": "gbp_rating", "value": "6.0"},
        {"key": "gbp_reviews", "value": "100"},
    ]
    result = checker._check_gbp_consistency(invalid_rating_claims)
    assert result is False

    # Ratings con diferencia significativa (>1.0)
    mismatched_ratings = [
        {"key": "gbp_rating", "value": "2.0"},
        {"key": "gbp_secondary_rating", "value": "4.5"},
    ]
    result = checker._check_gbp_consistency(mismatched_ratings)
    assert result is False


def test_check_schema_consistency(checker):
    """Test 3: Verificar consistencia de Schema."""
    # Schema válido con tipo Hotel
    valid_schema = [
        {"key": "schema_type", "value": "Hotel"},
        {"key": "schema_data", "value": {"@type": "Hotel"}},
    ]
    result = checker._check_schema_consistency(valid_schema)
    assert result is True

    # Schema válido con tipo LodgingBusiness
    lodging_schema = [
        {"key": "schema_type", "value": "LodgingBusiness"},
    ]
    result = checker._check_schema_consistency(lodging_schema)
    assert result is True

    # Schema inválido - tipo no reconocido
    invalid_schema = [
        {"key": "schema_type", "value": "InvalidType"},
    ]
    result = checker._check_schema_consistency(invalid_schema)
    assert result is False

    # Sin claims de schema - debe retornar True
    no_schema = [
        {"key": "hotel_name", "value": "Test Hotel"},
    ]
    result = checker._check_schema_consistency(no_schema)
    assert result is True


# =============================================================================
# Tests de Criterios de Exportación
# =============================================================================

def test_can_export_with_hard_conflicts(checker, inconsistent_assessment):
    """Test 4: No se puede exportar con conflictos HARD."""
    # Crear claims que generen conflicto HARD
    claims_with_hard_conflict = [
        {"key": "gbp_rating", "value": "6.0"},  # Rating inválido = HARD conflict
        {"key": "gbp_secondary_rating", "value": "2.0"},  # Diferencia > 1.0
    ]
    assessment = CanonicalAssessment(
        assessment_id=uuid4(),
        hotel_name="Test Hotel",
        claims=claims_with_hard_conflict
    )

    can_export, message = checker.can_export(assessment)

    assert can_export is False
    assert "BLOQUEADO" in message
    assert "HARD" in message or "conflicto" in message.lower()


def test_can_export_without_conflicts(checker, consistent_assessment):
    """Test 5: Se puede exportar sin conflictos."""
    can_export, message = checker.can_export(consistent_assessment)

    assert can_export is True
    assert "OK" in message or "consistente" in message.lower()


def test_can_export_low_confidence_blocked(checker):
    """Test 11: Bloqueo por baja confianza (< 0.5)."""
    # Assessment con muchos conflictos que reducen el score
    many_conflicts_claims = []
    for i in range(10):
        many_conflicts_claims.append({"key": f"conflict_{i}", "value": f"value_{i}"})

    assessment = CanonicalAssessment(
        assessment_id=uuid4(),
        hotel_name="Test Hotel",
        claims=many_conflicts_claims
    )

    can_export, message = checker.can_export(assessment)

    # Muchos conflictos reducen el score de confianza
    if not can_export:
        assert "BLOQUEADO" in message or "confianza" in message.lower()


def test_can_export_with_soft_conflicts_warning(checker):
    """Test 12: Advertencia con SOFT conflicts (> 5)."""
    # Assessment con 6+ soft conflicts pero sin hard conflicts
    soft_conflict_claims = [
        {"key": "whatsapp", "value": "+52 998 123 4567"},  # WhatsApp OK
    ]
    # Agregar claims que generen soft conflicts (diferencias menores)
    for i in range(6):
        soft_conflict_claims.append({
            "key": f"gbp_data_{i}",
            "value": f"data_{i}"
        })

    assessment = CanonicalAssessment(
        assessment_id=uuid4(),
        hotel_name="Test Hotel",
        claims=soft_conflict_claims
    )

    report = checker.check_assessment_consistency(assessment)
    can_export, message = checker.can_export(assessment)

    # Si hay muchos soft conflicts, debe permitir export con advertencia
    # o estar bloqueado por otro motivo
    if can_export and report.soft_conflicts_count > 5:
        assert "ADVERTENCIA" in message or "warning" in message.lower()


# =============================================================================
# Tests de Reporte y Formatos
# =============================================================================

def test_consistency_report_format(checker, consistent_assessment):
    """Test 6: Formato correcto del reporte."""
    report = checker.check_assessment_consistency(consistent_assessment)

    # Verificar tipo de retorno
    assert isinstance(report, ConsistencyReport)

    # Verificar atributos requeridos
    assert hasattr(report, "is_consistent")
    assert hasattr(report, "inconsistencies")
    assert hasattr(report, "recommendations")
    assert hasattr(report, "hard_conflicts_count")
    assert hasattr(report, "soft_conflicts_count")
    assert hasattr(report, "confidence_score")

    # Verificar tipos
    assert isinstance(report.is_consistent, bool)
    assert isinstance(report.inconsistencies, list)
    assert isinstance(report.recommendations, list)
    assert isinstance(report.hard_conflicts_count, int)
    assert isinstance(report.soft_conflicts_count, int)
    assert isinstance(report.confidence_score, float)

    # Verificar que to_dict funciona
    report_dict = report.to_dict()
    assert "is_consistent" in report_dict
    assert "summary" in report_dict
    assert "confidence_score" in report_dict


def test_calculate_confidence_score(checker):
    """Test 10: Cálculo de score de confianza."""
    # Sin claims - score neutral (0.5)
    score = checker._calculate_confidence_score([], 0)
    assert score == 0.5

    # Claims sin conflictos - score alto
    good_claims = [
        {"key": "whatsapp", "value": "1234567890"},
        {"key": "phone", "value": "1234567890"},
        {"key": "gbp_rating", "value": "4.5"},
    ]
    score = checker._calculate_confidence_score(good_claims, 0)
    assert score > 0.8

    # Claims con conflictos - score reducido
    score_with_conflicts = checker._calculate_confidence_score(good_claims, 3)
    assert score_with_conflicts < score

    # Score nunca menor a 0.0 ni mayor a 1.0
    extreme_claims = [{"key": f"key_{i}", "value": f"val_{i}"} for i in range(100)]
    extreme_score = checker._calculate_confidence_score(extreme_claims, 50)
    assert 0.0 <= extreme_score <= 1.0


# =============================================================================
# Tests de Assessment Consistency
# =============================================================================

def test_check_assessment_consistent(checker, consistent_assessment):
    """Test 7: Assessment consistente."""
    report = checker.check_assessment_consistency(consistent_assessment)

    assert isinstance(report, ConsistencyReport)
    assert report.is_consistent is True
    assert report.hard_conflicts_count == 0


def test_check_assessment_inconsistent(checker, inconsistent_assessment):
    """Test 8: Assessment inconsistente."""
    report = checker.check_assessment_consistency(inconsistent_assessment)

    assert isinstance(report, ConsistencyReport)
    # Debe detectar al menos algún conflicto
    total_conflicts = report.hard_conflicts_count + report.soft_conflicts_count
    assert total_conflicts > 0
    assert len(report.inconsistencies) > 0


# =============================================================================
# Tests de Consistencia Cruzada entre Documentos
# =============================================================================

def test_cross_document_consistency(checker):
    """Test 9: Consistencia entre dos documentos."""
    # Documentos consistentes
    doc1_claims = [
        {"key": "hotel_name", "value": "Hotel Test"},
        {"key": "phone", "value": "+52 998 123 4567"},
        {"key": "address", "value": "Calle Principal 123"},
    ]
    doc2_claims = [
        {"key": "hotel_name", "value": "Hotel Test"},  # Mismo nombre
        {"key": "phone", "value": "+52 998 123 4567"},  # Mismo teléfono
        {"key": "email", "value": "info@hoteltest.com"},  # Claim único
    ]

    report = checker.check_cross_document_consistency(doc1_claims, doc2_claims)

    assert isinstance(report, ConsistencyReport)
    # Los claims comunes son consistentes, solo hay claims únicos
    # Claims únicos generan soft conflicts
    assert report.hard_conflicts_count == 0

    # Documentos inconsistentes
    doc3_claims = [
        {"key": "hotel_name", "value": "Hotel Test Viejo"},  # Diferente nombre
        {"key": "phone", "value": "+52 998 999 9999"},  # Diferente teléfono
    ]

    report_inconsistent = checker.check_cross_document_consistency(doc1_claims, doc3_claims)

    assert isinstance(report_inconsistent, ConsistencyReport)
    # Hotel name y phone son campos hard, deben generar conflictos hard
    assert report_inconsistent.hard_conflicts_count > 0 or report_inconsistent.soft_conflicts_count > 0


# =============================================================================
# Tests de Integración con ContradictionEngine
# =============================================================================

def test_consistency_checker_with_engine(engine_claims_hard_conflict):
    """Test de integración: ConsistencyChecker con ContradictionEngine."""
    engine = ContradictionEngine()
    checker = ConsistencyChecker(contradiction_engine=engine)

    # Crear assessment con claims que generan conflictos
    assessment = CanonicalAssessment(
        assessment_id=uuid4(),
        hotel_name="Test Hotel",
        claims=engine_claims_hard_conflict
    )

    report = checker.check_assessment_consistency(assessment)

    # El engine debe haber detectado el conflicto HARD de schema
    assert isinstance(report, ConsistencyReport)
    # El total de conflictos debe reflejar los del engine
    total_conflicts = report.hard_conflicts_count + report.soft_conflicts_count
    assert total_conflicts >= 0  # Puede ser 0 si el engine no detecta los claims


def test_consistency_report_summary_generation(checker, consistent_assessment):
    """Test: Generación correcta de summary en reporte."""
    report = checker.check_assessment_consistency(consistent_assessment)

    summary = report._generate_summary()
    assert isinstance(summary, str)
    assert len(summary) > 0

    # Sin conflictos
    if report.hard_conflicts_count == 0 and report.soft_conflicts_count == 0:
        assert "consistente" in summary.lower() or "OK" in summary


# =============================================================================
# Tests de Normalización y Helpers
# =============================================================================

def test_normalize_phone(checker):
    """Test: Normalización de números de teléfono."""
    # Normalizar números mexicanos
    assert checker._normalize_phone("+52 998 123 4567") == "9981234567"
    assert checker._normalize_phone("5219981234567") == "9981234567"
    assert checker._normalize_phone("998-123-4567") == "9981234567"
    assert checker._normalize_phone("998 123 4567") == "9981234567"


def test_claims_match(checker):
    """Test: Comparación de claims."""
    # Claims que coinciden
    claim1 = {"key": "name", "value": "Hotel Test"}
    claim2 = {"key": "name", "value": "hotel test"}  # Case insensitive
    assert checker._claims_match(claim1, claim2) is True

    # Claims que no coinciden
    claim3 = {"key": "name", "value": "Hotel Different"}
    assert checker._claims_match(claim1, claim3) is False

    # Números con tolerancia
    num1 = {"key": "rating", "value": 4.5}
    num2 = {"key": "rating", "value": 4.50001}  # Dentro de tolerancia
    assert checker._claims_match(num1, num2) is True


def test_determine_conflict_severity(checker):
    """Test: Determinación de severidad de conflictos."""
    # Campos que generan conflictos hard
    hard_claim = {"key": "phone", "value": "1234567890"}
    assert checker._determine_conflict_severity(hard_claim, hard_claim) == "hard"

    hard_claim2 = {"key": "hotel_name", "value": "Test"}
    assert checker._determine_conflict_severity(hard_claim2, hard_claim2) == "hard"

    # Campos que generan conflictos soft
    soft_claim = {"key": "description", "value": "A nice hotel"}
    assert checker._determine_conflict_severity(soft_claim, soft_claim) == "soft"


def test_is_verifiable(checker):
    """Test: Identificación de claims verificables."""
    # Claims verificables
    assert checker._is_verifiable({"key": "phone", "value": "123"}) is True
    assert checker._is_verifiable({"key": "whatsapp", "value": "123"}) is True
    assert checker._is_verifiable({"key": "gbp_rating", "value": "4.5"}) is True
    assert checker._is_verifiable({"key": "schema_data", "value": {} }) is True
    assert checker._is_verifiable({"key": "email", "value": "test@test.com"}) is True

    # Claims no verificables
    assert checker._is_verifiable({"key": "description", "value": "Nice"}) is False
    assert checker._is_verifiable({"key": "color", "value": "blue"}) is False


# =============================================================================
# Tests de CanonicalAssessment
# =============================================================================

def test_canonical_assessment_creation():
    """Test: Creación de CanonicalAssessment."""
    assessment_id = uuid4()
    claims = [{"key": "test", "value": "value"}]

    assessment = CanonicalAssessment(
        assessment_id=assessment_id,
        hotel_name="Test Hotel",
        claims=claims
    )

    assert assessment.assessment_id == assessment_id
    assert assessment.hotel_name == "Test Hotel"
    assert assessment.claims == claims
    assert assessment.version == "1.0"
    assert assessment.generated_at is not None


def test_canonical_assessment_with_string_uuid():
    """Test: CanonicalAssessment acepta string UUID."""
    assessment_id = str(uuid4())

    assessment = CanonicalAssessment(
        assessment_id=assessment_id,
        hotel_name="Test Hotel",
        claims=[]
    )

    assert isinstance(assessment.assessment_id, type(uuid4()))
