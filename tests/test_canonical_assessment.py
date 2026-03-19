"""Tests para CanonicalAssessment - Sprint 1.

Valida la estructura canónica de análisis de hotel y sus métodos de filtrado.
"""
import sys
from pathlib import Path

# Add project root to Python path for pytest
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from datetime import datetime
from uuid import UUID
from typing import Dict, Any

from data_models.canonical_assessment import (
    CanonicalAssessment,
    SiteMetadata,
    SchemaAnalysis,
    PerformanceAnalysis,
    PerformanceMetrics,
    Claim,
)
from enums.severity import Severity


@pytest.fixture
def site_metadata():
    """Fixture con metadatos de sitio válidos."""
    return SiteMetadata(
        title="Hotel Vísperas | Hotel Boutique en Oaxaca",
        description="Hotel boutique en el centro histórico de Oaxaca",
        cms_detected="wordpress",
        has_default_title=False,
        detected_language="es",
        viewport_meta=True
    )


@pytest.fixture
def schema_analysis():
    """Fixture con análisis de schema."""
    return SchemaAnalysis(
        schema_type="Hotel",
        coverage_score=0.75,
        missing_critical_fields=["aggregateRating"],
        present_fields=["name", "address", "@type", "image", "geo"],
        raw_schema={"@type": "Hotel", "name": "Hotel Vísperas"},
        has_hotel_schema=True,
        has_local_business=False
    )


@pytest.fixture
def performance_analysis():
    """Fixture con análisis de performance."""
    return PerformanceAnalysis(
        performance_score=65,
        accessibility_score=80,
        metrics=PerformanceMetrics(
            lcp=3.2,
            fcp=2.0,
            cls=0.15,
            ttfb=800
        ),
        severity=Severity.HIGH,
        has_critical_issues=True
    )


@pytest.fixture
def sample_claims():
    """Fixture con claims de ejemplo."""
    return [
        Claim(
            source_id="metadata_validator",
            evidence_excerpt="My WordPress Blog",
            severity=Severity.CRITICAL,
            category="metadata",
            message="Título contiene string por defecto",
            confidence=0.95,
            field_path="title"
        ),
        Claim(
            source_id="schema_validator",
            evidence_excerpt="aggregateRating",
            severity=Severity.HIGH,
            category="schema",
            message="Falta campo crítico aggregateRating",
            confidence=0.9,
            field_path="aggregateRating"
        ),
        Claim(
            source_id="performance_auditor",
            evidence_excerpt="LCP 3.2s",
            severity=Severity.MEDIUM,
            category="performance",
            message="LCP excede umbral recomendado",
            confidence=0.95,
            field_path="metrics.lcp"
        ),
        Claim(
            source_id="gbp_auditor",
            evidence_excerpt="4.5 estrellas",
            severity=Severity.LOW,
            category="gbp",
            message="Perfil GBP bien configurado",
            confidence=0.9,
            field_path=None
        )
    ]


class TestCanonicalAssessmentCreation:
    """Tests para creación de CanonicalAssessment."""

    def test_canonical_assessment_creation(self, site_metadata, schema_analysis, performance_analysis):
        """Crea assessment válido con todos los campos requeridos."""
        assessment = CanonicalAssessment(
            url="https://hotelvisperas.com",
            site_metadata=site_metadata,
            schema_analysis=schema_analysis,
            performance_analysis=performance_analysis,
            coherence_score=0.85,
            evidence_coverage=0.9,
            hard_contradictions=0
        )
        
        assert assessment.url == "https://hotelvisperas.com"
        assert assessment.site_metadata.title == "Hotel Vísperas | Hotel Boutique en Oaxaca"
        assert assessment.schema_analysis.schema_type == "Hotel"
        assert assessment.performance_analysis.performance_score == 65
        assert assessment.coherence_score == 0.85
        assert assessment.evidence_coverage == 0.9
        assert assessment.hard_contradictions == 0
        assert assessment.version == "1.0.0"

    def test_assessment_has_uuid(self, site_metadata, schema_analysis, performance_analysis):
        """Assessment genera UUID automáticamente."""
        assessment = CanonicalAssessment(
            url="https://hotel.com",
            site_metadata=site_metadata,
            schema_analysis=schema_analysis,
            performance_analysis=performance_analysis
        )
        
        assert isinstance(assessment.assessment_id, UUID)

    def test_assessment_has_timestamp(self, site_metadata, schema_analysis, performance_analysis):
        """Assessment tiene timestamp de creación."""
        before = datetime.utcnow()
        assessment = CanonicalAssessment(
            url="https://hotel.com",
            site_metadata=site_metadata,
            schema_analysis=schema_analysis,
            performance_analysis=performance_analysis
        )
        after = datetime.utcnow()
        
        assert before <= assessment.analyzed_at <= after


