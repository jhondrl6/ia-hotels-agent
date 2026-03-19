"""
Tests for Publication Gates (Fase 5).

This module tests the 5 critical publication gates that must pass
before any commercial document or asset can be published.

Gates tested:
1. hard_contradictions_gate: Blocks if > 0 HARD conflicts
2. evidence_coverage_gate: Blocks if < 95% coverage
3. financial_validity_gate: Blocks if default values detected
4. coherence_gate: Blocks if < 0.8 coherence score
5. critical_recall_gate: Blocks if < 90% critical recall

Includes specific test case for Hotel Vísperas scenario.
"""

import pytest
from typing import Dict, Any, List

from modules.quality_gates.publication_gates import (
    PublicationGatesOrchestrator,
    PublicationGateResult,
    PublicationGateConfig,
    GateStatus,
    run_publication_gates,
    check_publication_readiness,
)
from modules.financial_engine.no_defaults_validator import (
    NoDefaultsValidator,
    NoDefaultsValidationResult,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def default_config() -> PublicationGateConfig:
    """Default gate configuration."""
    return PublicationGateConfig()


@pytest.fixture
def orchestrator(default_config) -> PublicationGatesOrchestrator:
    """Publication gates orchestrator with default config."""
    return PublicationGatesOrchestrator(default_config)


@pytest.fixture
def valid_assessment() -> Dict[str, Any]:
    """Assessment that passes all gates."""
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
    }


@pytest.fixture
def visperas_assessment() -> Dict[str, Any]:
    """
    Hotel Vísperas assessment data.
    
    This hotel has multiple issues that should result in DRAFT_INTERNAL status:
    - coherence_score: 0.0 (no se pudo calcular)
    - evidence_coverage: 0.2 (20%, muy bajo)
    - hard_contradictions: 3 (conflictos entre web y GBP)
    - critical_recall: 0.5 (50%, muy bajo)
    - financial: valores por defecto (0)
    """
    return {
        "coherence_score": 0.0,
        "evidence_coverage": 0.2,
        "hard_contradictions": 3,
        "critical_recall": 0.5,
        "financial": {
            "inputs": {"rooms": 0, "adr": 0, "occupancy": 0},
            "validation": {"validated": False}
        },
        "financial_data": {
            "occupancy_rate": 0,
            "direct_channel_percentage": 0,
            "adr_cop": 0,
        },
        "validation_summary": {
            "hard_contradictions_count": 3,
            "conflicts": [
                {
                    "field": "whatsapp",
                    "severity": "HARD",
                    "web_value": "+57 300 1234567",
                    "gbp_value": "+57 300 7654321",
                    "message": "WhatsApp diferente entre web y GBP"
                },
                {
                    "field": "address",
                    "severity": "HARD",
                    "web_value": "Calle 123 #45-67",
                    "gbp_value": "Carrera 45 #67-89",
                    "message": "Dirección diferente entre web y GBP"
                },
                {
                    "field": "phone",
                    "severity": "HARD",
                    "web_value": "+57 1 2345678",
                    "gbp_value": "+57 1 8765432",
                    "message": "Teléfono diferente entre web y GBP"
                },
            ]
        },
        "conflicts": [
            {"field": "whatsapp", "severity": "HARD", "type": "HARD"},
            {"field": "address", "severity": "HARD", "type": "HARD"},
            {"field": "phone", "severity": "HARD", "type": "HARD"},
        ]
    }


# =============================================================================
# Test Class 1: TestHardContradictionsGate
# =============================================================================

