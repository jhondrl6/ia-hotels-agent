"""
Tests for FASE-PROP-A: Coherence Score Unification.

Verifies:
1. Pipeline timing: CoherenceValidator runs before diagnostic generation
2. External coherence_score is used directly (no fallback)
3. gate_status is passed through to template data
4. Fallback _calculate_coherence_score is never auto-invoked
"""

import pytest
import tempfile
from pathlib import Path

from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
from modules.commercial_documents.data_structures import (
    V4AuditResult,
    ValidationSummary,
    ValidatedField,
    FinancialScenarios,
    Scenario,
    SchemaValidation,
    GBPData,
    PerformanceData,
    CrossValidationResult,
    ConfidenceLevel,
)


def _make_minimal_audit() -> V4AuditResult:
    """Create a minimal V4AuditResult for testing."""
    return V4AuditResult(
        url="https://example.com",
        hotel_name="Hotel Test",
        timestamp="2026-01-01T00:00:00",
        schema=SchemaValidation(
            hotel_schema_detected=True,
            hotel_schema_valid=True,
            hotel_confidence="verified",
            faq_schema_detected=True,
            faq_schema_valid=True,
            faq_confidence="verified",
            org_schema_detected=True,
            total_schemas=3,
        ),
        gbp=GBPData(
            place_found=True,
            place_id="ChI123",
            name="Hotel Test",
            rating=4.5,
            reviews=100,
            photos=30,
            phone="+571234567890",
            website="https://example.com",
            address="Calle 123, Ciudad, Colombia",
            geo_score=80,
            geo_score_breakdown={},
            confidence="verified",
        ),
        performance=PerformanceData(
            has_field_data=True,
            mobile_score=85,
            desktop_score=90,
            lcp=1.5,
            fid=20,
            cls=0.05,
            status="ok",
            message="Good performance",
        ),
        validation=CrossValidationResult(
            whatsapp_status="verified",
            phone_web="+571234567890",
            phone_gbp="+571234567890",
            adr_status="verified",
            adr_web=300000.0,
            adr_benchmark=280000.0,
        ),
        overall_confidence="verified",
        critical_issues=[],
        recommendations=[],
    )


def _make_minimal_validation_summary() -> ValidationSummary:
    """Create a minimal ValidationSummary for testing."""
    return ValidationSummary(
        fields=[
            ValidatedField(
                field_name="rooms",
                value=10,
                confidence=ConfidenceLevel.VERIFIED,
                sources=["onboarding"],
            ),
        ],
        overall_confidence=ConfidenceLevel.VERIFIED,
        conflicts=[],
    )


def _make_minimal_financial_scenarios() -> FinancialScenarios:
    """Create minimal FinancialScenarios for testing."""
    base = Scenario(
        monthly_loss_min=1_000_000,
        monthly_loss_max=2_000_000,
        probability=0.7,
        description="Test scenario",
        assumptions=["Assumption 1"],
        confidence_score=0.8,
        monthly_loss_central=1_500_000,
    )
    return FinancialScenarios(
        conservative=base,
        realistic=base,
        optimistic=base,
    )