class TestGetCriticalClaims:
    """Tests para filtrado de claims críticos."""

    def test_get_critical_claims(self, site_metadata, schema_analysis, performance_analysis, sample_claims):
        """Filtra solo claims CRITICAL y HIGH."""
        assessment = CanonicalAssessment(
            url="https://hotel.com",
            site_metadata=site_metadata,
            schema_analysis=schema_analysis,
            performance_analysis=performance_analysis,
            claims=sample_claims
        )
        
        critical_claims = assessment.get_critical_claims()
        
        assert len(critical_claims) == 2
        assert all(c.severity in (Severity.CRITICAL, Severity.HIGH) for c in critical_claims)
        assert any(c.severity == Severity.CRITICAL for c in critical_claims)
        assert any(c.severity == Severity.HIGH for c in critical_claims)

    def test_get_critical_claims_no_matches(self, site_metadata, schema_analysis, performance_analysis):
        """Retorna lista vacía si no hay claims críticos."""
        low_claims = [
            Claim(
                source_id="test",
                evidence_excerpt="test",
                severity=Severity.LOW,
                category="test",
                message="test",
                confidence=0.5
            )
        ]
        assessment = CanonicalAssessment(
            url="https://hotel.com",
            site_metadata=site_metadata,
            schema_analysis=schema_analysis,
            performance_analysis=performance_analysis,
            claims=low_claims
        )
        
        critical_claims = assessment.get_critical_claims()
        assert len(critical_claims) == 0


class TestEvidenceCoverageCalculation:
    """Tests para cálculo de cobertura de evidencia."""

    def test_evidence_coverage_calculation(self, site_metadata, schema_analysis, performance_analysis):
        """Calcula % correctamente después de agregar claims."""
        assessment = CanonicalAssessment(
            url="https://hotel.com",
            site_metadata=site_metadata,
            schema_analysis=schema_analysis,
            performance_analysis=performance_analysis,
            claims=[]
        )
        
        # Agregar claims con source_id (tienen evidencia)
        assessment.add_claim(Claim(
            source_id="validator1",
            evidence_excerpt="evidence1",
            severity=Severity.HIGH,
            category="metadata",
            message="test",
            confidence=0.9
        ))
        assessment.add_claim(Claim(
            source_id="validator2",
            evidence_excerpt="evidence2",
            severity=Severity.MEDIUM,
            category="schema",
            message="test",
            confidence=0.8
        ))
        
        # Ambos claims tienen source_id, coverage = 100%
        assert assessment.evidence_coverage == 1.0

    def test_evidence_coverage_partial(self, site_metadata, schema_analysis, performance_analysis):
        """Calcula coverage parcial correctamente."""
        assessment = CanonicalAssessment(
            url="https://hotel.com",
            site_metadata=site_metadata,
            schema_analysis=schema_analysis,
            performance_analysis=performance_analysis,
            claims=[]
        )
        
        # Claim con evidencia
        claim_with_evidence = Claim(
            source_id="validator",
            evidence_excerpt="evidence",
            severity=Severity.HIGH,
            category="metadata",
            message="test",
            confidence=0.9
        )
        
        assessment.add_claim(claim_with_evidence)
        
        # Con 1 claim que tiene source_id, coverage = 1.0
        assert assessment.evidence_coverage == 1.0


class TestSerializationRoundtrip:
    """Tests para serialización y deserialización."""

    def test_serialization_roundtrip(self, site_metadata, schema_analysis, performance_analysis, sample_claims):
        """Dict → Object → Dict preserva datos."""
        original = CanonicalAssessment(
            url="https://hotelvisperas.com",
            site_metadata=site_metadata,
            schema_analysis=schema_analysis,
            performance_analysis=performance_analysis,
            claims=sample_claims,
            coherence_score=0.85,
            evidence_coverage=0.9,
            hard_contradictions=1
        )
        
        # Serializar a dict
        data = original.to_dict()
        
        # Deserializar de dict
        restored = CanonicalAssessment.from_dict(data)
        
        # Verificar que los datos se preservaron
        assert restored.url == original.url
        assert restored.version == original.version
        assert restored.coherence_score == original.coherence_score
        assert restored.evidence_coverage == original.evidence_coverage
        assert restored.hard_contradictions == original.hard_contradictions
        
        # Verificar nested objects
        assert restored.site_metadata.title == original.site_metadata.title
        assert restored.schema_analysis.schema_type == original.schema_analysis.schema_type
        assert restored.performance_analysis.performance_score == original.performance_analysis.performance_score
        
        # Verificar claims
        assert len(restored.claims) == len(original.claims)
        assert restored.claims[0].severity == original.claims[0].severity
        assert restored.claims[0].category == original.claims[0].category

    def test_to_dict_excludes_raw_when_requested(self, site_metadata, schema_analysis, performance_analysis):
        """to_dict(include_raw=False) excluye datos crudos."""
        assessment = CanonicalAssessment(
            url="https://hotel.com",
            site_metadata=site_metadata,
            schema_analysis=schema_analysis,
            performance_analysis=performance_analysis
        )
        
        data_with_raw = assessment.to_dict(include_raw=True)
        data_without_raw = assessment.to_dict(include_raw=False)
        
        # Con raw debe incluir raw_schema
        assert "raw_schema" in data_with_raw.get("schema_analysis", {})
        
        # Sin raw debe excluir raw_schema
        assert "raw_schema" not in data_without_raw.get("schema_analysis", {})


