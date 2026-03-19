"""
Tests para el Contradiction Engine - Fase 2

Este módulo prueba la detección de conflictos entre claims
con clasificación HARD (bloquea exportación) y SOFT (incluye disclaimer).
"""

import sys
from pathlib import Path

# Add project root to Python path for pytest
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from uuid import uuid4
from data_validation.contradiction_engine import (
    ContradictionEngine, Claim, ConflictType, Conflict
)


@pytest.fixture
def engine():
    """Fixture que proporciona una instancia del ContradictionEngine."""
    return ContradictionEngine()


@pytest.fixture
def sample_whatsapp_verified():
    """Claim de WhatsApp verificado con alta confianza."""
    return Claim(
        claim_id=uuid4(),
        category="whatsapp_presence",
        message="WhatsApp VERIFIED con confianza 0.95",
        confidence=0.95,
        evidence_excerpt="Botón WhatsApp visible en footer",
        metadata={"source": "validation", "phone": "+34600123456"}
    )


@pytest.fixture
def sample_whatsapp_not_visible():
    """Claim de WhatsApp no visible."""
    return Claim(
        claim_id=uuid4(),
        category="whatsapp_presence",
        message="WhatsApp no visible en la página",
        confidence=0.85,
        evidence_excerpt="No se detectó botón WhatsApp",
        metadata={"source": "scraping"}
    )


@pytest.fixture
def sample_schema_present():
    """Claim de Schema.org presente."""
    return Claim(
        claim_id=uuid4(),
        category="schema_presence",
        message="Schema.org presente e implementado en el sitio",
        confidence=0.92,
        evidence_excerpt="<script type=\"application/ld+json\">",
        metadata={"source": "scraping"}
    )


@pytest.fixture
def sample_schema_absent():
    """Claim de Schema.org ausente."""
    return Claim(
        claim_id=uuid4(),
        category="schema_presence",
        message="Schema.org ausente del sitio web",
        confidence=0.88,
        evidence_excerpt="No se encontraron scripts ld+json",
        metadata={"source": "validation"}
    )


@pytest.fixture
def sample_gbp_exists():
    """Claim de GBP existente."""
    return Claim(
        claim_id=uuid4(),
        category="gbp_presence",
        message="Google Business Profile existe y está activo",
        confidence=0.90,
        evidence_excerpt="Place ID encontrado: ChIJ...",
        metadata={"source": "places_api"}
    )


@pytest.fixture
def sample_gbp_not_registered():
    """Claim de GBP no registrado."""
    return Claim(
        claim_id=uuid4(),
        category="gbp_presence",
        message="GBP no registrado para este hotel",
        confidence=0.85,
        evidence_excerpt="No se encontró perfil en Google Maps",
        metadata={"source": "validation"}
    )


@pytest.fixture
def sample_performance_critical():
    """Claim de performance con severidad crítica."""
    return Claim(
        claim_id=uuid4(),
        category="performance_speed",
        message="Performance crítico - LCP > 4s",
        confidence=0.88,
        evidence_excerpt="Largest Contentful Paint: 4.5s",
        metadata={"severity": "critical"}
    )


@pytest.fixture
def sample_performance_low():
    """Claim de performance con severidad baja."""
    return Claim(
        claim_id=uuid4(),
        category="performance_speed",
        message="Performance bajo - todas las métricas OK",
        confidence=0.90,
        evidence_excerpt="LCP: 1.2s, FID: 15ms, CLS: 0.05",
        metadata={"severity": "low"}
    )


@pytest.fixture
def sample_low_confidence_important():
    """Claim importante con baja confianza (para SOFT conflict)."""
    return Claim(
        claim_id=uuid4(),
        category="schema_presence",
        message="Schema detectado parcialmente",
        confidence=0.45,
        evidence_excerpt="Solo se encontró Schema básico",
        metadata={"source": "scraping"}
    )


@pytest.fixture
def sample_whatsapp_number_a():
    """Claim de WhatsApp con número específico A."""
    return Claim(
        claim_id=uuid4(),
        category="whatsapp_presence",
        message="WhatsApp detectado: +34 600 123 456",
        confidence=0.92,
        evidence_excerpt="Teléfono: +34 600 123 456",
        metadata={"phone": "+34600123456"}
    )


@pytest.fixture
def sample_whatsapp_number_b():
    """Claim de WhatsApp con número específico B (diferente)."""
    return Claim(
        claim_id=uuid4(),
        category="whatsapp_presence",
        message="WhatsApp detectado: +34 611 987 654",
        confidence=0.88,
        evidence_excerpt="Teléfono: +34 611 987 654",
        metadata={"phone": "+34611987654"}
    )


