"""
Tests for Doc-Audit Consistency Gate (N2 — FASE-C-A, contract updated FASE-G G1/NR1).

FASE-G (G1/NR1) contract changes vs the legacy WARNING mode (DEC-C1):
- A confirmed doc-vs-audit contradiction is FAILED (blocking — the gate is in
  BLOCKING_GATE_NAMES since FASE-D), not WARNING.
- Missing diagnostico_text or missing audit_data → NOT_EVALUATED (A1:
  skipped ≠ passed). The gate no longer passes green on data absence —
  in the SalentoReal 2026-08-31 run the gate reported "No audit data
  available" PASSED with value=None while audit_report existed on disk.
- gbp.reviews is accepted as int (real audits: SalentoReal has 986), not
  only as {"total": N}.

Both directions tested: doc claims X → audit contradicts; doc cites N
reviews → audit gbp.reviews int mismatches.
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
# Contradiction → FAILED (blocking, FASE-G G1)
# =============================================================================

class TestContradictionsBlocking:
    def test_og_contradiction_detected(self, orchestrator):
        """
        Doc says 'Sin Open Graph' but audit shows open_graph=True
        → FAILED with the contradiction (blocking since FASE-D).
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

        assert result.passed is False
        assert result.status == GateStatus.FAILED
        assert result.value == 1  # 1 contradiction
        contradictions = result.details["contradictions"]
        assert len(contradictions) == 1
        assert contradictions[0]["pattern_id"] == "og_missing_vs_present"
        assert "sin open graph" in contradictions[0]["doc_keyword"]

    def test_performance_error_vs_new_site(self, orchestrator):
        """
        Doc says 'sitio nuevo o tráfico bajo' but performance status=ERROR
        → FAILED.
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

        assert result.passed is False
        assert result.status == GateStatus.FAILED
        contradictions = result.details["contradictions"]
        assert any(
            c["pattern_id"] == "performance_error_vs_new_site" for c in contradictions
        )

    def test_reviews_mismatch_int_986(self, orchestrator):
        """
        Doc cites '203 reseñas' but gbp.reviews is a plain int (SalentoReal:
        986) → FAILED. FASE-G: int is accepted, not only {"total": N}.
        """
        assessment = make_assessment_with_audit(
            diag_text=(
                "## Reseñas\n\n"
                "El hotel cuenta con 203 reseñas en Google, "
                "con una calificación promedio de 4.2 estrellas."
            ),
            audit_data={
                "gbp": {"reviews": 986},
            },
        )

        result = orchestrator._doc_audit_consistency_gate(assessment)

        assert result.passed is False
        assert result.status == GateStatus.FAILED
        contradictions = result.details["contradictions"]
        assert any(c["pattern_id"] == "reviews_mismatch" for c in contradictions)
        assert any(c["audit_value"] == "986" for c in contradictions)

    def test_reviews_mismatch_dict_total_still_works(self, orchestrator):
        """Legacy shape {"total": N} keeps working (no-regression)."""
        assessment = make_assessment_with_audit(
            diag_text="El hotel cuenta con 203 reseñas en Google.",
            audit_data={
                "gbp": {"reviews": {"total": 50, "average_rating": 4.2}},
            },
        )

        result = orchestrator._doc_audit_consistency_gate(assessment)

        assert result.passed is False
        assert any(c["pattern_id"] == "reviews_mismatch" for c in result.details["contradictions"])

    def test_reviews_match_int_no_contradiction(self, orchestrator):
        """Doc cites the same count as gbp.reviews int → no contradiction."""
        assessment = make_assessment_with_audit(
            diag_text="El hotel cuenta con 986 reseñas en Google.",
            audit_data={"gbp": {"reviews": 986}},
        )

        result = orchestrator._doc_audit_consistency_gate(assessment)

        assert result.passed is True
        assert result.status == GateStatus.PASSED

    def test_photos_mismatch_detected(self, orchestrator):
        """
        Doc targets 40 photos but audit shows only 5
        → FAILED.
        """
        assessment = make_assessment_with_audit(
            diag_text="El hotel debería subir al menos 40 fotos adicionales.",
            audit_data={
                "photos": {"count": 5},
            },
            diagnostic_evidence={"target_photos": 40},
        )

        result = orchestrator._doc_audit_consistency_gate(assessment)

        assert result.passed is False
        assert result.status == GateStatus.FAILED
        contradictions = result.details["contradictions"]
        assert any(c["pattern_id"] == "photos_mismatch" for c in contradictions)

    def test_multiple_contradictions_reported(self, orchestrator):
        """
        Multiple contradictions in the same doc → all reported, FAILED.
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
                "gbp": {"reviews": 30},
            },
        )

        result = orchestrator._doc_audit_consistency_gate(assessment)

        assert result.status == GateStatus.FAILED
        assert result.value >= 2  # At least OG + performance + reviews
        assert len(result.details["contradictions"]) >= 2

    def test_contradiction_blocks_publication(self, orchestrator):
        """FAILED (not WARNING) blocks publication readiness."""
        assessment = make_assessment_with_audit(
            diag_text="El sitio presenta Sin Open Graph Tags incompletos.",
            audit_data={
                "seo_elements": {"open_graph": True},
            },
        )

        result = orchestrator._doc_audit_consistency_gate(assessment)
        assert result.status == GateStatus.FAILED

        results = [result]
        assert orchestrator.is_ready_for_publication(results) is False


# =============================================================================
# Datos ausentes → NOT_EVALUATED (A1: skipped ≠ passed)
# =============================================================================

class TestDatosAusentes:
    def test_no_diagnostic_text_not_evaluated(self, orchestrator):
        """Sin diagnostico_text el check no corrió → NOT_EVALUATED (no PASSED)."""
        assessment = make_assessment_with_audit(
            diag_text="",
            audit_data={"seo_elements": {"open_graph": True}},
        )

        result = orchestrator._doc_audit_consistency_gate(assessment)

        assert result.passed is False
        assert result.status == GateStatus.NOT_EVALUATED
        assert result.details["state_reason"] == "missing_diagnostico_text"

    def test_no_audit_data_not_evaluated(self, orchestrator):
        """Sin audit_data → NOT_EVALUATED. En la corrida SalentoReal
        2026-08-31 esto pasaba en verde con value=None (audit_report existía
        en disco) — ese es el defecto NR1 que G1 cierra."""
        assessment = make_assessment_with_audit(
            diag_text="Sin Open Graph Tags detectados.",
            audit_data={},
        )

        result = orchestrator._doc_audit_consistency_gate(assessment)

        assert result.passed is False
        assert result.status == GateStatus.NOT_EVALUATED
        assert result.details["state_reason"] == "missing_audit_data"
        assert result.value is None

    def test_not_evaluated_does_not_block_publication(self, orchestrator):
        """NOT_EVALUATED es visible pero no bloquea (coherente con A1)."""
        assessment = make_assessment_with_audit(
            diag_text="Sin Open Graph Tags detectados.",
            audit_data={},
        )

        result = orchestrator._doc_audit_consistency_gate(assessment)
        assert result.status == GateStatus.NOT_EVALUATED

        assert orchestrator.is_ready_for_publication([result]) is True


# =============================================================================
# Consistencia real → PASSED
# =============================================================================

class TestConsistenciaReal:
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
