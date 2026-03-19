"""Tests for Coherence Gate.

Valida que el gate de coherencia:
1. Pasa cuando coherence >= 0.8
2. Bloquea certificación cuando coherence < 0.8
3. Identifica gaps correctamente
4. Genera sugerencias de mejora
"""

import pytest
from modules.quality_gates.coherence_gate import (
    CoherenceGate,
    CoherenceGateResult,
    CoherenceStatus,
    PublicationStatus,
    CoherenceGap,
    check_coherence,
)


class TestCoherenceGate:
    """Test cases for CoherenceGate."""

    def test_gate_initialization_default_threshold(self):
        """Test gate initializes with default threshold of 0.8."""
        gate = CoherenceGate()
        assert gate.threshold == 0.8

    def test_gate_initialization_custom_threshold(self):
        """Test gate accepts custom threshold."""
        gate = CoherenceGate(config={"threshold": 0.9})
        assert gate.threshold == 0.9

    def test_high_coherence_passes(self):
        """Test that coherence >= 0.8 passes."""
        gate = CoherenceGate()
        
        result = gate.execute(coherence_score=0.85)
        
        assert result.passed is True
        assert result.status == CoherenceStatus.CERTIFIED
        assert result.publication_status == PublicationStatus.READY_FOR_CLIENT
        assert result.can_certify is True
        assert result.can_publish is True

    def test_exact_threshold_passes(self):
        """Test that coherence = 0.8 passes."""
        gate = CoherenceGate()
        
        result = gate.execute(coherence_score=0.8)
        
        assert result.passed is True
        assert result.status == CoherenceStatus.CERTIFIED

    def test_slightly_below_threshold_fails(self):
        """Test that coherence < 0.8 fails certification."""
        gate = CoherenceGate()
        
        result = gate.execute(coherence_score=0.79)
        
        assert result.passed is False
        assert result.status == CoherenceStatus.REVIEW
        assert result.publication_status == PublicationStatus.REQUIRES_REVIEW
        assert result.can_certify is False
        assert result.requires_review is True

    def test_medium_coherence_requires_review(self):
        """Test that coherence 0.5-0.8 requires review."""
        gate = CoherenceGate()
        
        result = gate.execute(coherence_score=0.65)
        
        assert result.status == CoherenceStatus.REVIEW
        assert result.publication_status == PublicationStatus.REQUIRES_REVIEW

    def test_low_coherence_draft_internal(self):
        """Test that coherence < 0.5 is draft internal."""
        gate = CoherenceGate()
        
        result = gate.execute(coherence_score=0.3)
        
        assert result.status == CoherenceStatus.DRAFT_INTERNAL
        assert result.publication_status == PublicationStatus.DRAFT_INTERNAL

    def test_very_low_coherence_blocked(self):
        """Test that very low coherence is blocked."""
        gate = CoherenceGate()
        
        result = gate.execute(coherence_score=0.1)
        
        assert result.status == CoherenceStatus.DRAFT_INTERNAL
        assert result.can_certify is False
        assert result.can_publish is False

    def test_zero_coherence_blocked(self):
        """Test that coherence = 0 is blocked (Hotel Vísperas case)."""
        gate = CoherenceGate()
        
        result = gate.execute(coherence_score=0.0)
        
        assert result.passed is False
        assert result.status == CoherenceStatus.DRAFT_INTERNAL
        assert result.can_certify is False
        assert len(result.suggestions) > 0

    def test_result_includes_gaps(self):
        """Test that result includes identified gaps."""
        gate = CoherenceGate()
        
        assessment_data = {
            "evidence_coverage": 0.3,
            "hard_contradictions": 2,
        }
        
        result = gate.execute(
            coherence_score=0.4,
            assessment_data=assessment_data
        )
        
        assert len(result.gaps) > 0

    def test_result_includes_suggestions(self):
        """Test that result includes improvement suggestions."""
        gate = CoherenceGate()
        
        result = gate.execute(coherence_score=0.6)
        
        assert len(result.suggestions) > 0

    def test_custom_threshold_0_9(self):
        """Test gate with stricter threshold of 0.9."""
        gate = CoherenceGate(config={"threshold": 0.9})
        
        result = gate.execute(coherence_score=0.85)
        
        assert result.passed is False  # Below 0.9
        assert result.threshold == 0.9

    def test_check_method_from_assessment(self):
        """Test check method that extracts from assessment."""
        gate = CoherenceGate()
        
        assessment = {
            "coherence_score": 0.85,
            "evidence_coverage": 0.9,
        }
        
        result = gate.check(assessment)
        
        assert result.passed is True