class TestContradictionEngineHardConflicts:
    """Tests para detección de conflictos HARD."""

    def test_detect_whatsapp_hard_conflict(self, engine, sample_whatsapp_verified, sample_whatsapp_not_visible):
        """Detectar conflicto HARD de WhatsApp: VERIFIED pero no visible."""
        claims = [sample_whatsapp_verified, sample_whatsapp_not_visible]
        conflicts = engine.detect_conflicts(claims)

        # Debe detectar al menos un conflicto HARD
        hard_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.HARD]
        assert len(hard_conflicts) >= 1

        # Verificar que el conflicto es sobre whatsapp_visibility
        whatsapp_conflicts = [c for c in hard_conflicts if c.field == "whatsapp_visibility"]
        assert len(whatsapp_conflicts) >= 1
        assert "VERIFIED" in whatsapp_conflicts[0].description

    def test_detect_schema_hard_conflict(self, engine, sample_schema_present, sample_schema_absent):
        """Detectar conflicto HARD de Schema: presente y ausente simultáneamente."""
        claims = [sample_schema_present, sample_schema_absent]
        conflicts = engine.detect_conflicts(claims)

        hard_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.HARD]
        assert len(hard_conflicts) >= 1

        schema_conflicts = [c for c in hard_conflicts if c.field == "schema_presence"]
        assert len(schema_conflicts) >= 1
        assert "existente" in schema_conflicts[0].description.lower() or "no existente" in schema_conflicts[0].description.lower()

    def test_detect_gbp_hard_conflict(self, engine, sample_gbp_exists, sample_gbp_not_registered):
        """Detectar conflicto HARD de GBP: existe pero no registrado."""
        claims = [sample_gbp_exists, sample_gbp_not_registered]
        conflicts = engine.detect_conflicts(claims)

        hard_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.HARD]
        assert len(hard_conflicts) >= 1

        gbp_conflicts = [c for c in hard_conflicts if c.field == "gbp_registration"]
        assert len(gbp_conflicts) >= 1
        assert "existe" in gbp_conflicts[0].description.lower()

    def test_detect_performance_severity_mismatch(self, engine, sample_performance_critical, sample_performance_low):
        """Detectar mismatch de severidad en performance (critical vs low)."""
        claims = [sample_performance_critical, sample_performance_low]
        conflicts = engine.detect_conflicts(claims)

        hard_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.HARD]
        assert len(hard_conflicts) >= 1

        perf_conflicts = [c for c in hard_conflicts if c.field == "performance_severity"]
        assert len(perf_conflicts) >= 1
        assert "severidad" in perf_conflicts[0].description.lower() or "inconsistente" in perf_conflicts[0].description.lower()


class TestContradictionEngineSoftConflicts:
    """Tests para detección de conflictos SOFT."""

    def test_detect_soft_conflict_low_confidence(self, engine, sample_low_confidence_important):
        """Detectar conflicto SOFT: claim importante con baja confianza."""
        claims = [sample_low_confidence_important]
        conflicts = engine.detect_conflicts(claims)

        soft_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.SOFT]
        assert len(soft_conflicts) >= 1

        low_conf = [c for c in soft_conflicts if "baja confianza" in c.description.lower()]
        assert len(low_conf) >= 1
        # Verificar que el conflicto es sobre el campo correcto
        assert low_conf[0].field == "schema_presence"

    def test_no_conflict_same_claims(self, engine, sample_schema_present):
        """Claims idénticos o consistentes no generan conflicto."""
        # Dos claims iguales sobre Schema presente
        claim_copy = Claim(
            claim_id=uuid4(),
            category=sample_schema_present.category,
            message=sample_schema_present.message,
            confidence=0.91,
            evidence_excerpt="Otra evidencia similar",
            metadata={"source": "validation"}
        )
        claims = [sample_schema_present, claim_copy]
        conflicts = engine.detect_conflicts(claims)

        # No debe haber conflictos para claims consistentes
        hard_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.HARD]
        schema_conflicts = [c for c in hard_conflicts if c.field == "schema_presence"]
        assert len(schema_conflicts) == 0


class TestContradictionEngineReports:
    """Tests para generación de reportes y utilidades."""

    def test_generate_conflict_report(self, engine, sample_whatsapp_verified, sample_whatsapp_not_visible):
        """Generar reporte de conflictos estructurado."""
        claims = [sample_whatsapp_verified, sample_whatsapp_not_visible]
        conflicts = engine.detect_conflicts(claims)
        report = engine.generate_conflict_report(conflicts)

        # Verificar estructura del reporte
        assert "summary" in report
        assert "hard_conflicts" in report
        assert "soft_conflicts" in report
        assert "conflicts_by_field" in report
        assert "recommendations" in report

        # Verificar contenido del summary
        summary = report["summary"]
        assert summary["total_conflicts"] == len(conflicts)
        assert summary["hard_conflicts"] >= 1
        assert summary["can_export"] is False  # Hay conflictos HARD

    def test_has_hard_conflicts_true(self, engine, sample_whatsapp_verified, sample_whatsapp_not_visible):
        """has_hard_conflicts retorna True cuando hay conflictos HARD."""
        claims = [sample_whatsapp_verified, sample_whatsapp_not_visible]
        result = engine.has_hard_conflicts(claims)
        assert result is True

    def test_has_hard_conflicts_false(self, engine, sample_schema_present):
        """has_hard_conflicts retorna False cuando no hay conflictos HARD."""
        claims = [sample_schema_present]
        result = engine.has_hard_conflicts(claims)
        assert result is False


