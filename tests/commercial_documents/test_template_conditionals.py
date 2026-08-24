"""Tests for FASE-1-A FIX-1: Template conditionals pre-processor.

FASE-R0-C additions:
- TestSeccion1Conditional: B3 fix (title S1 + WhatsApp clause conditional).
- TestSeccion6Contador: B5 fix (dynamic counter in Section 6).
- TestTemplateNoHardcodedFugas: static test ensuring no hardcoded fuga strings.
"""

import pytest
from pathlib import Path
from string import Template
from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator
from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
from modules.commercial_documents.data_structures import (
    V4AuditResult,
    SchemaValidation,
    GBPData,
    PerformanceData,
    CrossValidationResult,
)


class TestPreprocessConditionals:
    """Tests for _preprocess_conditionals method."""

    @pytest.fixture
    def generator(self):
        """Create a V4ProposalGenerator instance."""
        return V4ProposalGenerator()

    def test_conditional_include_when_true(self, generator):
        """{{if var == "value"}} block included when condition matches."""
        template = "Start {{if financial_evidence_tier == \"C\"}}WARNING{{endif}} End"
        data = {'financial_evidence_tier': 'C'}
        result = generator._preprocess_conditionals(template, data)
        assert "WARNING" in result
        assert "{{if}}" not in result
        assert "{{endif}}" not in result

    def test_conditional_exclude_when_false(self, generator):
        """{{if var == "value"}} block excluded when condition does not match."""
        template = "Start {{if financial_evidence_tier == \"C\"}}WARNING{{endif}} End"
        data = {'financial_evidence_tier': 'B'}
        result = generator._preprocess_conditionals(template, data)
        assert "WARNING" not in result
        assert "{{if}}" not in result
        assert "{{endif}}" not in result

    def test_no_residue_in_output(self, generator):
        """Output must NOT contain {{if}} or {{endif}} tags."""
        template = "{{if financial_evidence_tier == \"C\"}}content{{endif}}"
        data = {'financial_evidence_tier': 'C'}
        result = generator._preprocess_conditionals(template, data)
        assert "{{if}}" not in result
        assert "{{endif}}" not in result

    def test_render_template_with_conditionals(self, generator):
        """_render_template processes conditionals before safe_substitute."""
        template = "Tier: {{if financial_evidence_tier == \"C\"}}BRONZE{{endif}}"
        data = {'financial_evidence_tier': 'C', 'financial_evidence_tier': 'C'}
        result = generator._render_template(template, data)
        assert "BRONZE" in result
        assert "{{if}}" not in result

    def test_conditional_with_missing_variable(self, generator):
        """Missing variable treated as empty string (no match)."""
        template = "{{if missing_var == \"value\"}}SHOULD_NOT_APPEAR{{endif}}"
        data = {}
        result = generator._preprocess_conditionals(template, data)
        assert "SHOULD_NOT_APPEAR" not in result

    def test_multiple_conditionals(self, generator):
        """Multiple {{if}} blocks processed independently."""
        template = "{{if tier == \"A\"}}HIGH{{endif}} middle {{if tier == \"B\"}}MED{{endif}}"
        data = {'tier': 'A'}
        result = generator._preprocess_conditionals(template, data)
        assert "HIGH" in result
        assert "MED" not in result
        assert "{{if}}" not in result


# ---------------------------------------------------------------------------
# Helpers for FASE-R0-C (B3: Seccion 1 conditional)
# ---------------------------------------------------------------------------

def _make_audit_with_whatsapp_conflict() -> V4AuditResult:
    """Audit with real WhatsApp conflict (phone_web != phone_gbp)."""
    return V4AuditResult(
        url="https://hotel-test.com",
        hotel_name="Hotel Test",
        timestamp="2026-01-01T00:00:00",
        schema=SchemaValidation(
            hotel_schema_detected=True, hotel_schema_valid=True,
            hotel_confidence="verified", faq_schema_detected=True,
            faq_schema_valid=True, faq_confidence="verified",
            org_schema_detected=True, total_schemas=3,
        ),
        gbp=GBPData(
            place_found=True, place_id="ChI123", name="Hotel Test",
            rating=4.5, reviews=100, photos=30, phone="+573001234567",
            website="https://hotel-test.com", address="Calle 123, Armenia",
            geo_score=80, geo_score_breakdown={}, confidence="verified",
        ),
        performance=PerformanceData(
            has_field_data=True, mobile_score=85, desktop_score=90,
            lcp=1.5, fid=20, cls=0.05, status="ok", message="OK",
        ),
        validation=CrossValidationResult(
            whatsapp_status="conflict",
            phone_web="+573001111111",
            phone_gbp="+573002222222",
            adr_status="verified", adr_web=300000.0, adr_benchmark=280000.0,
            conflicts=[
                {"field_name": "whatsapp", "value": "conflict",
                 "discrepancies": "phone_web vs phone_gbp"},
            ],
        ),
        overall_confidence="verified",
        critical_issues=[], recommendations=[],
    )


def _make_audit_without_whatsapp_conflict() -> V4AuditResult:
    """Audit without WhatsApp conflict (Zione-like: VERIFIED)."""
    return V4AuditResult(
        url="https://hotel-test.com",
        hotel_name="Hotel Test",
        timestamp="2026-01-01T00:00:00",
        schema=SchemaValidation(
            hotel_schema_detected=True, hotel_schema_valid=True,
            hotel_confidence="verified", faq_schema_detected=True,
            faq_schema_valid=True, faq_confidence="verified",
            org_schema_detected=True, total_schemas=3,
        ),
        gbp=GBPData(
            place_found=True, place_id="ChI123", name="Hotel Test",
            rating=4.5, reviews=100, photos=30, phone="+573001234567",
            website="https://hotel-test.com", address="Calle 123, Armenia",
            geo_score=80, geo_score_breakdown={}, confidence="verified",
        ),
        performance=PerformanceData(
            has_field_data=True, mobile_score=85, desktop_score=90,
            lcp=1.5, fid=20, cls=0.05, status="ok", message="OK",
        ),
        validation=CrossValidationResult(
            whatsapp_status="verified",
            phone_web="+573001234567",
            phone_gbp="+573001234567",
            adr_status="verified", adr_web=300000.0, adr_benchmark=280000.0,
            conflicts=[],
        ),
        overall_confidence="verified",
        critical_issues=[], recommendations=[],
    )


