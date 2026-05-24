"""
tests/test_assessment_builder.py
NUEVO-8-ASSESSMENT-BUILDER — AssessmentPayload unit tests

Fase: N8-A
12+ tests covering creation, defaults, optionals, and NO zombie fields.
Python path: ./venv/Scripts/python.exe -m pytest
"""

import pytest
from dataclasses import asdict

import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])

from modules.assessment_builder import AssessmentPayload


class TestAssessmentPayloadCreation:
    """T1 + T2: Payload creation with required fields only."""

    def test_payload_creation_defaults(self):
        """Crear con solo url+hotel_name, verificar defaults."""
        payload = AssessmentPayload(
            url="https://www.example.com",
            hotel_name="Hotel Example"
        )
        assert payload.url == "https://www.example.com"
        assert payload.hotel_name == "Hotel Example"
        assert payload.hotel_url == ""
        assert payload.validation_summary == {}
        assert payload.financial_data == {}
        assert payload.financial_sources == {}
        assert payload.financial_evidence_tier == "C"
        assert payload.coherence_score == 0.0
        assert payload.pain_ledger == []
        assert payload.diagnostic_pain_ids == []
        assert payload.proposal_pain_ids == []
        assert payload.audit_schema == {}
        assert payload.critical_issues == []
        assert payload.proposal_services == []
        assert payload.diagnostico_text == ""
        assert payload.propuesta_text == ""
        assert payload.generated_assets == []
        assert payload.evidence_coverage == 0.95
        assert payload.site_presence_report is None
        assert payload.hotel_data == {}


class TestAssessmentPayloadAliases:
    """T2: hotel_url alias de url."""

    def test_payload_hotel_url_alias(self):
        """hotel_url default es \"\" (no url), verificar."""
        payload = AssessmentPayload(
            url="https://www.example.com",
            hotel_name="Hotel Example"
        )
        assert payload.hotel_url == ""  # NO hereda url por defecto


class TestAssessmentPayloadValidation:
    """T3: validation_summary dict anidado."""

    def test_payload_validation_summary(self):
        """Dict anidado en validation_summary."""
        nested = {
            "whatsapp_status": "HIGH",
            "overall_confidence": "HIGH",
            "hard_contradictions_count": 0,
            "conflicts": [{"type": "soft", "severity": "LOW"}],
        }
        payload = AssessmentPayload(
            url="https://www.example.com",
            hotel_name="Hotel Example",
            validation_summary=nested,
        )
        assert payload.validation_summary == nested
        assert payload.validation_summary["whatsapp_status"] == "HIGH"
        assert payload.validation_summary["conflicts"][0]["type"] == "soft"


class TestAssessmentPayloadFinancial:
    """T4: financial_data + financial_evidence_tier."""

    def test_payload_financial_data(self):
        """financial_data dict + financial_evidence_tier string."""
        financial = {
            "rooms": 25,
            "adr_cop": 380000,
            "occupancy_rate": 0.72,
            "direct_channel_percentage": 0.35,
        }
        payload = AssessmentPayload(
            url="https://www.example.com",
            hotel_name="Hotel Example",
            financial_data=financial,
            financial_sources={"booking": "Scraped", "direct": "Onboarding"},
            financial_evidence_tier="B",
        )
        assert payload.financial_data == financial
        assert payload.financial_sources == {"booking": "Scraped", "direct": "Onboarding"}
        assert payload.financial_evidence_tier == "B"


class TestAssessmentPayloadCoherence:
    """T5: coherence_score float."""

    def test_payload_coherence(self):
        """coherence_score float entre 0 y 1."""
        payload = AssessmentPayload(
            url="https://www.example.com",
            hotel_name="Hotel Example",
            coherence_score=0.83,
        )
        assert isinstance(payload.coherence_score, float)
        assert payload.coherence_score == 0.83