class TestContradictionEngineSpecificCases:
    """Tests para casos específicos de detección."""

    def test_whatsapp_number_mismatch_conflict(self, engine, sample_whatsapp_number_a, sample_whatsapp_number_b):
        """Detectar números de WhatsApp diferentes como conflicto HARD."""
        claims = [sample_whatsapp_number_a, sample_whatsapp_number_b]
        conflicts = engine.detect_conflicts(claims)

        hard_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.HARD]
        number_conflicts = [c for c in hard_conflicts if c.field == "whatsapp_number"]

        assert len(number_conflicts) >= 1
        assert "600123456" in number_conflicts[0].description or "611987654" in number_conflicts[0].description

    def test_detect_all_conflicts_combined(self, engine, 
                                          sample_whatsapp_verified, sample_whatsapp_not_visible,
                                          sample_schema_present, sample_schema_absent,
                                          sample_gbp_exists, sample_gbp_not_registered,
                                          sample_low_confidence_important):
        """Detectar todos los tipos de conflictos en conjunto."""
        claims = [
            sample_whatsapp_verified, sample_whatsapp_not_visible,
            sample_schema_present, sample_schema_absent,
            sample_gbp_exists, sample_gbp_not_registered,
            sample_low_confidence_important
        ]
        conflicts = engine.detect_conflicts(claims)

        # Debe haber conflictos HARD y SOFT
        hard_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.HARD]
        soft_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.SOFT]

        assert len(hard_conflicts) >= 3  # WhatsApp, Schema, GBP
        assert len(soft_conflicts) >= 1  # Low confidence

        # Verificar campos afectados
        fields = set(c.field for c in conflicts)
        assert "whatsapp_visibility" in fields
        assert "schema_presence" in fields
        assert "gbp_registration" in fields

    def test_get_conflicts_by_field(self, engine, 
                                   sample_whatsapp_verified, sample_whatsapp_not_visible,
                                   sample_schema_present, sample_schema_absent):
        """Filtrar conflictos por campo específico."""
        claims = [
            sample_whatsapp_verified, sample_whatsapp_not_visible,
            sample_schema_present, sample_schema_absent
        ]
        all_conflicts = engine.detect_conflicts(claims)

        # Filtrar por campo whatsapp_visibility
        whatsapp_conflicts = engine.get_conflicts_by_field(all_conflicts, "whatsapp_visibility")
        assert len(whatsapp_conflicts) >= 1
        assert all(c.field == "whatsapp_visibility" for c in whatsapp_conflicts)

        # Filtrar por campo schema_presence
        schema_conflicts = engine.get_conflicts_by_field(all_conflicts, "schema_presence")
        assert len(schema_conflicts) >= 1
        assert all(c.field == "schema_presence" for c in schema_conflicts)

        # Filtrar por campo inexistente
        empty_conflicts = engine.get_conflicts_by_field(all_conflicts, "nonexistent_field")
        assert len(empty_conflicts) == 0


class TestContradictionEngineEdgeCases:
    """Tests para casos límite y edge cases."""

    def test_empty_claims_list(self, engine):
        """Lista vacía de claims no genera conflictos."""
        conflicts = engine.detect_conflicts([])
        assert len(conflicts) == 0

    def test_single_claim_no_conflict(self, engine, sample_schema_present):
        """Un solo claim no genera conflictos consigo mismo (excepto auto-conflictos SOFT)."""
        claims = [sample_schema_present]
        conflicts = engine.detect_conflicts(claims)

        # Solo puede haber SOFT conflicts (auto-conflictos de baja confianza)
        hard_conflicts = [c for c in conflicts if c.conflict_type == ConflictType.HARD]
        assert len(hard_conflicts) == 0

    def test_claim_to_dict(self, sample_schema_present):
        """Claim se convierte correctamente a diccionario."""
        data = sample_schema_present.to_dict()
        assert data["category"] == "schema_presence"
        assert data["confidence"] == 0.92
        assert "claim_id" in data
        assert "message" in data

    def test_conflict_to_dict(self, engine, sample_whatsapp_verified, sample_whatsapp_not_visible):
        """Conflict se convierte correctamente a diccionario."""
        claims = [sample_whatsapp_verified, sample_whatsapp_not_visible]
        conflicts = engine.detect_conflicts(claims)

        if conflicts:
            conflict_data = conflicts[0].to_dict()
            assert "conflict_id" in conflict_data
            assert "conflict_type" in conflict_data
            assert "claim_a_id" in conflict_data
            assert "claim_b_id" in conflict_data
            assert "description" in conflict_data
            assert "field" in conflict_data
            assert "resolution_hint" in conflict_data