class TestCoherenceGateResult:
    """Test cases for CoherenceGateResult."""

    def test_result_properties_certified(self):
        """Test result properties when certified."""
        result = CoherenceGateResult(
            coherence_score=0.85,
            threshold=0.8,
            passed=True,
            status=CoherenceStatus.CERTIFIED,
            publication_status=PublicationStatus.READY_FOR_CLIENT,
        )
        
        assert result.can_certify is True
        assert result.can_publish is True
        assert result.requires_review is False

    def test_result_properties_review(self):
        """Test result properties when review needed."""
        result = CoherenceGateResult(
            coherence_score=0.65,
            threshold=0.8,
            passed=False,
            status=CoherenceStatus.REVIEW,
            publication_status=PublicationStatus.REQUIRES_REVIEW,
        )
        
        assert result.can_certify is False
        assert result.can_publish is False
        assert result.requires_review is True

    def test_result_to_dict(self):
        """Test result serialization."""
        result = CoherenceGateResult(
            coherence_score=0.85,
            threshold=0.8,
            passed=True,
            status=CoherenceStatus.CERTIFIED,
            publication_status=PublicationStatus.READY_FOR_CLIENT,
            gaps=[
                CoherenceGap(
                    category="evidence",
                    description="Missing evidence",
                    severity="medium",
                    suggestion="Add more sources",
                )
            ],
            suggestions=["Suggestion 1"],
        )
        
        data = result.to_dict()
        
        assert data["coherence_score"] == 0.85
        assert data["threshold"] == 0.8
        assert data["passed"] is True
        assert data["status"] == "certified"
        assert data["publication_status"] == "ready_for_client"
        assert data["can_certify"] is True
        assert len(data["gaps"]) == 1
        assert len(data["suggestions"]) == 1

    def test_result_user_message_passed(self):
        """Test user message when passed."""
        result = CoherenceGateResult(
            coherence_score=0.85,
            threshold=0.8,
            passed=True,
            status=CoherenceStatus.CERTIFIED,
            publication_status=PublicationStatus.READY_FOR_CLIENT,
        )
        
        message = result.to_user_message()
        
        assert "✅" in message or "validada" in message.lower()
        assert "85" in message or "0.85" in message

    def test_result_user_message_failed(self):
        """Test user message when failed."""
        result = CoherenceGateResult(
            coherence_score=0.4,
            threshold=0.8,
            passed=False,
            status=CoherenceStatus.DRAFT_INTERNAL,
            publication_status=PublicationStatus.DRAFT_INTERNAL,
            gaps=[
                CoherenceGap(
                    category="evidence",
                    description="Insufficient evidence",
                    severity="high",
                    suggestion="Complete onboarding",
                )
            ],
            suggestions=["Complete onboarding"],
        )
        
        message = result.to_user_message()
        
        assert "⚠️" in message or "insuficiente" in message.lower()
        assert "40" in message or "0.4" in message
        assert "Gaps" in message or "gaps" in message.lower()


class TestCheckCoherenceHelper:
    """Test cases for check_coherence helper function."""

    def test_helper_high_coherence(self):
        """Test helper with high coherence."""
        result = check_coherence(coherence_score=0.85, threshold=0.8)
        
        assert result.passed is True
        assert result.status == CoherenceStatus.CERTIFIED

    def test_helper_low_coherence(self):
        """Test helper with low coherence."""
        result = check_coherence(coherence_score=0.5, threshold=0.8)
        
        assert result.passed is False

    def test_helper_custom_threshold(self):
        """Test helper with custom threshold."""
        result = check_coherence(coherence_score=0.88, threshold=0.9)
        
        assert result.passed is False  # 0.88 < 0.9
        assert result.threshold == 0.9


class TestCoherenceGap:
    """Test cases for CoherenceGap."""

    def test_gap_creation(self):
        """Test CoherenceGap creation."""
        gap = CoherenceGap(
            category="evidence",
            description="Missing evidence",
            severity="high",
            suggestion="Add more sources",
        )
        
        assert gap.category == "evidence"
        assert gap.severity == "high"


class TestHotelVisperasScenario:
    """Test scenarios for Hotel Vísperas case."""

    def test_visperas_zero_coherence_blocked(self):
        """Test Hotel Vísperas with 0% coherence is blocked."""
        gate = CoherenceGate()
        
        # Hotel Vísperas had coherence_score = 0.0
        result = gate.execute(coherence_score=0.0)
        
        assert result.passed is False
        assert result.status == CoherenceStatus.DRAFT_INTERNAL
        assert result.publication_status == PublicationStatus.DRAFT_INTERNAL
        assert result.can_certify is False
        assert len(result.suggestions) > 0
        # Should suggest completing onboarding
        assert any("onboarding" in s.lower() for s in result.suggestions)

    def test_visperas_should_not_be_certified(self):
        """Test that Hotel Vísperas should never be certified."""
        gate = CoherenceGate()
        
        assessment = {
            "coherence_score": 0.0,
            "hard_contradictions": 3,
            "evidence_coverage": 0.2,
        }
        
        result = gate.check(assessment)
        
        assert result.can_certify is False
        assert result.can_publish is False
        assert result.status == CoherenceStatus.DRAFT_INTERNAL