class TestHardContradictionsGate:
    """Tests for the hard contradictions publication gate."""

    def test_no_hard_contradictions_passes(self, orchestrator):
        """
        Test that gate passes when there are 0 hard contradictions.
        
        Expected: PASSED status, passed=True
        """
        assessment = {
            "hard_contradictions": 0,
            "validation_summary": {"hard_contradictions_count": 0},
            "conflicts": []
        }
        
        result = orchestrator._hard_contradictions_gate(assessment)
        
        assert result.passed is True
        assert result.status == GateStatus.PASSED
        assert result.value == 0
        assert "No hard contradictions" in result.message

    def test_hard_contradictions_blocks(self, orchestrator):
        """
        Test that gate blocks when there are > 0 hard contradictions.
        
        Expected: BLOCKED status, passed=False
        """
        assessment = {
            "hard_contradictions": 3,
            "validation_summary": {"hard_contradictions_count": 3},
            "conflicts": [
                {"field": "whatsapp", "severity": "HARD", "type": "HARD"},
                {"field": "address", "severity": "HARD", "type": "HARD"},
                {"field": "phone", "severity": "HARD", "type": "HARD"},
            ]
        }
        
        result = orchestrator._hard_contradictions_gate(assessment)
        
        assert result.passed is False
        assert result.status == GateStatus.BLOCKED
        assert result.value == 3
        assert "3 hard contradiction" in result.message
        assert "Resolve all HARD conflicts" in result.suggestion

    def test_single_hard_contradiction_blocks(self, orchestrator):
        """
        Test that even 1 hard contradiction blocks publication.
        
        Threshold is 0, so any hard contradiction blocks.
        """
        assessment = {
            "validation_summary": {"hard_contradictions_count": 1},
            "conflicts": [{"field": "email", "severity": "HARD"}]
        }
        
        result = orchestrator._hard_contradictions_gate(assessment)
        
        assert result.passed is False
        assert result.status == GateStatus.BLOCKED
        assert result.value == 1


# =============================================================================
# Test Class 2: TestEvidenceCoverageGate
# =============================================================================

class TestEvidenceCoverageGate:
    """Tests for the evidence coverage publication gate."""

    def test_high_coverage_passes(self, orchestrator):
        """
        Test that gate passes when evidence coverage >= 95%.
        
        Expected: PASSED status, passed=True
        """
        assessment = {
            "evidence_coverage": 0.96,
            "metrics": {"evidence_coverage": 0.96}
        }
        
        result = orchestrator._evidence_coverage_gate(assessment)
        
        assert result.passed is True
        assert result.status == GateStatus.PASSED
        assert result.value == 0.96
        assert "96.0%" in result.message

    def test_exact_threshold_passes(self, orchestrator):
        """
        Test that gate passes at exactly 95% threshold.
        
        Boundary condition test.
        """
        assessment = {
            "evidence_coverage": 0.95,
            "metrics": {"evidence_coverage": 0.95}
        }
        
        result = orchestrator._evidence_coverage_gate(assessment)
        
        assert result.passed is True
        assert result.status == GateStatus.PASSED

    def test_low_coverage_blocks(self, orchestrator):
        """
        Test that gate blocks when evidence coverage < 95%.
        
        Expected: BLOCKED status, passed=False
        """
        assessment = {
            "evidence_coverage": 0.85,
            "metrics": {"evidence_coverage": 0.85}
        }
        
        result = orchestrator._evidence_coverage_gate(assessment)
        
        assert result.passed is False
        assert result.status == GateStatus.BLOCKED
        assert result.value == 0.85
        assert "85.0%" in result.message
        assert "below threshold" in result.message
        assert "Add evidence excerpts" in result.suggestion

    def test_coverage_from_claims_calculation(self, orchestrator):
        """
        Test that coverage is calculated from claims if not provided directly.
        """
        assessment = {
            "claims": [
                {"text": "Claim 1", "evidence_excerpt": "Evidence 1"},
                {"text": "Claim 2", "evidence_excerpt": "Evidence 2"},
                {"text": "Claim 3", "evidence_excerpt": None},
                {"text": "Claim 4"},  # No evidence_excerpt key
            ]
        }
        
        result = orchestrator._evidence_coverage_gate(assessment)
        
        # 2 out of 4 have evidence = 50%
        assert result.value == 0.5
        assert result.passed is False  # 50% < 95%


# =============================================================================
# Test Class 3: TestFinancialValidityGate
# =============================================================================