class TestAssessmentPayloadPainLedger:
    """T6: pain_ledger lista de dicts."""

    def test_payload_pain_ledger(self):
        """pain_ledger lista de dicts con to_dict()."""
        entries = [
            {"pain_id": "P-001", "severity": "HIGH", "description": "Sin booking directo"},
            {"pain_id": "P-002", "severity": "MEDIUM", "description": "Falta schema markup"},
        ]
        payload = AssessmentPayload(
            url="https://www.example.com",
            hotel_name="Hotel Example",
            pain_ledger=entries,
            diagnostic_pain_ids=["P-001"],
            proposal_pain_ids=["P-001", "P-002"],
        )
        assert payload.pain_ledger == entries
        assert payload.diagnostic_pain_ids == ["P-001"]
        assert payload.proposal_pain_ids == ["P-001", "P-002"]


class TestAssessmentPayloadAudit:
    """T7: audit_schema + critical_issues."""

    def test_payload_audit(self):
        """audit_schema dict + critical_issues lista."""
        audit = {
            "hotel_schema_detected": True,
            "hotel_schema_valid": True,
            "hotel_confidence": 0.95,
            "faq_schema_detected": False,
            "faq_schema_valid": False,
            "faq_confidence": 0.0,
        }
        issues = ["Google Business Profile no verificado", "Falta FAQ schema"]
        payload = AssessmentPayload(
            url="https://www.example.com",
            hotel_name="Hotel Example",
            audit_schema=audit,
            critical_issues=issues,
        )
        assert payload.audit_schema == audit
        assert payload.critical_issues == issues
        assert payload.audit_schema["hotel_schema_detected"] is True


class TestAssessmentPayloadDocuments:
    """T8: diagnostico_text + propuesta_text strings."""

    def test_payload_documents(self):
        """diagnostico_text + propuesta_text strings."""
        payload = AssessmentPayload(
            url="https://www.example.com",
            hotel_name="Hotel Example",
            diagnostico_text="# Diagnóstico\n\nHotel sin presencia en...",
            propuesta_text="# Propuesta\n\nImplementar schema markup...",
        )
        assert isinstance(payload.diagnostico_text, str)
        assert isinstance(payload.propuesta_text, str)
        assert "Diagnóstico" in payload.diagnostico_text
        assert "Propuesta" in payload.propuesta_text


class TestAssessmentPayloadAssets:
    """T9: generated_assets + evidence_coverage."""

    def test_payload_assets(self):
        """generated_assets lista + evidence_coverage float."""
        assets = [
            {"asset_type": "hotel_schema", "filename": "hotel_schema.json",
             "confidence_score": 0.95, "preflight_status": "PASSED"},
            {"asset_type": "geo_media", "filename": "geo_media.json",
             "confidence_score": 0.80, "preflight_status": "PASSED"},
        ]
        payload = AssessmentPayload(
            url="https://www.example.com",
            hotel_name="Hotel Example",
            generated_assets=assets,
            evidence_coverage=0.88,
        )
        assert payload.generated_assets == assets
        assert payload.evidence_coverage == 0.88
        assert len(payload.generated_assets) == 2


class TestAssessmentPayloadSitePresence:
    """T10: site_presence_report opcional."""

    def test_payload_site_presence(self):
        """site_presence_report opcional (None default)."""
        payload = AssessmentPayload(
            url="https://www.example.com",
            hotel_name="Hotel Example",
            site_presence_report={
                "presence_status": "present",
                "assets_checked": {"hotel_schema": "present"},
            },
        )
        assert payload.site_presence_report is not None
        assert payload.site_presence_report["presence_status"] == "present"


class TestAssessmentPayloadNoZombieFields:
    """T11: Verificar que NO existen zombie fields."""

    def test_payload_no_zombie_fields(self):
        """NO existen: quality_gate_*, coherence_checks, coherence_errors,
        coherence_warnings, critical_issues_detected, metrics, coherence_report."""
        payload = AssessmentPayload(
            url="https://www.example.com",
            hotel_name="Hotel Example",
        )
        # Estos campos no existen como atributos del dataclass
        assert not hasattr(payload, "quality_gate_issues")
        assert not hasattr(payload, "quality_gate_blockers")
        assert not hasattr(payload, "quality_gate_warnings")
        assert not hasattr(payload, "coherence_checks")
        assert not hasattr(payload, "coherence_errors")
        assert not hasattr(payload, "coherence_warnings")
        assert not hasattr(payload, "critical_issues_detected")
        assert not hasattr(payload, "metrics")
        assert not hasattr(payload, "coherence_report")


