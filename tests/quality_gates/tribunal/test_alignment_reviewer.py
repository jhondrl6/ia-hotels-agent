"""Tests para alignment_reviewer.py — Bot 2 del tribunal.

Valida la clasificación de promesas verbales contra la matriz, la detección
de S-C4 (tabla de assets técnicos), y la serialización del reporte.
"""

import json
import pytest
from pathlib import Path

from modules.quality_gates.tribunal.alignment_reviewer import (
    AlignmentReviewer,
    STATUS_ALINEADO,
    STATUS_SIN_BRECHA,
    STATUS_PROMESA_SIN_MATRIZ,
    VERDICT_APROBADO,
    VERDICT_BLOQUEAR,
    VERDICT_DEVOLVER,
)
from modules.quality_gates.tribunal.llm_extractor import (
    MockPromiseExtractor,
    VerbalPromise,
)


@pytest.fixture
def v4_audit_dir(tmp_path):
    """Directorio temporal con artefactos mínimos para tests."""
    return tmp_path


@pytest.fixture
def sample_proposal(v4_audit_dir):
    """Propuesta comercial ficticia."""
    proposal = """# PROPUESTA COMERCIAL
## Hotel Salento Real

## La Solución

Le proponemos un plan integral donde **nosotros implementamos todo**:

### Servicios incluidos:
- Botón de WhatsApp para reservas directas
- Página de FAQ optimizada para SEO
- Schema Hotel para rich results

### Estado de los Entregables

| Servicio | Estado |
|----------|--------|
| WhatsApp | ✅ Generado |
| FAQ | ✅ Generado |

### Assets Técnicos Adicionales

Estos assets técnicos complementan su kit de hospitalidad digital:

| Asset Técnico | Estado | Descripción |
|---------------|--------|-------------|
| Guía Analytics | ✅ Generado | Configuración de Google Analytics |
| Optimización Tráfico | ⏳ No generado | Análisis de tráfico indirecto |
"""
    path = v4_audit_dir / "02_PROPUESTA_COMERCIAL_20260911.md"
    path.write_text(proposal, encoding="utf-8")
    return path


@pytest.fixture
def sample_matrix(v4_audit_dir):
    """Matriz proposal_asset_matrix.json ficticia."""
    matrix = {
        "proposal_asset_matrix_version": "2.1",
        "entries": [
            {
                "service_name": "Botón de WhatsApp",
                "pain_ids": ["no_whatsapp_visible"],
                "asset_type": "whatsapp_button",
                "asset_path": "/path/to/whatsapp.html",
                "confidence": 0.95,
                "status": "LINKED",
                "alignment": "linked",
            },
            {
                "service_name": "Página de FAQ",
                "pain_ids": [],
                "asset_type": "faq_page",
                "asset_path": "/path/to/faq.html",
                "confidence": 0.85,
                "status": "LINKED",
                "alignment": "linked",
            },
            {
                "service_name": "Schema Hotel",
                "pain_ids": ["no_schema_detected"],
                "asset_type": "hotel_schema",
                "asset_path": None,
                "confidence": 0.0,
                "status": "PRESENT_IN_PRODUCTION",
                "alignment": "present_in_production",
            },
        ],
        "summary": {"promised": 3, "not_promised": 0, "unknown": 0},
    }
    path = v4_audit_dir / "proposal_asset_matrix.json"
    path.write_text(json.dumps(matrix, ensure_ascii=False), encoding="utf-8")
    return path