class TestFinancialValidityGate:
    """Tests for the financial validity publication gate."""

    def test_valid_financial_passes(self, orchestrator):
        """
        Test that gate passes with valid financial data (no defaults).
        
        Expected: PASSED status, passed=True
        """
        assessment = {
            "financial_data": {
                "occupancy_rate": 75.0,
                "direct_channel_percentage": 30.0,
                "adr_cop": 450000.0,
            }
        }
        
        result = orchestrator._financial_validity_gate(assessment)
        
        assert result.passed is True
        assert result.status == GateStatus.PASSED
        assert "no default values detected" in result.message

    def test_default_values_blocks(self, orchestrator):
        """
        Test that gate blocks when financial data has default values.
        
        Expected: BLOCKED status, passed=False
        """
        assessment = {
            "financial_data": {
                "occupancy_rate": 0,
                "direct_channel_percentage": 30.0,
                "adr_cop": 450000.0,
            }
        }
        
        result = orchestrator._financial_validity_gate(assessment)
        
        assert result.passed is False
        assert result.status == GateStatus.BLOCKED
        assert "default values" in result.message
        assert "occupancy_rate" in result.message

    def test_multiple_default_values_blocks(self, orchestrator):
        """
        Test that gate blocks when multiple fields have defaults.
        """
        assessment = {
            "financial_data": {
                "occupancy_rate": 0,
                "direct_channel_percentage": 0,
                "adr_cop": 0,
            }
        }
        
        result = orchestrator._financial_validity_gate(assessment)
        
        assert result.passed is False
        assert result.status == GateStatus.BLOCKED
        assert "occupancy_rate" in result.message
        assert "direct_channel" in result.message or "adr_cop" in result.message

    def test_none_values_blocks(self, orchestrator):
        """
        Test that None values are treated as defaults and block.
        """
        assessment = {
            "financial_data": {
                "occupancy_rate": None,
                "direct_channel_percentage": 30.0,
                "adr_cop": 450000.0,
            }
        }
        
        result = orchestrator._financial_validity_gate(assessment)
        
        assert result.passed is False
        assert result.status == GateStatus.BLOCKED

    def test_no_financial_data_blocks(self, orchestrator):
        """
        Test that missing financial data blocks the gate.
        """
        assessment = {}
        
        result = orchestrator._financial_validity_gate(assessment)
        
        assert result.passed is False
        assert result.status == GateStatus.BLOCKED
        assert "No financial data found" in result.message


# =============================================================================
# Test Class 4: TestCoherenceGate
# =============================================================================

class TestCoherenceGate:
    """Tests for the coherence score publication gate."""

    def test_high_coherence_passes(self, orchestrator):
        """
        Test that gate passes when coherence >= 0.8.
        
        Expected: PASSED status, passed=True
        """
        assessment = {
            "coherence_score": 0.85,
            "metrics": {"coherence_score": 0.85}
        }
        
        result = orchestrator._coherence_gate(assessment)
        
        assert result.passed is True
        assert result.status == GateStatus.PASSED
        assert result.value == 0.85
        assert "meets threshold" in result.message

    def test_exact_threshold_passes(self, orchestrator):
        """
        Test that gate passes at exactly 0.8 threshold.
        
        Boundary condition test.
        """
        assessment = {
            "coherence_score": 0.8,
        }
        
        result = orchestrator._coherence_gate(assessment)
        
        assert result.passed is True
        assert result.status == GateStatus.PASSED

    def test_low_coherence_blocks(self, orchestrator):
        """
        Test that gate blocks when coherence < 0.8.
        
        Expected: BLOCKED status for < 0.5, FAILED for 0.5-0.8
        """
        assessment = {
            "coherence_score": 0.6,
        }
        
        result = orchestrator._coherence_gate(assessment)
        
        assert result.passed is False
        assert result.status == GateStatus.FAILED  # 0.5 <= score < 0.8
        assert result.value == 0.6
        assert "below threshold" in result.message

    def test_very_low_coherence_blocked(self, orchestrator):
        """
        Test that very low coherence (< 0.5) results in BLOCKED status.
        """
        assessment = {
            "coherence_score": 0.3,
        }
        
        result = orchestrator._coherence_gate(assessment)
        
        assert result.passed is False
        assert result.status == GateStatus.BLOCKED
        assert result.value == 0.3

    def test_zero_coherence_blocked(self, orchestrator):
        """
        Test that zero coherence is BLOCKED.
        """
        assessment = {
            "coherence_score": 0.0,
        }
        
        result = orchestrator._coherence_gate(assessment)
        
        assert result.passed is False
        assert result.status == GateStatus.BLOCKED
        assert result.value == 0.0

    def test_missing_coherence_blocks(self, orchestrator):
        """
        Test that missing coherence score blocks.
        """
        assessment = {}
        
        result = orchestrator._coherence_gate(assessment)
        
        assert result.passed is False
        assert result.status == GateStatus.BLOCKED
        assert "not found" in result.message


# =============================================================================
# Test Class 5: TestCriticalRecallGate
# =============================================================================

