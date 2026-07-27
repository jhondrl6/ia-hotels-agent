"""
Tests for Coverage Gate.

FASE-0C: Valida que ninguna brecha (pain_id) detectada desaparezca
sin explicacion — debe aparecer en diagnostico, propuesta, o estar
justificada (JUSTIFIED_SKIP | BLOCKED | MAPPED_TO_SERVICE).

Regla: brechas_en_diagnostico + brechas_justificadas == brechas_detectadas
"""

import pytest
from dataclasses import dataclass
from typing import List, Set, Dict, Any

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


def make_assessment(
    pain_ledger: List[Dict[str, str]],
    diagnostic_pain_ids: List[str],
    proposal_pain_ids: List[str],
) -> Dict[str, Any]:
    """Build an assessment dict for coverage gate testing."""
    return {
        "pain_ledger": pain_ledger,
        "diagnostic_pain_ids": diagnostic_pain_ids,
        "proposal_pain_ids": proposal_pain_ids,
    }


# =============================================================================
# Test Class: Coverage Gate
# =============================================================================

class TestCoverageGate:
    """Test cases for _coverage_gate()."""

    def test_fails_when_pain_detected_not_in_diagnostic_nor_justified(self, orchestrator):
        """
        Pain detectado que NO aparece en diagnostico NI propuesta NI
        tiene status justificable → coverage gate FAIL.

        Escenario: pain_id='no_whatsapp_visible' detectado pero:
        - No esta en diagnostic_pain_ids
        - No esta en proposal_pain_ids
        - Status='DETECTED' (no justificable)
        """
        assessment = make_assessment(
            pain_ledger=[{"pain_id": "no_whatsapp_visible", "status": "DETECTED"}],
            diagnostic_pain_ids=[],
            proposal_pain_ids=[],
        )

        result = orchestrator._coverage_gate(assessment)

        assert result.passed is False
        assert result.status == GateStatus.FAILED
        assert "no_whatsapp_visible" in result.message
        assert result.gate_name == "coverage_no_silent_drop"
        assert result.details["uncovered"] == ["no_whatsapp_visible"]

    def test_passes_when_pain_in_diagnostic(self, orchestrator):
        """Pain en diagnostico → PASS."""
        assessment = make_assessment(
            pain_ledger=[{"pain_id": "no_whatsapp_visible", "status": "DETECTED"}],
            diagnostic_pain_ids=["no_whatsapp_visible"],
            proposal_pain_ids=[],
        )

        result = orchestrator._coverage_gate(assessment)

        assert result.passed is True
        assert result.status == GateStatus.PASSED

    def test_passes_when_pain_in_proposal(self, orchestrator):
        """Pain no en diagnostico pero SI en propuesta → PASS."""
        assessment = make_assessment(
            pain_ledger=[{"pain_id": "no_hotel_schema", "status": "DETECTED"}],
            diagnostic_pain_ids=[],
            proposal_pain_ids=["no_hotel_schema"],
        )

        result = orchestrator._coverage_gate(assessment)

        assert result.passed is True
        assert result.status == GateStatus.PASSED

    def test_passes_when_pain_grouped_with_explicit_justification(self, orchestrator):
        """
        Pain detectado con status=JUSTIFIED_SKIP → coverage gate PASS.

        Escenario: pain_id='missing_alt_text' detectado y justificado como
        'no aplica para este tipo de hotel'.
        """
        assessment = make_assessment(
            pain_ledger=[{"pain_id": "missing_alt_text", "status": "JUSTIFIED_SKIP"}],
            diagnostic_pain_ids=["missing_alt_text"],  # aparece en diagnostico
            proposal_pain_ids=[],
        )

        result = orchestrator._coverage_gate(assessment)

        assert result.passed is True
        assert result.status == GateStatus.PASSED

    def test_passes_when_pain_has_status_blocked(self, orchestrator):
        """Pain con status=BLOCKED → PASS (bloqueado por falta de datos)."""
        assessment = make_assessment(
            pain_ledger=[{"pain_id": "no_analytics_configured", "status": "BLOCKED"}],
            diagnostic_pain_ids=[],
            proposal_pain_ids=[],
        )

        result = orchestrator._coverage_gate(assessment)

        assert result.passed is True
        assert result.status == GateStatus.PASSED
        assert result.details["justified"] == 1

    def test_passes_when_pain_has_status_mapped_to_service(self, orchestrator):
        """Pain con status=MAPPED_TO_SERVICE → PASS (ya tiene solucion)."""
        assessment = make_assessment(
            pain_ledger=[{"pain_id": "low_ota_divergence", "status": "MAPPED_TO_SERVICE"}],
            diagnostic_pain_ids=[],
            proposal_pain_ids=[],
        )

        result = orchestrator._coverage_gate(assessment)

        assert result.passed is True
        assert result.status == GateStatus.PASSED
        assert result.details["justified"] == 1

    def test_passes_with_fixture_representative(self, orchestrator):
        """
        Mix representativo — 3 pains, todos cubiertos o justificados.

        Escenario:
        - pain_A: en diagnostico → OK
        - pain_B: no en diagnostico, pero en propuesta → OK
        - pain_C: no en diagnostico ni propuesta, pero status=BLOCKED → OK
        """
        assessment = make_assessment(
            pain_ledger=[
                {"pain_id": "no_whatsapp_visible", "status": "DETECTED"},
                {"pain_id": "low_gbp_score", "status": "DETECTED"},
                {"pain_id": "no_faq_schema", "status": "BLOCKED"},
            ],
            diagnostic_pain_ids=["no_whatsapp_visible"],
            proposal_pain_ids=["low_gbp_score"],
        )

        result = orchestrator._coverage_gate(assessment)

        assert result.passed is True
        assert result.status == GateStatus.PASSED
        assert result.details["covered"] == 2  # no_whatsapp_visible + low_gbp_score
        assert result.details["justified"] == 1  # no_faq_schema

    def test_empty_pain_ledger_passes(self, orchestrator):
        """Ledger vacio → no hay brechas, coverage PASS."""
        assessment = make_assessment(
            pain_ledger=[],
            diagnostic_pain_ids=[],
            proposal_pain_ids=[],
        )

        result = orchestrator._coverage_gate(assessment)

        assert result.passed is True
        assert result.status == GateStatus.PASSED
        assert result.value == 1.0

    def test_partial_coverage_still_fails(self, orchestrator):
        """
        Mix: 2 pains cubiertos, 1 sin cobertura → FAIL.

        - pain_A: en diagnostico → OK
        - pain_B: en propuesta → OK
        - pain_C: sin diagnostico ni propuesta y status=DETECTED → FAIL
        """
        assessment = make_assessment(
            pain_ledger=[
                {"pain_id": "no_whatsapp_visible", "status": "DETECTED"},
                {"pain_id": "low_gbp_score", "status": "DETECTED"},
                {"pain_id": "missing_reviews", "status": "DETECTED"},
            ],
            diagnostic_pain_ids=["no_whatsapp_visible"],
            proposal_pain_ids=["low_gbp_score"],
        )

        result = orchestrator._coverage_gate(assessment)

        assert result.passed is False
        assert result.status == GateStatus.FAILED
        assert "missing_reviews" in result.message
        assert result.details["uncovered"] == ["missing_reviews"]

    def test_blocked_when_painLedger_missing(self, orchestrator):
        """Assessment sin pain_ledger → BLOCKED (pipeline incompleto)."""
        assessment: Dict[str, Any] = {
            "diagnostic_pain_ids": ["no_whatsapp_visible"],
            "proposal_pain_ids": [],
            # no pain_ledger key — indica pipeline sin populate
        }

        result = orchestrator._coverage_gate(assessment)

        assert result.passed is False
        assert result.status == GateStatus.BLOCKED
        assert "pain_ledger not found" in result.message

    def test_blocked_when_painLedger_not_list(self, orchestrator):
        """Assessment con pain_ledger no-valido (no es lista) → BLOCKED."""
        assessment = {
            "pain_ledger": "not-a-list",
            "diagnostic_pain_ids": [],
            "proposal_pain_ids": [],
        }

        result = orchestrator._coverage_gate(assessment)

        assert result.passed is False
        assert result.status == GateStatus.BLOCKED