class TestSeccion1Conditional:
    """FASE-R0-C (B3): Seccion 1 title and WhatsApp clause are conditional."""

    def test_seccion1_titulo_condicional(self):
        """With conflict: title mentions WhatsApp. Without: it doesn't."""
        gen = V4DiagnosticGenerator()

        # --- With real WhatsApp conflict ---
        audit_conflict = _make_audit_with_whatsapp_conflict()
        assert gen._has_whatsapp_conflict(audit_conflict) is True

        canales_conflict = (
            "WHATSAPP, GOOGLE MAPS E IA"
            if gen._has_whatsapp_conflict(audit_conflict)
            else "GOOGLE MAPS E IA"
        )
        clausula_conflict = (
            " o el número de WhatsApp no responde"
            if gen._has_whatsapp_conflict(audit_conflict)
            else ""
        )

        title_tpl = Template("## 1. 🚨 HOY HAY RESERVAS ESCAPÁNDOSE POR ${seccion_1_canales}")
        clause_tpl = Template(
            "Cada día que pasa, viajeros potenciales buscan su hotel en Google Maps, "
            "le preguntan a ChatGPT o comparan en Booking.com — y algunos se van sin "
            "reservar porque no encuentran lo que buscan${seccion_1_whatsapp_clausula}."
        )

        rendered_title = title_tpl.safe_substitute(seccion_1_canales=canales_conflict)
        rendered_clause = clause_tpl.safe_substitute(seccion_1_whatsapp_clausula=clausula_conflict)

        assert "WHATSAPP, GOOGLE MAPS E IA" in rendered_title
        assert "no responde" in rendered_clause

        # --- Without WhatsApp conflict (Zione-like) ---
        audit_no_conflict = _make_audit_without_whatsapp_conflict()
        assert gen._has_whatsapp_conflict(audit_no_conflict) is False

        canales_no = (
            "WHATSAPP, GOOGLE MAPS E IA"
            if gen._has_whatsapp_conflict(audit_no_conflict)
            else "GOOGLE MAPS E IA"
        )
        clausula_no = (
            " o el número de WhatsApp no responde"
            if gen._has_whatsapp_conflict(audit_no_conflict)
            else ""
        )

        rendered_title_no = title_tpl.safe_substitute(seccion_1_canales=canales_no)
        rendered_clause_no = clause_tpl.safe_substitute(seccion_1_whatsapp_clausula=clausula_no)

        assert "WHATSAPP" not in rendered_title_no
        assert "GOOGLE MAPS E IA" in rendered_title_no
        assert "no responde" not in rendered_clause_no


class TestSeccion6Contador:
    """FASE-R0-C (B5): Section 6 uses dynamic counter, not hardcoded '3'."""

    def test_seccion6_contador_dinamico(self):
        """Template uses ${brechas_total_count} and renders with real N."""
        template_path = (
            Path(__file__).resolve().parent.parent.parent
            / "modules" / "commercial_documents" / "templates"
            / "diagnostico_v6_template.md"
        )
        content = template_path.read_text(encoding="utf-8")

        # The template must contain the dynamic variable
        assert "${brechas_total_count} fugas digitales" in content

        # The template must NOT contain the hardcoded version
        assert "las 3 fugas digitales" not in content.lower()

        # Verify rendering with a realistic value (e.g., 7 for Zione)
        tpl_line = "Detecta las ${brechas_total_count} fugas digitales"
        rendered = Template(tpl_line).safe_substitute(brechas_total_count="7")
        assert "Detecta las 7 fugas digitales" in rendered


class TestTemplateNoHardcodedFugas:
    """FASE-R0-C: Static test — template has no hardcoded fuga strings."""

    def test_template_no_hardcoded_fugas(self):
        """Template .md must not contain any hardcoded fuga references."""
        template_path = (
            Path(__file__).resolve().parent.parent.parent
            / "modules" / "commercial_documents" / "templates"
            / "diagnostico_v6_template.md"
        )
        content = template_path.read_text(encoding="utf-8")
        content_upper = content.upper()

        # B1 (R0-B): "LAS 3 FUGAS" must not exist
        assert "LAS 3 FUGAS" not in content_upper, (
            "Template still contains hardcoded 'LAS 3 FUGAS'"
        )

        # B5 (R0-C): "Detecta las 3 fugas" must not exist
        assert "DETECTA LAS 3 FUGAS" not in content_upper, (
            "Template still contains hardcoded 'Detecta las 3 fugas'"
        )

        # B3 (R0-C): Title line must use ${seccion_1_canales}, not hardcoded channels
        title_lines = [
            line for line in content.splitlines()
            if line.strip().startswith("## 1.")
        ]
        assert len(title_lines) == 1, "Expected exactly one S1 title line"
        title_line = title_lines[0]
        assert "${seccion_1_canales}" in title_line, (
            "S1 title must use ${seccion_1_canales} variable"
        )
        # The title line must NOT have hardcoded "WHATSAPP" (any channel must be parametrized)
        assert "WHATSAPP" not in title_line, (
            "S1 title must not hardcode WHATSAPP — use ${seccion_1_canales}"
        )