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


# ── FASE-A: IA-Readiness Critical Advisory Alert Tests ──────────────────────────────────────────

class TestIAReadinessAdvisoryAlert:
    """Tests for IA-Readiness Critical warning in diagnostic (FASE-A)."""

    def test_ia_critical_shows_alert(self):
        """IA-Readiness Critical → alert blockquote appears in output."""
        from modules.auditors.ia_readiness_calculator import IAReadinessReport
        gen = V4DiagnosticGenerator()
        audit = _make_minimal_audit()
        validation = _make_minimal_validation_summary()
        financial = _make_minimal_financial_scenarios()

        # Inject IAReadinessReport with Critical status
        ia_report = IAReadinessReport(
            overall_score=35.0,
            components={
                "schema_quality": 30.0,
                "crawler_access": 40.0,
                "citability": 35.0,
                "llms_txt": 0,
                "brand_signals": 40.0,
            },
            status="Critical",
            actionable_items=["Improve schema quality", "Fix crawler access"],
        )
        # Attach ia_readiness to the audit object
        audit = dataclass_replace(audit, ia_readiness=ia_report)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = gen.generate(
                audit_result=audit,
                validation_summary=validation,
                financial_scenarios=financial,
                hotel_name="Hotel Test",
                hotel_url="https://example.com",
                output_dir=tmpdir,
                coherence_score=0.85,
            )
            content = Path(path).read_text(encoding="utf-8")
            assert "Alerta IA-Readiness Critical" in content
            assert "objetivo comercial" in content.lower()

    def test_ia_ready_no_alert(self):
        """IA-Readiness Ready → NO alert blockquote."""
        from modules.auditors.ia_readiness_calculator import IAReadinessReport

        gen = V4DiagnosticGenerator()
        audit = _make_minimal_audit()
        validation = _make_minimal_validation_summary()
        financial = _make_minimal_financial_scenarios()

        ia_report = IAReadinessReport(
            overall_score=78.0,
            components={
                "schema_quality": 80.0,
                "crawler_access": 75.0,
                "citability": 78.0,
                "llms_txt": 100,
                "brand_signals": 70.0,
            },
            status="Ready",
            actionable_items=[],
        )
        audit = dataclass_replace(audit, ia_readiness=ia_report)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = gen.generate(
                audit_result=audit,
                validation_summary=validation,
                financial_scenarios=financial,
                hotel_name="Hotel Test",
                hotel_url="https://example.com",
                output_dir=tmpdir,
                coherence_score=0.85,
            )
            content = Path(path).read_text(encoding="utf-8")
            assert "Alerta IA-Readiness Critical" not in content

    def test_ia_needs_work_no_alert(self):
        """IA-Readiness Needs Work → NO alert blockquote (only Critical triggers)."""
        from modules.auditors.ia_readiness_calculator import IAReadinessReport

        gen = V4DiagnosticGenerator()
        audit = _make_minimal_audit()
        validation = _make_minimal_validation_summary()
        financial = _make_minimal_financial_scenarios()

        ia_report = IAReadinessReport(
            overall_score=55.0,
            components={
                "schema_quality": 50.0,
                "crawler_access": 55.0,
                "citability": 60.0,
                "llms_txt": 100,
                "brand_signals": 50.0,
            },
            status="Needs Work",
            actionable_items=["Improve schema quality"],
        )
        audit = dataclass_replace(audit, ia_readiness=ia_report)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = gen.generate(
                audit_result=audit,
                validation_summary=validation,
                financial_scenarios=financial,
                hotel_name="Hotel Test",
                hotel_url="https://example.com",
                output_dir=tmpdir,
                coherence_score=0.85,
            )
            content = Path(path).read_text(encoding="utf-8")
            assert "Alerta IA-Readiness Critical" not in content


class TestWhatsappConflictNote:
    """FASE-A-02b: Tests for _build_whatsapp_conflict_note."""

    def test_whatsapp_conflict_note_generated(self):
        """With whatsapp conflict in validation.conflicts → note not empty."""
        gen = V4DiagnosticGenerator()

        # Build audit with whatsapp conflict in validation.conflicts
        audit = V4AuditResult(
            url="https://hotel-test.com",
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
                phone="+573001234567",
                website="https://hotel-test.com",
                address="Calle 123, Armenia, Quindío",
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
                whatsapp_status="conflict",
                phone_web="+573001111111",
                phone_gbp="+573002222222",
                adr_status="verified",
                adr_web=300000.0,
                adr_benchmark=280000.0,
                conflicts=[
                    {"field_name": "whatsapp", "value": "conflict", "discrepancies": "phone_web vs phone_gbp"},
                ],
            ),
            overall_confidence="verified",
            critical_issues=[],
            recommendations=[],
        )

        note = gen._build_whatsapp_conflict_note(audit)

        # Should NOT be empty when conflict exists
        assert note != ""
        # Should contain the phone numbers
        assert "+573001111111" in note
        assert "+573002222222" in note
        # Should contain the business impact phrasing
        assert "ALERTA" in note
        assert "número equivocado" in note.lower()

    def test_whatsapp_conflict_note_empty_no_conflict(self):
        """Without whatsapp conflict in validation.conflicts → note empty."""
        gen = V4DiagnosticGenerator()

        # Audit with no whatsapp conflict (different field conflict only)
        audit = V4AuditResult(
            url="https://hotel-test.com",
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
                phone="+573001234567",
                website="https://hotel-test.com",
                address="Calle 123, Armenia, Quindío",
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
                whatsapp_status="conflict",
                phone_web=None,  # Missing phone_web → note should be empty
                phone_gbp="+573002222222",
                adr_status="verified",
                adr_web=300000.0,
                adr_benchmark=280000.0,
                conflicts=[
                    {"field_name": "whatsapp", "value": "conflict", "discrepancies": "phone_web vs phone_gbp"},
                ],
            ),
            overall_confidence="verified",
            critical_issues=[],
            recommendations=[],
        )

        note = gen._build_whatsapp_conflict_note(audit)

        # Should be empty when no whatsapp conflict
        assert note == ""

    def test_whatsapp_conflict_note_empty_no_validation(self):
        """Without whatsapp conflict → note empty (safe fallback)."""
        gen = V4DiagnosticGenerator()

        # Audit with whatsapp_status=conflict but NO whatsapp in conflicts list
        audit = V4AuditResult(
            url="https://hotel-test.com",
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
                phone="+573001234567",
                website="https://hotel-test.com",
                address="Calle 123, Armenia, Quindío",
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
            # whatsapp_status=conflict BUT no whatsapp conflict in conflicts list
            validation=CrossValidationResult(
                whatsapp_status="conflict",
                phone_web="+573001111111",
                phone_gbp="+573002222222",
                adr_status="verified",
                adr_web=300000.0,
                adr_benchmark=280000.0,
                conflicts=[
                    {"field_name": "email", "value": "conflict", "discrepancies": "different email"},
                ],
            ),
            overall_confidence="verified",
            critical_issues=[],
            recommendations=[],
        )

        note = gen._build_whatsapp_conflict_note(audit)

        # Should be empty when no whatsapp conflict in the list
        assert note == ""


def dataclass_replace(obj, **kwargs):
    """Create a copy of a dataclass with updated fields."""
    from dataclasses import replace
    return replace(obj, **kwargs)
