"""
Tests for Doc-Audit Consistency Gate (N2 — FASE-C-A).

FASE-C-A (N2): Detects contradictions between claims in the generated
diagnostic document and the actual audit data.

Known contradiction patterns:
- audit.seo_elements.open_graph=True → doc cannot say "Sin Open Graph"
- reviews cited in doc vs gbp.reviews.total
- photo target in doc vs audit photos count
- performance.status=ERROR → doc cannot say "sitio nuevo o trafico bajo"

Initial mode: WARNING (DEC-C1) — does not block publication.
"""

import pytest
from typing import Dict, Any

from modules.quality_gates.publication_gates import (
    PublicationGatesOrchestrator,
    PublicationGateConfig,
    GateStatus,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def orchestrator() -> PublicationGatesOrchestrator:
    return PublicationGatesOrchestrator(PublicationGateConfig())


def make_assessment_with_audit(
    diag_text: str,
    audit_data: Dict[str, Any],
    diagnostic_evidence: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Build an assessment dict for doc-audit consistency gate testing."""
    assessment = {
        "diagnostico_text": diag_text,
        "audit_data": audit_data,
    }
    if diagnostic_evidence is not None:
        assessment["diagnostic_evidence"] = diagnostic_evidence
    return assessment


# =============================================================================
# Test Class: Doc-Audit Consistency Gate (N2)
# =============================================================================

class TestDocAuditConsistencyGate:
    """Test cases for _doc_audit_consistency_gate()."""

    def test_og_contradiction_detected(self, orchestrator):
        """
        Doc says 'Sin Open Graph' but audit shows open_graph=True
        → gate reports WARNING with the contradiction.
        """
        assessment = make_assessment_with_audit(
            diag_text=(
                "## Problemas SEO\n\n"
                "El sitio presenta Sin Open Graph Tags, lo que reduce "
                "la visibilidad en redes sociales."
            ),
            audit_data={
                "seo_elements": {
                    "open_graph": True,
                    "twitter_card": False,
                },
            },
        )

        result = orchestrator._doc_audit_consistency_gate(assessment)

        assert result.passed is True  # WARNING does not block (DEC-C1)
        assert result.status == GateStatus.WARNING
        assert result.value == 1  # 1 contradiction
        contradictions = result.details["contradictions"]
        assert len(contradictions) == 1
        assert contradictions[0]["pattern_id"] == "og_missing_vs_present"
        assert "sin open graph" in contradictions[0]["doc_keyword"]

    def test_performance_error_vs_new_site(self, orchestrator):
        """
        Doc says 'sitio nuevo o tráfico bajo' but performance status=ERROR
        → gate reports the contradiction.
        """
        assessment = make_assessment_with_audit(
            diag_text=(
                "## Rendimiento\n\n"
                "Debido a que es un sitio nuevo o trafico bajo, "
                "no se pueden evaluar métricas de rendimiento."
            ),
            audit_data={
                "performance": {
                    "status": "ERROR",
                    "score": None,
                },
            },
        )

        result = orchestrator._doc_audit_consistency_gate(assessment)

        assert result.passed is True
        assert result.status == GateStatus.WARNING
        contradictions = result.details["contradictions"]
        assert any(c["pattern_id"] == "performance_error_vs_new_site" for c in contradictions)

    def test_reviews_mismatch_detected(self, orchestrator):
        """
        Doc cites '203 reseñas' but audit shows 50 reviews
        → gate reports the contradiction.
        """
        assessment = make_assessment_with_audit(
            diag_text=(
                "## Reseñas\n\n"
                "El hotel cuenta con 203 reseñas en Google, "
                "con una calificación promedio de 4.2 estrellas."
            ),
            audit_data={
                "gbp": {
                    "reviews": {
                        "total": 50,
                        "average_rating": 4.2,
                    },
                },
            },
        )

        result = orchestrator._doc_audit_consistency_gate(assessment)

        assert result.passed is True
        assert result.status == GateStatus.WARNING
        contradictions = result.details["contradictions"]
        assert any(c["pattern_id"] == "reviews_mismatch" for c in contradictions)

    def test_photos_mismatch_detected(self, orchestrator):
        """
        Doc targets 40 photos but audit shows only 5
        → gate reports the contradiction.
        """
        assessment = make_assessment_with_audit(
            diag_text="El hotel debería subir al menos 40 fotos adicionales.",
            audit_data={
                "photos": {"count": 5},
            },
            diagnostic_evidence={"target_photos": 40},
        )

        result = orchestrator._doc_audit_consistency_gate(assessment)

        assert result.passed is True
        assert result.status == GateStatus.WARNING
        contradictions = result.details["contradictions"]
        assert any(c["pattern_id"] == "photos_mismatch" for c in contradictions)

    def test_consistent_doc_passes_silently(self, orchestrator):
        """
        Doc is consistent with audit data → gate PASSED, no contradictions.
        """
        assessment = make_assessment_with_audit(
            diag_text=(
                "## Problemas SEO\n\n"
                "El sitio carece de datos estructurados Hotel Schema. "
                "Se recomienda implementar FAQ Page."
            ),
            audit_data={
                "seo_elements": {
                    "open_graph": True,
                    "hotel_schema": False,
                },
                "performance": {
                    "status": "OK",
                    "score": 72,
                },
            },
        )

        result = orchestrator._doc_audit_consistency_gate(assessment)

        assert result.passed is True
        assert result.status == GateStatus.PASSED
        assert result.value == 0
        assert "no contradictions" in result.message.lower()

    def test_no_diagnostic_text_passes(self, orchestrator):
        """
        No diagnostic text available → gate PASSED (nothing to check).
        """
        assessment = make_assessment_with_audit(
            diag_text="",
            audit_data={"seo_elements": {"open_graph": True}},
        )

        result = orchestrator._doc_audit_consistency_gate(assessment)

        assert result.passed is True
        assert result.status == GateStatus.PASSED

    def test_no_audit_data_passes(self, orchestrator):
        """
        No audit data available → gate PASSED (nothing to compare).
        """
        assessment = make_assessment_with_audit(
            diag_text="Sin Open Graph Tags detectados.",
            audit_data={},
        )

        result = orchestrator._doc_audit_consistency_gate(assessment)

        assert result.passed is True
        assert result.status == GateStatus.PASSED

    def test_warning_does_not_block_publication(self, orchestrator):
        """
        WARNING mode (DEC-C1) must not block publication.
        Verify via is_ready_for_publication that WARNING results pass.
        """
        assessment = make_assessment_with_audit(
            diag_text="El sitio presenta Sin Open Graph Tags incompletos.",
            audit_data={
                "seo_elements": {"open_graph": True},
            },
        )

        result = orchestrator._doc_audit_consistency_gate(assessment)
        assert result.status == GateStatus.WARNING

        # WARNING counts as passed for publication readiness
        results = [result]
        assert orchestrator.is_ready_for_publication(results) is True

    def test_multiple_contradictions_reported(self, orchestrator):
        """
        Multiple contradictions in the same doc → all reported.
        """
        assessment = make_assessment_with_audit(
            diag_text=(
                "## Diagnóstico\n\n"
                "Sin Open Graph Tags. Sitio nuevo o trafico bajo. "
                "Cuenta con 500 reseñas en Google."
            ),
            audit_data={
                "seo_elements": {"open_graph": True},
                "performance": {"status": "ERROR", "score": None},
                "gbp": {"reviews": {"total": 30}},
            },
        )

        result = orchestrator._doc_audit_consistency_gate(assessment)

        assert result.status == GateStatus.WARNING
        assert result.value >= 2  # At least OG + performance + reviews
        assert len(result.details["contradictions"]) >= 2
