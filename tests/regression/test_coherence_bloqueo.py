"""Tests de regresion para bloqueo por coherencia."""

import pytest
from data_models.canonical_assessment import (
    CanonicalAssessment, SiteMetadata, SchemaAnalysis, PerformanceAnalysis
)
from commercial_documents.composer import DocumentComposer
from observability.dashboard import QualityDashboard, RunMetrics


def create_test_assessment(coherence=0.0):
    """Helper para crear assessment."""
    return CanonicalAssessment(
        url="https://test-hotel.com",
        site_metadata=SiteMetadata(
            title="Test Hotel",
            description="Test",
            cms_detected="WordPress",
            has_default_title=False,
            detected_language="es",
            viewport_meta=True
        ),
        schema_analysis=SchemaAnalysis(
            schema_type="Hotel",
            coverage_score=0.6,
            has_hotel_schema=True,
            has_local_business=False
        ),
        performance_analysis=PerformanceAnalysis(
            performance_score=75.0
        ),
        coherence_score=coherence,
        evidence_coverage=0.95,
        hard_contradictions=0
    )


class TestCoherenceBloqueo:
    """Tests para verificar bloqueo por baja coherencia."""
    
    def test_coherence_0_8_boundary(self):
        """Verifica limite exacto en 0.8."""
        composer = DocumentComposer()
        
        # Crear assessment con coherence exactamente 0.8
        assessment_80 = create_test_assessment(coherence=0.8)
        doc_80 = composer.compose_diagnostico(assessment_80)
        
        # 0.8 debe pasar
        assert doc_80.publication_status == "READY_FOR_CLIENT"
        
        # 0.79 debe bloquear
        assessment_79 = create_test_assessment(coherence=0.79)
        doc_79 = composer.compose_diagnostico(assessment_79)
        assert doc_79.publication_status == "DRAFT_INTERNAL"
    
    def test_coherence_blocks_publication_when_low(self):
        """Confirma DRAFT_INTERNAL cuando coherence < 0.8."""
        assessment = create_test_assessment(coherence=0.5)
        composer = DocumentComposer()
        doc = composer.compose_diagnostico(assessment)
        
        assert doc.publication_status == "DRAFT_INTERNAL"
    
    def test_coherence_allows_certified_when_high(self):
        """Confirma READY_FOR_CLIENT cuando coherence >= 0.8."""
        assessment = create_test_assessment(coherence=0.85)
        composer = DocumentComposer()
        doc = composer.compose_diagnostico(assessment)
        
        assert doc.publication_status == "READY_FOR_CLIENT"
    
    def test_coherence_trend_detection(self, tmp_path):
        """Detecta degradacion en tendencias."""
        storage_path = tmp_path / "test_trends.jsonl"
        dashboard = QualityDashboard(storage_path=str(storage_path))
        
        # Simular degradacion
        run1 = RunMetrics(
            run_id="run-001",
            hotel_id="test-hotel",
            coherence_score=0.9,
            evidence_coverage=0.95,
            hard_contradictions=0,
            soft_contradictions=0,
            financial_validity=True,
            critical_recall=0.95,
            publication_status="READY_FOR_CLIENT"
        )
        
        run2 = RunMetrics(
            run_id="run-002",
            hotel_id="test-hotel",
            coherence_score=0.7,
            evidence_coverage=0.95,
            hard_contradictions=0,
            soft_contradictions=0,
            financial_validity=True,
            critical_recall=0.95,
            publication_status="DRAFT_INTERNAL"
        )
        
        dashboard.record_run(run1)
        dashboard.record_run(run2)
        
        trends = dashboard.get_trends(days=7, hotel_id="test-hotel")
        assert trends.total_runs == 2