class TestCriticalRecallGate:
    """Tests for the critical recall publication gate."""

    def test_high_recall_passes(self, orchestrator):
        """
        Test that gate passes when critical recall >= 90%.
        
        Expected: PASSED status, passed=True
        """
        assessment = {
            "critical_recall": 0.95,
            "metrics": {"critical_recall": 0.95}
        }
        
        result = orchestrator._critical_recall_gate(assessment)
        
        assert result.passed is True
        assert result.status == GateStatus.PASSED
        assert result.value == 0.95
        assert "95.0%" in result.message

    def test_exact_threshold_passes(self, orchestrator):
        """
        Test that gate passes at exactly 90% threshold.
        
        Boundary condition test.
        """
        assessment = {
            "critical_recall": 0.90,
        }
        
        result = orchestrator._critical_recall_gate(assessment)
        
        assert result.passed is True
        assert result.status == GateStatus.PASSED

    def test_low_recall_blocks(self, orchestrator):
        """
        Test that gate blocks when critical recall < 90%.
        
        Expected: BLOCKED status, passed=False
        """
        assessment = {
            "critical_recall": 0.75,
        }
        
        result = orchestrator._critical_recall_gate(assessment)
        
        assert result.passed is False
        assert result.status == GateStatus.BLOCKED
        assert result.value == 0.75
        assert "75.0%" in result.message
        assert "below threshold" in result.message

    def test_very_low_recall_blocks(self, orchestrator):
        """
        Test that very low recall blocks.
        """
        assessment = {
            "critical_recall": 0.5,
        }
        
        result = orchestrator._critical_recall_gate(assessment)
        
        assert result.passed is False
        assert result.status == GateStatus.BLOCKED
        assert result.value == 0.5

    def test_missing_recall_blocks(self, orchestrator):
        """
        Test that missing critical recall blocks.
        """
        assessment = {}
        
        result = orchestrator._critical_recall_gate(assessment)
        
        assert result.passed is False
        assert result.status == GateStatus.BLOCKED
        assert "not found" in result.message


# =============================================================================
# Test Class 6: TestPublicationGatesOrchestrator
# =============================================================================

class TestPublicationGatesOrchestrator:
    """Tests for the publication gates orchestrator."""

    def test_all_gates_pass(self, orchestrator, valid_assessment):
        """
        Test that when all gates pass, is_ready_for_publication returns True.
        
        Expected: ready=True, all results passed=True
        """
        results = orchestrator.run_all(valid_assessment)
        
        assert len(results) == 6  # 6 gates (including ethics)
        assert all(r.passed for r in results)
        assert orchestrator.is_ready_for_publication(results) is True

    def test_one_gate_blocks(self, orchestrator):
        """
        Test that if any gate fails, is_ready_for_publication returns False.
        
        Expected: ready=False, get_blocking_gates returns failed gate
        """
        assessment = {
            "coherence_score": 0.85,
            "evidence_coverage": 0.96,
            "hard_contradictions": 1,  # This will fail
            "critical_recall": 0.95,
            "financial_data": {
                "occupancy_rate": 75.0,
                "direct_channel_percentage": 30.0,
                "adr_cop": 450000.0,
            },
            "validation_summary": {"hard_contradictions_count": 1},
            "conflicts": [{"severity": "HARD"}]
        }
        
        results = orchestrator.run_all(assessment)
        
        assert orchestrator.is_ready_for_publication(results) is False
        
        blocking = orchestrator.get_blocking_gates(results)
        assert len(blocking) >= 1
        assert any(r.gate_name == "hard_contradictions" for r in blocking)

    def test_get_blocking_issues(self, orchestrator):
        """
        Test that get_blocking_gates returns only failed gates.
        """
        # Mix of passing and failing
        assessment = {
            "coherence_score": 0.85,  # Pass
            "evidence_coverage": 0.50,  # Fail
            "hard_contradictions": 0,  # Pass
            "critical_recall": 0.50,  # Fail
            "financial_data": {
                "occupancy_rate": 75.0,
                "direct_channel_percentage": 30.0,
                "adr_cop": 450000.0,
            },
        }
        
        results = orchestrator.run_all(assessment)
        blocking = orchestrator.get_blocking_gates(results)
        
        # Should have exactly 2 blocking gates
        assert len(blocking) == 2
        
        blocking_names = {r.gate_name for r in blocking}
        assert "evidence_coverage" in blocking_names
        assert "critical_recall" in blocking_names
        assert "coherence" not in blocking_names
        assert "hard_contradictions" not in blocking_names

    def test_multiple_gates_block(self, orchestrator):
        """
        Test that multiple failing gates are all reported.
        """
        assessment = {
            "coherence_score": 0.3,  # Fail
            "evidence_coverage": 0.50,  # Fail
            "hard_contradictions": 5,  # Fail
            "critical_recall": 0.50,  # Fail
            "financial_data": {
                "occupancy_rate": 0,  # Fail
                "direct_channel_percentage": 0,
                "adr_cop": 0,
            },
            "validation_summary": {"hard_contradictions_count": 5},
            "conflicts": [{"severity": "HARD"}] * 5
        }
        
        results = orchestrator.run_all(assessment)
        
        assert orchestrator.is_ready_for_publication(results) is False
        
        blocking = orchestrator.get_blocking_gates(results)
        assert len(blocking) == 6  # All gates should block

    def test_run_publication_gates_function(self, valid_assessment):
        """
        Test the convenience function run_publication_gates.
        """
        results = run_publication_gates(valid_assessment)
        
        assert len(results) == 6
        assert all(r.passed for r in results)

    def test_check_publication_readiness_function(self):
        """
        Test the convenience function check_publication_readiness.
        """
        assessment = {
            "coherence_score": 0.85,
            "evidence_coverage": 0.96,
            "hard_contradictions": 0,
            "critical_recall": 0.95,
            "financial_data": {
                "occupancy_rate": 75.0,
                "direct_channel_percentage": 30.0,
                "adr_cop": 450000.0,
            },
        }
        
        report = check_publication_readiness(assessment)
        
        assert report["ready"] is True
        assert report["status"] == "READY_FOR_PUBLICATION"
        assert report["summary"]["passed"] == 6
        assert report["summary"]["failed"] == 0
        assert len(report["blocking_issues"]) == 0