class TestClaimFilteringMethods:
    """Tests para métodos de filtrado de claims."""

    def test_get_claims_by_category(self, site_metadata, schema_analysis, performance_analysis, sample_claims):
        """Filtra claims por categoría."""
        assessment = CanonicalAssessment(
            url="https://hotel.com",
            site_metadata=site_metadata,
            schema_analysis=schema_analysis,
            performance_analysis=performance_analysis,
            claims=sample_claims
        )
        
        metadata_claims = assessment.get_claims_by_category("metadata")
        schema_claims = assessment.get_claims_by_category("schema")
        performance_claims = assessment.get_claims_by_category("performance")
        
        assert len(metadata_claims) == 1
        assert metadata_claims[0].category == "metadata"
        assert len(schema_claims) == 1
        assert schema_claims[0].category == "schema"
        assert len(performance_claims) == 1
        assert performance_claims[0].category == "performance"

    def test_get_claims_by_severity(self, site_metadata, schema_analysis, performance_analysis, sample_claims):
        """Filtra claims por severidad."""
        assessment = CanonicalAssessment(
            url="https://hotel.com",
            site_metadata=site_metadata,
            schema_analysis=schema_analysis,
            performance_analysis=performance_analysis,
            claims=sample_claims
        )
        
        critical = assessment.get_claims_by_severity(Severity.CRITICAL)
        high = assessment.get_claims_by_severity(Severity.HIGH)
        medium = assessment.get_claims_by_severity(Severity.MEDIUM)
        low = assessment.get_claims_by_severity(Severity.LOW)
        
        assert len(critical) == 1
        assert len(high) == 1
        assert len(medium) == 1
        assert len(low) == 1

    def test_get_verified_claims(self, site_metadata, schema_analysis, performance_analysis, sample_claims):
        """Retorna solo claims verificados (confianza >= 0.9)."""
        assessment = CanonicalAssessment(
            url="https://hotel.com",
            site_metadata=site_metadata,
            schema_analysis=schema_analysis,
            performance_analysis=performance_analysis,
            claims=sample_claims
        )
        
        verified = assessment.get_verified_claims()
        
        # Solo claims con confidence >= 0.9
        assert all(c.confidence >= 0.9 for c in verified)
        assert len(verified) == 4  # Todos los claims tienen >= 0.9

    def test_get_deployment_blockers(self, site_metadata, schema_analysis, performance_analysis, sample_claims):
        """Retorna claims que bloquean publicación (CRITICAL)."""
        assessment = CanonicalAssessment(
            url="https://hotel.com",
            site_metadata=site_metadata,
            schema_analysis=schema_analysis,
            performance_analysis=performance_analysis,
            claims=sample_claims
        )
        
        blockers = assessment.get_deployment_blockers()
        
        assert len(blockers) == 1
        assert blockers[0].severity == Severity.CRITICAL
        assert blockers[0].blocks_deployment is True

    def test_get_categories(self, site_metadata, schema_analysis, performance_analysis, sample_claims):
        """Retorna todas las categorías únicas."""
        assessment = CanonicalAssessment(
            url="https://hotel.com",
            site_metadata=site_metadata,
            schema_analysis=schema_analysis,
            performance_analysis=performance_analysis,
            claims=sample_claims
        )
        
        categories = assessment.get_categories()
        
        assert categories == {"metadata", "schema", "performance", "gbp"}


class TestSummaryGeneration:
    """Tests para generación de resumen."""

    def test_get_summary(self, site_metadata, schema_analysis, performance_analysis, sample_claims):
        """Genera resumen ejecutivo correctamente."""
        assessment = CanonicalAssessment(
            url="https://hotelvisperas.com",
            site_metadata=site_metadata,
            schema_analysis=schema_analysis,
            performance_analysis=performance_analysis,
            claims=sample_claims,
            coherence_score=0.85,
            evidence_coverage=0.9,
            hard_contradictions=1
        )
        
        summary = assessment.get_summary()
        
        assert summary["url"] == "https://hotelvisperas.com"
        assert summary["version"] == "1.0.0"
        assert summary["total_claims"] == 4
        assert summary["severity_breakdown"]["critical"] == 1
        assert summary["severity_breakdown"]["high"] == 1
        assert summary["severity_breakdown"]["medium"] == 1
        assert summary["severity_breakdown"]["low"] == 1
        assert summary["coherence_score"] == 0.85
        assert summary["evidence_coverage"] == 0.9
        assert summary["hard_contradictions"] == 1
        assert summary["verified_claims"] == 4
        assert summary["deployment_blockers"] == 1
        assert summary["has_gbp_data"] is False
        assert summary["performance_score"] == 65
        assert summary["schema_coverage"] == 0.75
