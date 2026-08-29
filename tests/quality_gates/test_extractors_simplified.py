"""
tests/quality_gates/test_extractors_simplified.py
NUEVO-8-ASSESSMENT-BUILDER — FASE N8-C

Tests para los 5 extractores simplificados en publication_gates.py.
Cada extractor ahora usa acceso directo en vez de múltiples fallbacks.

FASE N8-C: Simplificar extractores multi-path → acceso directo
"""

import pytest
from typing import Dict, Any, List
from modules.quality_gates.publication_gates import PublicationGatesOrchestrator, PublicationGateConfig


@pytest.fixture
def orchestrator():
    return PublicationGatesOrchestrator(PublicationGateConfig())


# =============================================================================
# T1: 5 extractores simplificados
# =============================================================================

class TestExtractConflicts:
    """T1.1: _extract_conflicts → acceso directo a validation_summary.conflicts"""

    def test_extract_conflicts_direct(self, orchestrator):
        """Acceso directo a validation_summary.conflicts (canonical path)."""
        assessment = {
            "validation_summary": {
                "conflicts": [
                    {"field": "whatsapp", "severity": "HARD"},
                    {"field": "phone", "severity": "SOFT"},
                ]
            }
        }
        result = orchestrator._extract_conflicts(assessment)
        assert len(result) == 2
        assert result[0]["field"] == "whatsapp"

    def test_extract_conflicts_empty(self, orchestrator):
        """validation_summary vacío → []"""
        assessment = {"validation_summary": {}}
        result = orchestrator._extract_conflicts(assessment)
        assert result == []

    def test_extract_conflicts_missing_validation_summary(self, orchestrator):
        """Sin validation_summary → []"""
        assessment = {}
        result = orchestrator._extract_conflicts(assessment)
        assert result == []

    def test_extract_conflicts_non_dict_validation_summary(self, orchestrator):
        """validation_summary no es dict → []"""
        assessment = {"validation_summary": "not-a-dict"}
        result = orchestrator._extract_conflicts(assessment)
        assert result == []


class TestExtractEvidenceCoverage:
    """T1.2: _extract_evidence_coverage → acceso directo a evidence_coverage"""

    def test_extract_evidence_coverage_direct(self, orchestrator):
        """Acceso directo a evidence_coverage (canonical path)."""
        assessment = {"evidence_coverage": 0.97}
        result = orchestrator._extract_evidence_coverage(assessment)
        assert result == 0.97

    def test_extract_evidence_coverage_default(self, orchestrator):
        """Sin evidence_coverage → 0.0"""
        assessment = {}
        result = orchestrator._extract_evidence_coverage(assessment)
        assert result == 0.0

    def test_extract_evidence_coverage_string_convertible(self, orchestrator):
        """evidence_coverage como string convertible → float"""
        assessment = {"evidence_coverage": "0.95"}
        result = orchestrator._extract_evidence_coverage(assessment)
        assert result == 0.95

    def test_extract_evidence_coverage_invalid_type(self, orchestrator):
        """evidence_coverage como lista (invalid) → 0.0"""
        assessment = {"evidence_coverage": ["not", "a", "number"]}
        result = orchestrator._extract_evidence_coverage(assessment)
        assert result == 0.0


class TestExtractFinancialData:
    """T1.3: _extract_financial_data → acceso directo a financial_data"""

    def test_extract_financial_data_direct(self, orchestrator):
        """Acceso directo a financial_data (canonical path)."""
        assessment = {
            "financial_data": {
                "adr_cop": 450000,
                "occupancy_rate": 75.0,
                "direct_channel_percentage": 30.0,
            }
        }
        result = orchestrator._extract_financial_data(assessment)
        assert result["adr_cop"] == 450000
        assert result["occupancy_rate"] == 75.0

    def test_extract_financial_data_empty(self, orchestrator):
        """Sin financial_data → {}"""
        assessment = {}
        result = orchestrator._extract_financial_data(assessment)
        assert result == {}

    def test_extract_financial_data_not_dict(self, orchestrator):
        """financial_data no es dict → {}"""
        assessment = {"financial_data": "not-a-dict"}
        result = orchestrator._extract_financial_data(assessment)
        assert result == {}


class TestExtractCoherenceScore:
    """T1.4: _extract_coherence_score → acceso directo a coherence_score"""

    def test_extract_coherence_score_direct(self, orchestrator):
        """Acceso directo a coherence_score (canonical path)."""
        assessment = {"coherence_score": 0.85}
        result = orchestrator._extract_coherence_score(assessment)
        assert result == 0.85

    def test_extract_coherence_score_missing(self, orchestrator):
        """Sin coherence_score → None (para que el gate lo detecte como BLOCKED)"""
        assessment = {}
        result = orchestrator._extract_coherence_score(assessment)
        assert result is None

    def test_extract_coherence_score_invalid_type(self, orchestrator):
        """coherence_score como string no convertible → None"""
        assessment = {"coherence_score": "not-a-number"}
        result = orchestrator._extract_coherence_score(assessment)
        assert result is None

    def test_extract_coherence_score_zero(self, orchestrator):
        """coherence_score = 0.0 → 0.0 (distinguir de missing)"""
        assessment = {"coherence_score": 0.0}
        result = orchestrator._extract_coherence_score(assessment)
        assert result == 0.0