class TestAssessmentPayloadSerialization:
    """T12: dataclasses.asdict() produce dict esperado."""

    def test_payload_serialization(self):
        """dataclasses.asdict() produce dict con todos los campos."""
        payload = AssessmentPayload(
            url="https://www.example.com",
            hotel_name="Hotel Example",
            coherence_score=0.83,
            financial_evidence_tier="B",
            evidence_coverage=0.95,
            critical_issues=["GBP no verificado"],
            site_presence_report={"presence_status": "unknown"},
        )
        d = asdict(payload)

        assert isinstance(d, dict)
        assert d["url"] == "https://www.example.com"
        assert d["hotel_name"] == "Hotel Example"
        assert d["coherence_score"] == 0.83
        assert d["financial_evidence_tier"] == "B"
        assert d["evidence_coverage"] == 0.95
        assert d["critical_issues"] == ["GBP no verificado"]
        assert d["site_presence_report"] == {"presence_status": "unknown"}
        # Verify no extra/zombie keys
        assert "quality_gate_issues" not in d
        assert "metrics" not in d
        assert "coherence_report" not in d


# ─── AssessmentBuilder tests (N8-B) ──────────────────────────────────────────

import tempfile
import os
from unittest.mock import MagicMock

from modules.assessment_builder import AssessmentBuilder


class TestAssessmentBuilderWithCore:
    """T1: test_builder_with_core"""

    def test_builder_with_core(self):
        b = AssessmentBuilder()
        b.with_core("https://www.example.com", "Hotel Example")
        assert b._payload.url == "https://www.example.com"
        assert b._payload.hotel_name == "Hotel Example"
        assert b._payload.hotel_url == "https://www.example.com"

    def test_builder_with_core_alias(self):
        b = AssessmentBuilder()
        b.with_core("https://www.hotel.com", "Hotel Test")
        assert b._payload.hotel_url == b._payload.url


class TestAssessmentBuilderWithValidation:
    """T2: test_builder_with_validation"""

    def test_builder_with_validation(self):
        validation_summary = {
            "whatsapp_status": "HIGH",
            "overall_confidence": "HIGH",
            "hard_contradictions_count": 0,
            "conflicts": [],
        }
        b = AssessmentBuilder()
        b.with_validation(validation_summary, None)
        assert b._payload.validation_summary == validation_summary
        assert b._payload.validation_summary["whatsapp_status"] == "HIGH"


class TestAssessmentBuilderWithFinancial:
    """T3: test_builder_with_financial"""

    def test_builder_with_financial(self):
        b = AssessmentBuilder()
        b.with_financial(
            rooms=25,
            adr_cop=380000,
            occupancy_rate=0.72,
            direct_channel_pct=0.35,
            financial_sources={"booking": "Scraped"},
            financial_breakdown=None,
        )
        assert b._payload.financial_data["rooms"] == 25
        assert b._payload.financial_data["adr_cop"] == 380000
        assert b._payload.financial_data["occupancy_rate"] == 0.72
        assert b._payload.financial_data["direct_channel_percentage"] == 0.35
        assert b._payload.financial_sources == {"booking": "Scraped"}
        assert b._payload.financial_evidence_tier == "C"

    def test_builder_with_financial_breakdown_tier(self):
        mock_fb = MagicMock()
        mock_fb.evidence_tier = "B"
        b = AssessmentBuilder()
        b.with_financial(20, 400000, 0.80, 0.40, {}, mock_fb)
        assert b._payload.financial_evidence_tier == "B"


class TestAssessmentBuilderWithCoherence:
    """T4-T5: test_builder_with_coherence"""

    def test_builder_with_coherence(self):
        mock_asset = MagicMock()
        mock_asset.coherence_report.overall_score = 0.83
        b = AssessmentBuilder()
        b.with_coherence(None, mock_asset)
        assert b._payload.coherence_score == 0.83

    def test_builder_with_coherence_no_asset_result(self):
        b = AssessmentBuilder()
        b.with_coherence(None, None)
        assert b._payload.coherence_score == 0.0