class TestAlignmentReviewer:
    """Tests para AlignmentReviewer."""

    def test_promise_without_matrix_detected(self, v4_audit_dir, sample_proposal, sample_matrix):
        """Mock extrae 'implementación de chatbot' → no está en matriz → PROMESA-SIN-MATRIZ."""
        promises = [
            VerbalPromise("implementación de chatbot", "chatbot", "Intro", 0.9),
        ]
        mock_extractor = MockPromiseExtractor(promises)

        reviewer = AlignmentReviewer(v4_audit_dir)
        report = reviewer.review(extractor=mock_extractor)

        chatbot_rows = [r for r in report["service_matrix"] if r["service"] == "chatbot"]
        assert len(chatbot_rows) == 1
        row = chatbot_rows[0]
        assert row["status"] == STATUS_PROMESA_SIN_MATRIZ
        assert row["matrix_entry_found"] is False
        assert row["verbal_promise_found"] is True
        assert len([f for f in report["findings"] if f["finding_type"] == "PROMESA_SIN_MATRIZ"]) == 1
        assert report["verdict_recommendation"] == VERDICT_DEVOLVER

    def test_aligned_service_not_flagged(self, v4_audit_dir, sample_proposal, sample_matrix):
        """Servicio con brecha + entrada en matriz → ALINEADO."""
        promises = [
            VerbalPromise("Botón de WhatsApp", "whatsapp", "Intro", 0.95),
        ]
        mock_extractor = MockPromiseExtractor(promises)

        reviewer = AlignmentReviewer(v4_audit_dir)
        report = reviewer.review(extractor=mock_extractor)

        whatsapp_rows = [r for r in report["service_matrix"] if r["service"] == "whatsapp"]
        assert len(whatsapp_rows) == 1
        assert whatsapp_rows[0]["status"] == STATUS_ALINEADO
        assert whatsapp_rows[0]["pain_id"] == "no_whatsapp_visible"
        assert whatsapp_rows[0]["matrix_entry_found"] is True
        assert whatsapp_rows[0]["verbal_promise_found"] is True

    def test_no_breach_associated_detected(self, v4_audit_dir, sample_proposal, sample_matrix):
        """Entrada LINKED en matriz sin pain_id → SIN-BRECHA-ASOCIADA."""
        promises = [
            VerbalPromise("Página de FAQ", "faq", "Entregables", 0.85),
        ]
        mock_extractor = MockPromiseExtractor(promises)

        reviewer = AlignmentReviewer(v4_audit_dir)
        report = reviewer.review(extractor=mock_extractor)

        faq_rows = [r for r in report["service_matrix"] if r["service"] == "faq"]
        assert len(faq_rows) == 1
        assert faq_rows[0]["status"] == STATUS_SIN_BRECHA
        assert faq_rows[0]["finding"] == "Servicio LINKED sin pain_id asociado"
        assert any(f["finding_type"] == "SIN_BRECHA_ASOCIADA" for f in report["findings"])

    def test_present_in_production_aligned(self, v4_audit_dir, sample_proposal, sample_matrix):
        """Servicio PRESENT_IN_PRODUCTION → ALINEADO con nota."""
        promises = [
            VerbalPromise("Schema Hotel", "schema", "Entregables", 0.9),
        ]
        mock_extractor = MockPromiseExtractor(promises)

        reviewer = AlignmentReviewer(v4_audit_dir)
        report = reviewer.review(extractor=mock_extractor)

        schema_rows = [r for r in report["service_matrix"] if r["service"] == "schema"]
        assert len(schema_rows) == 1
        assert schema_rows[0]["status"] == STATUS_ALINEADO
        assert schema_rows[0]["finding"] == "Presente en producción"

    def test_s_c4_asset_table_detected(self, v4_audit_dir, sample_proposal, sample_matrix):
        """Tabla de assets técnicos incondicional → finding S-C4."""
        mock_extractor = MockPromiseExtractor([])

        reviewer = AlignmentReviewer(v4_audit_dir)
        report = reviewer.review(extractor=mock_extractor)

        s_c4_findings = [f for f in report["findings"] if f["finding_type"] == "S_C4_TECHNICAL_ASSETS_TABLE"]
        assert len(s_c4_findings) == 1
        assert s_c4_findings[0]["severity"] == "INFO"
        assert "tercera superficie de promesa" in s_c4_findings[0]["description"]

    def test_serialization_to_disk(self, v4_audit_dir, sample_proposal, sample_matrix):
        """JSON escrito y re-leído (R2.4)."""
        mock_extractor = MockPromiseExtractor([])

        reviewer = AlignmentReviewer(v4_audit_dir)
        output_path = reviewer.write_report(extractor=mock_extractor)

        assert output_path.exists()
        with open(output_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded["reviewer"] == "alignment_reviewer"
        assert loaded["clause"] == "P6.2"
        assert "service_matrix" in loaded
        assert "findings" in loaded
        assert "summary" in loaded
        assert "verdict_recommendation" in loaded

    def test_summary_counts(self, v4_audit_dir, sample_proposal, sample_matrix):
        """Summary cuenta clasificaciones con cruce bidireccional.

        Promesas: WhatsApp→ALINEADO, FAQ→SIN-BRECHA, Chatbot→PROMESA-SIN-MATRIZ.
        Entradas sin promesa: Schema Hotel (PRESENT_IN_PRODUCTION)→ALINEADO.
        """
        promises = [
            VerbalPromise("WhatsApp", "whatsapp", "Intro", 0.95),
            VerbalPromise("FAQ", "faq", "Entregables", 0.85),
            VerbalPromise("Chatbot", "chatbot", "Intro", 0.9),
        ]
        mock_extractor = MockPromiseExtractor(promises)

        reviewer = AlignmentReviewer(v4_audit_dir)
        report = reviewer.review(extractor=mock_extractor)

        summary = report["summary"]
        assert summary["aligned"] == 2
        assert summary["no_breach"] == 1
        assert summary["promise_without_matrix"] == 1
        assert summary["total"] == 4
        assert summary["no_breach_info"] == 0

    def test_verdict_bloquear_on_critical(self, v4_audit_dir):
        """Veredicto BLOQUEAR cuando falta artefacto crítico."""
        reviewer = AlignmentReviewer(v4_audit_dir)
        report = reviewer.review()

        assert report["verdict_recommendation"] == VERDICT_BLOQUEAR
        assert report["findings"][0]["finding_type"] == "MISSING_ARTIFACT"

    def test_verdict_aprobado_no_findings(self, v4_audit_dir):
        """APROBADO con fixture limpio: sin tabla S-C4 y única entrada LINKED+pain_id."""
        proposal = "# PROPUESTA\n\nIncluimos el Botón de WhatsApp para su hotel.\n"
        (v4_audit_dir / "02_PROPUESTA_COMERCIAL_LIMPIA.md").write_text(proposal, encoding="utf-8")
        matrix = {"entries": [{
            "service_name": "Botón de WhatsApp",
            "pain_ids": ["no_whatsapp_visible"],
            "status": "LINKED",
        }]}
        (v4_audit_dir / "proposal_asset_matrix.json").write_text(
            json.dumps(matrix, ensure_ascii=False), encoding="utf-8"
        )

        mock_extractor = MockPromiseExtractor([
            VerbalPromise("Botón de WhatsApp", "whatsapp", "Intro", 0.95),
        ])
        reviewer = AlignmentReviewer(v4_audit_dir)
        report = reviewer.review(extractor=mock_extractor)

        assert report["findings"] == []
        assert report["verdict_recommendation"] == VERDICT_APROBADO

    def test_no_breach_not_a_finding(self, v4_audit_dir):
        """NO_BREACH sin promesa: estado legítimo, no es hallazgo (solo info)."""
        proposal = "# Propuesta\n\nSolo prometemos el Botón de WhatsApp.\n"
        (v4_audit_dir / "02_PROPUESTA_COMERCIAL_NOBREACH.md").write_text(proposal, encoding="utf-8")
        matrix = {"entries": [
            {"service_name": "Botón de WhatsApp", "pain_ids": ["no_whatsapp_visible"], "status": "LINKED"},
            {"service_name": "Guía Analytics", "pain_ids": [], "status": "NO_BREACH"},
        ]}
        (v4_audit_dir / "proposal_asset_matrix.json").write_text(
            json.dumps(matrix, ensure_ascii=False), encoding="utf-8"
        )

        mock_extractor = MockPromiseExtractor([
            VerbalPromise("Botón de WhatsApp", "whatsapp", "Intro", 0.95),
        ])
        reviewer = AlignmentReviewer(v4_audit_dir)
        report = reviewer.review(extractor=mock_extractor)

        services = [r["service"] for r in report["service_matrix"]]
        assert "Guía Analytics" not in services
        assert report["findings"] == []
        assert report["summary"]["no_breach_info"] == 1
        assert report["verdict_recommendation"] == VERDICT_APROBADO

    def test_promise_on_no_breach_entry_flagged(self, v4_audit_dir):
        """Promesa sobre entrada NO_BREACH → servicio vendido sin brecha (§5.2)."""
        proposal = "# Propuesta\n\nTambién prometemos un chatbot con IA.\n"
        (v4_audit_dir / "02_PROPUESTA_COMERCIAL_PNOB.md").write_text(proposal, encoding="utf-8")
        matrix = {"entries": [
            {"service_name": "Chatbot IA", "pain_ids": [], "status": "NO_BREACH"},
        ]}
        (v4_audit_dir / "proposal_asset_matrix.json").write_text(
            json.dumps(matrix, ensure_ascii=False), encoding="utf-8"
        )

        mock_extractor = MockPromiseExtractor([
            VerbalPromise("implementación de chatbot IA", "chatbot_ia", "Intro", 0.9),
        ])
        reviewer = AlignmentReviewer(v4_audit_dir)
        report = reviewer.review(extractor=mock_extractor)

        rows = [r for r in report["service_matrix"] if r["service"] == "chatbot_ia"]
        assert len(rows) == 1
        assert rows[0]["status"] == STATUS_SIN_BRECHA
        assert rows[0]["finding"] == "Servicio vendido sin brecha asociada (NO_BREACH)"
        assert any(f["finding_type"] == "SIN_BRECHA_ASOCIADA" for f in report["findings"])
        assert report["verdict_recommendation"] == VERDICT_DEVOLVER

    def test_matrix_entries_covered_without_promise(self, v4_audit_dir, sample_proposal, sample_matrix):
        """Cruce inverso: entradas sin promesa reciben fila con verbal_promise_found=false."""
        mock_extractor = MockPromiseExtractor([
            VerbalPromise("Botón de WhatsApp", "whatsapp", "Intro", 0.95),
        ])
        reviewer = AlignmentReviewer(v4_audit_dir)
        report = reviewer.review(extractor=mock_extractor)

        rows_by_service = {r["service"]: r for r in report["service_matrix"]}
        assert rows_by_service["Página de FAQ"]["verbal_promise_found"] is False
        assert rows_by_service["Página de FAQ"]["status"] == STATUS_SIN_BRECHA
        assert rows_by_service["Schema Hotel"]["verbal_promise_found"] is False
        assert rows_by_service["Schema Hotel"]["status"] == STATUS_ALINEADO
        assert any(f["finding_type"] == "SIN_BRECHA_ASOCIADA" for f in report["findings"])

    def test_promise_without_matrix_escalates_verdict(self, v4_audit_dir, sample_proposal, sample_matrix):
        """Un solo PROMESA-SIN-MATRIZ escala la recomendación a DEVOLVER-PRUEBAS."""
        mock_extractor = MockPromiseExtractor([
            VerbalPromise("auditoría de reseñas externas", "tripadvisor_reviews", "Intro", 0.8),
        ])
        reviewer = AlignmentReviewer(v4_audit_dir)
        report = reviewer.review(extractor=mock_extractor)

        assert any(r["status"] == STATUS_PROMESA_SIN_MATRIZ for r in report["service_matrix"])
        assert report["verdict_recommendation"] == VERDICT_DEVOLVER
