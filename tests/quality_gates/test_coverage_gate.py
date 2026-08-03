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

    def test_warning_when_pain_has_status_blocked_not_in_docs(self, orchestrator):
        """
        FASE-C-A (D5): Pain with status=BLOCKED but NOT in any document
        → covered=0, justified=1 → WARNING (not PASSED).
        """
        assessment = make_assessment(
            pain_ledger=[{"pain_id": "no_analytics_configured", "status": "BLOCKED"}],
            diagnostic_pain_ids=[],
            proposal_pain_ids=[],
        )

        result = orchestrator._coverage_gate(assessment)

        assert result.passed is True  # WARNING does not block
        assert result.status == GateStatus.WARNING
        assert result.details["justified"] == 1
        assert result.details["covered"] == 0

    def test_warning_when_pain_mapped_to_service_not_in_docs(self, orchestrator):
        """
        FASE-C-A (D5): Pain with status=MAPPED_TO_SERVICE but NOT in any
        document → covered=0, justified=1 → WARNING.
        """
        assessment = make_assessment(
            pain_ledger=[{"pain_id": "low_ota_divergence", "status": "MAPPED_TO_SERVICE"}],
            diagnostic_pain_ids=[],
            proposal_pain_ids=[],
        )

        result = orchestrator._coverage_gate(assessment)

        assert result.passed is True  # WARNING does not block
        assert result.status == GateStatus.WARNING
        assert result.details["justified"] == 1
        assert result.details["covered"] == 0

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


# =============================================================================
# FASE-5 (DT4-N3): Gate Idempotency Tests
# =============================================================================

class TestGateIdempotency:
    """Verify that publication gates are idempotent and don't mutate input."""

    @pytest.fixture
    def full_assessment(self) -> Dict[str, Any]:
        """Minimal valid assessment for running all gates without failures."""
        return {
            "coherence_score": 0.85,
            "evidence_coverage": 0.96,
            "hard_contradictions": 0,
            "critical_recall": 0.95,
            "financial_data": {
                "occupancy_rate": 75.0,
                "direct_channel_percentage": 30.0,
                "adr_cop": 450000.0,
            },
            "validation_summary": {
                "hard_contradictions_count": 0,
            },
            "pain_ledger": [],
            "diagnostic_pain_ids": [],
            "proposal_pain_ids": [],
            "financial_evidence_tier": "B",
            "generated_assets": [
                {"asset_type": "whatsapp_button", "confidence_score": 0.9},
                {"asset_type": "faq_page", "confidence_score": 0.9},
                {"asset_type": "hotel_schema", "confidence_score": 0.9},
                {"asset_type": "org_schema", "confidence_score": 0.9},
                {"asset_type": "review_plan", "confidence_score": 0.9},
                {"asset_type": "optimization_guide", "confidence_score": 0.9},
                {"asset_type": "monthly_report", "confidence_score": 0.9},
                {"asset_type": "open_graph", "confidence_score": 0.9},
                {"asset_type": "llms_txt", "confidence_score": 0.9},
            ],
        }

    def test_gates_same_result_on_double_execution(self, full_assessment):
        """
        Running gates twice on the same assessment produces identical results.

        This verifies the orchestrator is deterministic and doesn't carry
        internal state between runs that would cause drift.
        """
        import copy

        from modules.quality_gates.publication_gates import run_publication_gates

        assessment = copy.deepcopy(full_assessment)
        results_1 = run_publication_gates(assessment)
        results_2 = run_publication_gates(assessment)

        assert len(results_1) == len(results_2), (
            f"Gate count differs: {len(results_1)} vs {len(results_2)}"
        )
        for r1, r2 in zip(results_1, results_2):
            assert r1.gate_name == r2.gate_name
            assert r1.passed == r2.passed, (
                f"Gate '{r1.gate_name}' passed={r1.passed} first, "
                f"passed={r2.passed} second"
            )
            assert r1.status == r2.status, (
                f"Gate '{r1.gate_name}' status={r1.status} first, "
                f"status={r2.status} second"
            )
            assert r1.value == r2.value, (
                f"Gate '{r1.gate_name}' value={r1.value} first, "
                f"value={r2.value} second"
            )

    def test_assessment_not_mutated_after_gates(self, full_assessment):
        """
        Running gates does not mutate the assessment dictionary.

        The assessment input must be identical before and after gate execution.
        """
        import copy

        from modules.quality_gates.publication_gates import run_publication_gates

        assessment = copy.deepcopy(full_assessment)
        original = copy.deepcopy(assessment)
        run_publication_gates(assessment)

        # Compare field by field for a clear error message
        assert set(assessment.keys()) == set(original.keys()), (
            f"Key set changed: before={sorted(original.keys())}, "
            f"after={sorted(assessment.keys())}"
        )
        for key in original:
            assert assessment[key] == original[key], (
                f"Field '{key}' was mutated by gate execution:\n"
                f"  before: {original[key]}\n"
                f"  after:  {assessment[key]}"
            )

    def test_check_publication_readiness_does_not_re_execute_gates(self, full_assessment):
        """
        check_publication_readiness with pre-computed gate_results does NOT
        re-invoke run_publication_gates internally.
        """
        import copy

        from modules.quality_gates.publication_gates import (
            run_publication_gates,
            check_publication_readiness,
        )

        assessment = copy.deepcopy(full_assessment)

        # Run gates once, capture results
        gate_results = run_publication_gates(assessment)

        # Call readiness with pre-computed results
        readiness = check_publication_readiness(assessment, gate_results)

        # Verify the report uses the same gate_results we provided
        assert readiness["gate_results"] == [r.to_dict() for r in gate_results], (
            "readiness report gate_results differ from pre-computed results"
        )
        assert readiness["summary"]["total_gates"] == len(gate_results)
        assert readiness["ready"] is True  # valid_assessment should pass all gates