class TestAssessmentBuilderWithPainLedger:
    """T6-T7: test_builder_with_pain_ledger"""

    def test_builder_with_pain_ledger(self):
        entry1 = MagicMock()
        entry1.to_dict.return_value = {
            "pain_id": "P-001", "severity": "HIGH", "description": "Test"
        }
        entry2 = {"pain_id": "P-002", "severity": "MEDIUM"}
        mock_ds = MagicMock()
        mock_ds.pain_ids = ["P-001"]
        mock_ap = [MagicMock(pain_ids=["P-001", "P-002"])]

        b = AssessmentBuilder()
        b.with_pain_ledger([entry1, entry2], mock_ds, mock_ap)

        assert len(b._payload.pain_ledger) == 2
        assert b._payload.pain_ledger[0]["pain_id"] == "P-001"
        assert b._payload.pain_ledger[1]["pain_id"] == "P-002"
        assert b._payload.diagnostic_pain_ids == ["P-001"]
        assert set(b._payload.proposal_pain_ids) == {"P-001", "P-002"}

    def test_builder_with_pain_ledger_no_diagnostic(self):
        b = AssessmentBuilder()
        b.with_pain_ledger([], None, None)
        assert b._payload.diagnostic_pain_ids == []
        assert b._payload.proposal_pain_ids == []


class TestAssessmentBuilderWithAudit:
    """T8-T9: test_builder_with_audit"""

    def test_builder_with_audit(self):
        mock_audit = MagicMock()
        mock_audit.critical_issues = ["GBP no verificado"]
        mock_audit.schema.hotel_schema_detected = True
        mock_audit.schema.hotel_schema_valid = True
        mock_audit.schema.hotel_confidence = 0.95
        mock_audit.schema.faq_schema_detected = False
        mock_audit.schema.faq_schema_valid = False
        mock_audit.schema.faq_confidence = 0.0

        b = AssessmentBuilder()
        b.with_audit(mock_audit)
        assert b._payload.critical_issues == ["GBP no verificado"]
        assert b._payload.audit_schema["hotel_schema_detected"] is True
        assert b._payload.audit_schema["faq_confidence"] == 0.0

    def test_builder_with_audit_none(self):
        b = AssessmentBuilder()
        b.with_audit(None)
        assert b._payload.audit_schema == {}
        assert b._payload.critical_issues == []