class TestExtractCriticalRecall:
    """T1.5: _extract_critical_recall → directo + cálculo desde critical_issues"""

    def test_extract_critical_recall_direct_field(self, orchestrator):
        """Direct critical_recall field (preferred path)."""
        assessment = {"critical_recall": 0.95}
        result = orchestrator._extract_critical_recall(assessment)
        assert result == 0.95

    def test_extract_critical_recall_with_critical_issues(self, orchestrator):
        """Sin critical_recall directo pero CON critical_issues → 1.0 (el builder garantiza completeness)"""
        assessment = {"critical_issues": ["issue1", "issue2", "issue3"]}
        result = orchestrator._extract_critical_recall(assessment)
        assert result == 1.0

    def test_extract_critical_recall_no_critical_issues(self, orchestrator):
        """Sin critical_recall y sin critical_issues → None"""
        assessment = {}
        result = orchestrator._extract_critical_recall(assessment)
        assert result is None

    def test_extract_critical_recall_empty_with_audit_present(self, orchestrator):
        """critical_issues vacío + audit ejecutado (audit_schema no vacío) → 1.0 (FASE-SR-H2).

        Lista vacía con audit presente = resultado favorable (0 issues críticos,
        nada que recordar), NO dato ausente. El builder garantiza que audit_schema
        no vacío ⟺ audit ejecutado (assessment_builder.py ~L200-213).
        """
        assessment = {"critical_issues": [], "audit_schema": {"rich_results": {"status": "OK"}}}
        result = orchestrator._extract_critical_recall(assessment)
        assert result == 1.0

    def test_extract_critical_recall_empty_without_audit(self, orchestrator):
        """critical_issues vacío SIN audit (audit_schema vacío) → None (dato ausente).

        L-SR5: sin evidencia de audit la métrica está genuinamente ausente →
        el gate debe BLOCKED real (ciclar o escalar, nunca silenciar).
        """
        assessment = {"critical_issues": [], "audit_schema": {}}
        result = orchestrator._extract_critical_recall(assessment)
        assert result is None

    def test_extract_critical_recall_invalid_type(self, orchestrator):
        """critical_recall como string no convertible → intenta fallback a critical_issues"""
        assessment = {"critical_recall": "invalid", "critical_issues": ["issue1"]}
        result = orchestrator._extract_critical_recall(assessment)
        assert result == 1.0  # fallback a critical_issues = 1.0


# =============================================================================
# T2: Verificación de campos muertos eliminados
# =============================================================================

class TestZombieFieldsEliminated:
    """T2: Verificar que campos zombie ya no están en AssessmentPayload"""

    def test_no_critical_issues_detected_in_builder(self, orchestrator):
        """critical_issues_detected ya no existe (era tautológico con critical_issues)."""
        from modules.assessment_builder import AssessmentBuilder
        builder = AssessmentBuilder()
        assessment = builder.with_core("http://test.com", "Test Hotel").build()
        # critical_issues_detected no está en el dict del builder
        assert "critical_issues_detected" not in assessment

    def test_no_metrics_in_assessment(self, orchestrator):
        """metrics (0 consumidores post-simplificación) → _extract no lo busca."""
        assessment = {"metrics": {"evidence_coverage": 0.99}}
        # El extractor simplificado solo busca evidence_coverage directo
        result = orchestrator._extract_evidence_coverage(assessment)
        # metrics.evidence_coverage ya no es fallback → 0.0
        assert result == 0.0

    def test_no_coherence_report_in_assessment(self, orchestrator):
        """coherence_report (0 consumidores post-simplificación) → _extract no lo busca."""
        assessment = {"coherence_report": {"overall_score": 0.95}}
        result = orchestrator._extract_coherence_score(assessment)
        # coherence_report.overall_score ya no es fallback → None
        assert result is None


# =============================================================================
# T4: Tests de integración con assessment builder
# =============================================================================

class TestExtractorsWithBuilderOutput:
    """T4: Verificar que extractores funcionan con output real del AssessmentBuilder."""

    def test_extractors_work_with_builder_dict(self, orchestrator):
        """Output del AssessmentBuilder → todos los extractores funcionan."""
        from modules.assessment_builder import AssessmentBuilder
        
        # Build assessment dict directly (as the builder produces)
        assessment: Dict[str, Any] = {
            "url": "http://hotel.com",
            "hotel_name": "Hotel Test",
            "hotel_url": "http://hotel.com",
            "validation_summary": {
                "conflicts": [{"field": "whatsapp", "severity": "HARD"}],
            },
            "financial_data": {
                "rooms": 50,
                "adr_cop": 350000,
                "occupancy_rate": 0.70,
                "direct_channel_percentage": 0.25,
            },
            "financial_sources": {},
            "financial_evidence_tier": "C",
            "coherence_score": 0.82,
            "evidence_coverage": 0.95,
            "critical_issues": ["issue1"],
            "pain_ledger": [],
            "diagnostic_pain_ids": [],
            "proposal_pain_ids": [],
            "generated_assets": [],
            "site_presence_report": None,
            "hotel_data": {},
            "audit_schema": {},
            "diagnostico_text": "",
            "propuesta_text": "",
        }
        
        # Todos los extractores deben funcionar sin error
        conflicts = orchestrator._extract_conflicts(assessment)
        assert len(conflicts) == 1
        
        ec = orchestrator._extract_evidence_coverage(assessment)
        assert ec == 0.95
        
        fd = orchestrator._extract_financial_data(assessment)
        assert fd.get("adr_cop") == 350000
        
        cs = orchestrator._extract_coherence_score(assessment)
        assert cs == 0.82
        
        cr = orchestrator._extract_critical_recall(assessment)
        assert cr == 1.0  # tiene critical_issues