# =============================================================================
# Test Class 7: TestHotelVisperasScenario
# =============================================================================

class TestHotelVisperasScenario:
    """
    Tests for the specific Hotel Vísperas scenario.
    
    Hotel Vísperas tiene múltiples problemas que deberían resultar
    en estado DRAFT_INTERNAL (no apto para publicación).
    """

    def test_visperas_blocked_by_coherence(self, orchestrator, visperas_assessment):
        """
        Test that Hotel Vísperas is blocked by coherence gate (score = 0.0).
        
        coherence_score: 0.0 < 0.8 threshold → BLOCKED
        """
        result = orchestrator._coherence_gate(visperas_assessment)
        
        assert result.passed is False
        assert result.status == GateStatus.BLOCKED
        assert result.value == 0.0
        assert "0.00" in result.message or "0.0" in result.message

    def test_visperas_has_hard_contradictions(self, orchestrator, visperas_assessment):
        """
        Test that Hotel Vísperas has hard contradictions detected.
        
        hard_contradictions: 3 > 0 threshold → BLOCKED
        """
        result = orchestrator._hard_contradictions_gate(visperas_assessment)
        
        assert result.passed is False
        assert result.status == GateStatus.BLOCKED
        assert result.value == 3
        assert "3 hard contradiction" in result.message

    def test_visperas_low_evidence_coverage(self, orchestrator, visperas_assessment):
        """
        Test that Hotel Vísperas has low evidence coverage.
        
        evidence_coverage: 0.2 < 0.95 threshold → BLOCKED
        """
        result = orchestrator._evidence_coverage_gate(visperas_assessment)
        
        assert result.passed is False
        assert result.status == GateStatus.BLOCKED
        assert result.value == 0.2

    def test_visperas_low_critical_recall(self, orchestrator, visperas_assessment):
        """
        Test that Hotel Vísperas has low critical recall.
        
        critical_recall: 0.5 < 0.90 threshold → BLOCKED
        """
        result = orchestrator._critical_recall_gate(visperas_assessment)
        
        assert result.passed is False
        assert result.status == GateStatus.BLOCKED
        assert result.value == 0.5

    def test_visperas_financial_defaults(self, orchestrator, visperas_assessment):
        """
        Test that Hotel Vísperas has financial default values.
        
        occupancy_rate: 0, direct_channel: 0, adr_cop: 0 → BLOCKED
        """
        result = orchestrator._financial_validity_gate(visperas_assessment)
        
        assert result.passed is False
        assert result.status == GateStatus.BLOCKED
        assert "default values" in result.message

    def test_visperas_is_draft_internal(self, orchestrator, visperas_assessment):
        """
        Test that Hotel Vísperas final status is NOT ready for publication.
        
        Todos los gates deberían fallar → Estado DRAFT_INTERNAL equivalente
        """
        results = orchestrator.run_all(visperas_assessment)
        
        # All 6 gates should fail
        assert orchestrator.is_ready_for_publication(results) is False
        
        # Get blocking gates
        blocking = orchestrator.get_blocking_gates(results)
        
        # Should have multiple blocking gates
        assert len(blocking) >= 4  # At least 4 gates should block
        
        # Verify specific gates are blocking
        blocking_names = {r.gate_name for r in blocking}
        assert "coherence" in blocking_names
        assert "hard_contradictions" in blocking_names
        assert "evidence_coverage" in blocking_names
        assert "critical_recall" in blocking_names
        assert "financial_validity" in blocking_names

    def test_visperas_comprehensive_report(self, visperas_assessment):
        """
        Test the full readiness report for Hotel Vísperas.
        """
        report = check_publication_readiness(visperas_assessment)
        
        # Should not be ready
        assert report["ready"] is False
        assert report["status"] == "NOT_READY"
        
        # Should have multiple blocking issues
        assert len(report["blocking_issues"]) >= 4
        
        # Summary should show failures
        assert report["summary"]["passed"] < 2  # At most 1 gate passes
        assert report["summary"]["failed"] >= 4  # At least 4 gates fail
        
        # Verify timestamp exists
        assert "timestamp" in report["summary"]