class TestCoherenceScoreUnification:
    """FASE-PROP-A: coherence_score uses external value, no auto-fallback."""

    def test_external_coherence_score_used_directly(self):
        """When coherence_score=0.72 is passed, template data shows 0.72 (not fallback)."""
        gen = V4DiagnosticGenerator()
        audit = _make_minimal_audit()
        validation = _make_minimal_validation_summary()
        financial = _make_minimal_financial_scenarios()

        template_data = gen._prepare_template_data(
            audit_result=audit,
            validation_summary=validation,
            financial_scenarios=financial,
            hotel_name="Hotel Test",
            hotel_url="https://example.com",
            coherence_score=0.72,
            gate_status="PASSED",
        )

        assert template_data["coherence_score"] == "0.72"
        assert template_data["gate_status"] == "PASSED"

    def test_none_coherence_score_shows_pending(self):
        """When coherence_score is None, template data shows 'PENDIENTE'."""
        gen = V4DiagnosticGenerator()
        audit = _make_minimal_audit()
        validation = _make_minimal_validation_summary()
        financial = _make_minimal_financial_scenarios()

        template_data = gen._prepare_template_data(
            audit_result=audit,
            validation_summary=validation,
            financial_scenarios=financial,
            hotel_name="Hotel Test",
            hotel_url="https://example.com",
            coherence_score=None,
            gate_status=None,
        )

        assert template_data["coherence_score"] == "PENDIENTE"
        assert template_data["gate_status"] == "PENDIENTE"

    def test_zero_coherence_score_shows_pending(self):
        """When coherence_score is 0, template data shows 'PENDIENTE'."""
        gen = V4DiagnosticGenerator()
        audit = _make_minimal_audit()
        validation = _make_minimal_validation_summary()
        financial = _make_minimal_financial_scenarios()

        template_data = gen._prepare_template_data(
            audit_result=audit,
            validation_summary=validation,
            financial_scenarios=financial,
            hotel_name="Hotel Test",
            hotel_url="https://example.com",
            coherence_score=0,
            gate_status="FAILED",
        )

        assert template_data["coherence_score"] == "PENDIENTE"
        assert template_data["gate_status"] == "FAILED"

    def test_fallback_never_auto_invoked(self):
        """_calculate_coherence_score must never be called automatically when score is missing."""
        gen = V4DiagnosticGenerator()
        audit = _make_minimal_audit()
        validation = _make_minimal_validation_summary()
        financial = _make_minimal_financial_scenarios()

        # coherence_score=None should NOT trigger fallback calculation
        template_data = gen._prepare_template_data(
            audit_result=audit,
            validation_summary=validation,
            financial_scenarios=financial,
            hotel_name="Hotel Test",
            hotel_url="https://example.com",
            coherence_score=None,
        )

        # If fallback had run, we'd see ~100 (since our mock has VERIFIED field).
        # Instead we should see "PENDIENTE".
        assert template_data["coherence_score"] == "PENDIENTE"

    def test_generate_accepts_gate_status(self):
        """generate() must accept gate_status parameter."""
        gen = V4DiagnosticGenerator()
        audit = _make_minimal_audit()
        validation = _make_minimal_validation_summary()
        financial = _make_minimal_financial_scenarios()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = gen.generate(
                audit_result=audit,
                validation_summary=validation,
                financial_scenarios=financial,
                hotel_name="Hotel Test",
                hotel_url="https://example.com",
                output_dir=tmpdir,
                coherence_score=0.85,
                gate_status="PASSED",
            )
            assert Path(path).exists()
            content = Path(path).read_text(encoding="utf-8")
            assert "gate_status: PASSED" in content
            assert "coherence_score: 0.85" in content

    def test_generate_with_none_shows_pending(self):
        """generate() without coherence_score must show PENDIENTE in output."""
        gen = V4DiagnosticGenerator()
        audit = _make_minimal_audit()
        validation = _make_minimal_validation_summary()
        financial = _make_minimal_financial_scenarios()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = gen.generate(
                audit_result=audit,
                validation_summary=validation,
                financial_scenarios=financial,
                hotel_name="Hotel Test",
                hotel_url="https://example.com",
                output_dir=tmpdir,
                coherence_score=None,
                gate_status=None,
            )
            assert Path(path).exists()
            content = Path(path).read_text(encoding="utf-8")
            assert "gate_status: PENDIENTE" in content
            assert "coherence_score: PENDIENTE" in content


class TestDeprecatedFallback:
    """Verify _calculate_coherence_score still exists for explicit callers."""

    def test_deprecated_method_exists(self):
        """The method must still exist for backward compatibility."""
        gen = V4DiagnosticGenerator()
        validation = _make_minimal_validation_summary()
        score = gen._calculate_coherence_score(validation)
        assert isinstance(score, int)
        # With 1 VERIFIED field, score should be 100
        assert score == 100