class TestAssessmentBuilderWithDocuments:
    """T10-T11: test_builder_with_documents"""

    def test_builder_with_documents(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write("# Diagnostico\n\nContenido de prueba")
            diag_path = f.name
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write("# Propuesta\n\nContenido de propuesta")
            prop_path = f.name

        try:
            b = AssessmentBuilder()
            b.with_documents(diag_path, prop_path)
            assert "# Diagnostico" in b._payload.diagnostico_text
            assert "Propuesta" in b._payload.propuesta_text
        finally:
            os.unlink(diag_path)
            os.unlink(prop_path)

    def test_builder_with_documents_missing(self):
        b = AssessmentBuilder()
        b.with_documents("/no/existe/diagnostico.md", "/no/existe/propuesta.md")
        assert b._payload.diagnostico_text == ""
        assert b._payload.propuesta_text == ""


class TestAssessmentBuilderWithAssets:
    """T12: test_builder_with_assets"""

    def test_builder_with_assets(self):
        mock_asset = MagicMock()
        mock_asset.asset_type = "hotel_schema"
        mock_asset.filename = "hotel_schema.json"
        mock_asset.confidence_score = 0.95
        mock_asset.preflight_status = "PASSED"
        mock_asset.path = "/output/hotel_schema.json"

        mock_result = MagicMock()
        mock_result.generated_assets = [mock_asset]

        b = AssessmentBuilder()
        b.with_assets(mock_result)
        assert len(b._payload.generated_assets) == 1
        assert b._payload.generated_assets[0]["asset_type"] == "hotel_schema"
        assert b._payload.generated_assets[0]["confidence_score"] == 0.95


class TestAssessmentBuilderWithSitePresence:
    """T13: test_builder_with_site_presence"""

    def test_builder_with_site_presence(self):
        report = {"presence_status": "present", "assets_checked": {}}
        b = AssessmentBuilder()
        b.with_site_presence(report)
        assert b._payload.site_presence_report == report


class TestAssessmentBuilderWithHotelData:
    """T14: test_builder_with_hotel_data"""

    def test_builder_with_hotel_data(self):
        b = AssessmentBuilder()
        b.with_hotel_data("eje_cafetero")
        assert b._payload.hotel_data == {"region": "Eje Cafetero"}

    def test_builder_with_hotel_data_empty(self):
        b = AssessmentBuilder()
        b.with_hotel_data("")
        assert b._payload.hotel_data == {}


class TestAssessmentBuilderBuild:
    """T15-T17: test_builder_build_*"""

    def test_builder_build_valid(self):
        b = AssessmentBuilder()
        b.with_core("https://www.example.com", "Hotel Test")
        b.with_financial(20, 300000, 0.70, 0.30, {}, None)
        result = b.build()
        assert isinstance(result, dict)
        assert result["url"] == "https://www.example.com"
        assert result["hotel_name"] == "Hotel Test"
        assert result["financial_data"]["rooms"] == 20
        assert "coherence_score" in result

    def test_builder_build_missing_url(self):
        b = AssessmentBuilder()
        b.with_core("", "Hotel Test")
        with pytest.raises(ValueError, match="url es requerido"):
            b.build()

    def test_builder_build_missing_hotel_name(self):
        b = AssessmentBuilder()
        b.with_core("https://www.example.com", "")
        with pytest.raises(ValueError, match="hotel_name es requerido"):
            b.build()


class TestAssessmentBuilderFullPipeline:
    """T18: test_builder_full_pipeline"""

    def test_builder_full_pipeline(self):
        mock_asset = MagicMock()
        mock_asset.coherence_report.overall_score = 0.83
        mock_asset.generated_assets = []

        mock_audit = MagicMock()
        mock_audit.critical_issues = []
        mock_audit.schema.hotel_schema_detected = True
        mock_audit.schema.hotel_schema_valid = True
        mock_audit.schema.hotel_confidence = 0.90
        mock_audit.schema.faq_schema_detected = False
        mock_audit.schema.faq_schema_valid = False
        mock_audit.schema.faq_confidence = 0.0

        mock_ds = MagicMock()
        mock_ds.pain_ids = ["P-001"]

        mock_ap = [MagicMock(pain_ids=["P-001"])]

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write("# Diag")
            diag_path = f.name
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write("# Prop")
            prop_path = f.name

        try:
            b = AssessmentBuilder()
            b.with_core("https://www.hotel.com", "Hotel Completo")
            b.with_validation({"whatsapp_status": "HIGH", "overall_confidence": "HIGH", "conflicts": []}, None)
            b.with_financial(30, 450000, 0.75, 0.40, {"direct": "Scraped"}, None)
            b.with_coherence(None, mock_asset)
            b.with_pain_ledger([], mock_ds, mock_ap)
            b.with_audit(mock_audit)
            b.with_documents(diag_path, prop_path)
            b.with_assets(mock_asset)
            b.with_site_presence({"presence_status": "present"})
            b.with_hotel_data("bogota")

            result = b.build()

            assert result["url"] == "https://www.hotel.com"
            assert result["hotel_name"] == "Hotel Completo"
            assert result["hotel_url"] == "https://www.hotel.com"
            assert result["coherence_score"] == 0.83
            assert result["diagnostic_pain_ids"] == ["P-001"]
            assert result["audit_schema"]["hotel_schema_detected"] is True
            assert "# Diag" in result["diagnostico_text"]
            assert result["hotel_data"]["region"] == "Bogota"
            assert result["site_presence_report"]["presence_status"] == "present"
        finally:
            os.unlink(diag_path)
            os.unlink(prop_path)