# =============================================================================
# Additional Edge Case Tests
# =============================================================================

class TestEdgeCases:
    """Edge case tests for publication gates."""

    def test_empty_assessment(self, orchestrator):
        """
        Test behavior with completely empty assessment.
        """
        assessment = {}
        
        results = orchestrator.run_all(assessment)
        
        # Most gates should fail with empty data
        assert orchestrator.is_ready_for_publication(results) is False
        
        # At least coherence and critical_recall should block (missing data)
        blocking = orchestrator.get_blocking_gates(results)
        assert len(blocking) >= 2

    def test_custom_thresholds(self):
        """
        Test that custom thresholds work correctly.
        """
        config = PublicationGateConfig(
            coherence_threshold=0.9,
            evidence_coverage_threshold=0.99,
            critical_recall_threshold=0.95,
        )
        orchestrator = PublicationGatesOrchestrator(config)
        
        assessment = {
            "coherence_score": 0.85,  # Below 0.9
            "evidence_coverage": 0.96,  # Below 0.99
            "critical_recall": 0.94,  # Below 0.95
            "hard_contradictions": 0,
            "financial_data": {
                "occupancy_rate": 75.0,
                "direct_channel_percentage": 30.0,
                "adr_cop": 450000.0,
            },
        }
        
        results = orchestrator.run_all(assessment)
        blocking = orchestrator.get_blocking_gates(results)
        
        # Should have 3 blocking gates with stricter thresholds
        assert len(blocking) == 3

    def test_partial_assessment_data(self, orchestrator):
        """
        Test with partial assessment data (some fields missing).
        """
        assessment = {
            # Missing coherence_score
            "evidence_coverage": 0.96,
            "hard_contradictions": 0,
            "critical_recall": 0.95,
            "financial_data": {
                "occupancy_rate": 75.0,
                "direct_channel_percentage": 30.0,
                "adr_cop": 450000.0,
            },
        }
        
        results = orchestrator.run_all(assessment)
        
        # Should not be ready (coherence missing)
        assert orchestrator.is_ready_for_publication(results) is False
        
        blocking = orchestrator.get_blocking_gates(results)
        blocking_names = {r.gate_name for r in blocking}
        assert "coherence" in blocking_names

    def test_gate_result_to_dict(self):
        """
        Test that PublicationGateResult can be serialized to dict.
        """
        result = PublicationGateResult(
            gate_name="test_gate",
            passed=True,
            status=GateStatus.PASSED,
            message="Test passed",
            value=0.95,
            suggestion="",
            details={"extra": "info"}
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["gate_name"] == "test_gate"
        assert result_dict["passed"] is True
        assert result_dict["status"] == "PASSED"
        assert result_dict["value"] == 0.95
        assert "details" in result_dict

    def test_config_to_dict(self):
        """
        Test that PublicationGateConfig can be serialized to dict.
        """
        config = PublicationGateConfig()
        
        config_dict = config.to_dict()
        
        assert config_dict["coherence_threshold"] == 0.8
        assert config_dict["evidence_coverage_threshold"] == 0.95
        assert config_dict["critical_recall_threshold"] == 0.90
        assert config_dict["hard_contradictions_max"] == 0
        assert config_dict["financial_validity_required"] is True
