"""Tests para HonestyReviewer (Bot 4 del tribunal).

Tests obligatorios:
- test_reads_both_commercial_files: Fixture con 2 archivos → total_cg_count: 12
- test_cg_whatsapp_lead_detected: CG-WHATSAPP-LEAD en diagnóstico → finding CG_WARNING_UNDISCLOSED
- test_over_presentation_detected: Mock extrae "cifras verificadas" con tier B → OVER_PRESENTATION
- test_missing_scenario_detected: Fixture con solo escenario optimista → MISSING_SCENARIO
- test_tier_mismatch_detected: Claim con tier declarado ≠ tier real → TIER_MISMATCH
- test_serialization_to_disk: JSON escrito y re-leído (R2.4)
- test_mock_extractor_no_real_llm: Tests no llaman LLM real
"""

import json
from pathlib import Path

import pytest

from modules.quality_gates.tribunal.honesty_reviewer import (
    FINDING_CG_WARNING_UNDISCLOSED,
    FINDING_MISSING_SCENARIO,
    FINDING_OVER_PRESENTATION,
    FINDING_TIER_MISMATCH,
    HonestyReviewer,
)
from modules.quality_gates.tribunal.llm_extractor import (
    MockPromiseExtractor,
    VerbalPromise,
)


@pytest.fixture
def sample_v4_audit_dir(tmp_path):
    """Fixture con estructura completa de v4_audit para HonestyReviewer."""
    v4_audit = tmp_path / "v4_audit"
    v4_audit.mkdir()

    commercial_gates_canonical = {
        "all_passed": True,
        "blocking_passed": True,
        "results": [
            {
                "gate_id": "CG-ROI-NEGATIVE",
                "name": "ROI negativo como argumento de cierre",
                "passed": True,
                "severity": "BLOCKING",
                "message": "Beneficio neto 6m positivo: $3,047,608 COP.",
                "suggestion": "",
            },
            {
                "gate_id": "CG-OTA-NARRATIVE",
                "name": "Sin narrativa OTA",
                "passed": True,
                "severity": "WARNING",
                "message": "Términos OTA encontrados: Booking, Expedia, comisión.",
                "suggestion": "",
            },
            {
                "gate_id": "CG-TECH-JARGON",
                "name": "Jerga técnica en vista gerencia",
                "passed": True,
                "severity": "WARNING",
                "message": "No se encontró jerga técnica en las primeras secciones.",
                "suggestion": "",
            },
        ],
        "summary": "All commercial gates passed.",
    }

    commercial_gates_diagnostic = {
        "all_passed": False,
        "blocking_passed": True,
        "results": [
            {
                "gate_id": "CG-SCENARIO-ORDER",
                "name": "Orden de escenarios inválido",
                "passed": True,
                "severity": "BLOCKING",
                "message": "Orden de escenarios válido.",
                "suggestion": "",
            },
            {
                "gate_id": "CG-SCENARIO-NEGATIVE",
                "name": "Escenario negativo como recuperación",
                "passed": True,
                "severity": "BLOCKING",
                "message": "Escenario optimista no es negativo.",
                "suggestion": "",
            },
            {
                "gate_id": "CG-IA-BLOCKED-CLAIM",
                "name": "\"IA Bloqueada\" sin evidencia",
                "passed": True,
                "severity": "BLOCKING",
                "message": "No se encontró claim de 'IA Bloqueada'.",
                "suggestion": "",
            },
            {
                "gate_id": "CG-CLAIM-VS-EVIDENCE",
                "name": "Claims no soportados por datos",
                "passed": True,
                "severity": "BLOCKING",
                "message": "No se encontraron claims factuales.",
                "suggestion": "",
            },
            {
                "gate_id": "CG-WHATSAPP-LEAD",
                "name": "WhatsApp no lidera narrativa",
                "passed": False,
                "severity": "WARNING",
                "message": "WhatsApp no aparece en la sección inicial del diagnóstico.",
                "suggestion": "Abrir diagnóstico con conflicto WhatsApp.",
            },
            {
                "gate_id": "CG-OTA-NARRATIVE",
                "name": "Sin narrativa OTA",
                "passed": True,
                "severity": "WARNING",
                "message": "Términos OTA encontrados: Booking, Expedia.",
                "suggestion": "",
            },
            {
                "gate_id": "CG-TIER-CONSISTENCY",
                "name": "Tier inconsistente",
                "passed": True,
                "severity": "WARNING",
                "message": "Tier consistente: 'B' en frontmatter y texto.",
                "suggestion": "",
            },
            {
                "gate_id": "CG-EVIDENCE-TIER-CONSISTENCY",
                "name": "Evidencia Tier vs GA4/GSC",
                "passed": True,
                "severity": "INFO",
                "message": "Tier B no requiere verificación GA4/GSC.",
                "suggestion": "",
            },
            {
                "gate_id": "CG-TECH-JARGON",
                "name": "Jerga técnica en vista gerencia",
                "passed": True,
                "severity": "WARNING",
                "message": "No se encontró jerga técnica.",
                "suggestion": "",
            },
        ],
        "summary": "1 WARNING(s): CG-WHATSAPP-LEAD",
    }

    financial_scenarios = {
        "hotel": "Hotelsalentoreal",
        "url": "https://www.hotelsalentoreal.com/",
        "input_data": {
            "rooms": 10,
            "adr_cop": 280000,
            "adr_source": "regional_v410",
            "occupancy_rate": 0.512,
            "direct_channel_percentage": 0.2,
        },
        "scenarios": {
            "conservative": 6571622.4,
            "realistic": 4042752.0,
            "optimistic": 1264435.2,
        },
        "expected_monthly_cop": 4042752.0,
        "breakdown": {
            "evidence_tier": "B",
            "disclaimer": "Estimación basada en benchmarks regionales.",
        },
        "precision_tier": "C",
    }

    proposal_text = """# Propuesta Comercial

## Introducción
Ofrecemos soluciones verificadas para su hotel.

## Alcance
Implementación de chatbot con datos confirmados del mercado.
"""

    (v4_audit / "commercial_gates_report.json").write_text(
        json.dumps(commercial_gates_canonical, indent=2), encoding="utf-8"
    )
    (v4_audit / "commercial_gates_report_diagnostic_20260904_120413.json").write_text(
        json.dumps(commercial_gates_diagnostic, indent=2), encoding="utf-8"
    )
    (v4_audit / "financial_scenarios_20260904_120404.json").write_text(
        json.dumps(financial_scenarios, indent=2), encoding="utf-8"
    )
    (v4_audit / "02_PROPUESTA_COMERCIAL_20260904_120413.md").write_text(proposal_text, encoding="utf-8")

    deliveries = tmp_path / "deliveries" / "hotelsalentoreal_20260904"
    deliveries.mkdir(parents=True)
    manifest = {
        "quality_metadata": {
            "evidence_tier": "B",
            "precision_tier": "C",
            "coherence_score": 0.91,
        }
    }
    (deliveries / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return v4_audit


@pytest.fixture
def mock_extractor():
    """MockPromiseExtractor con claims de prueba."""
    promises = [
        VerbalPromise(
            text="soluciones verificadas para su hotel",
            service_hint="general",
            location="Introducción",
            confidence=0.9,
        ),
        VerbalPromise(
            text="datos confirmados del mercado",
            service_hint="whatsapp_bot",
            location="Alcance",
            confidence=0.85,
        ),
    ]
    return MockPromiseExtractor(promises)


def test_reads_both_commercial_files(sample_v4_audit_dir):
    """Bot 4 lee AMBOS archivos comerciales y reporta total_cg_count: 12."""
    reviewer = HonestyReviewer(sample_v4_audit_dir)
    mock_ext = MockPromiseExtractor([])
    report = reviewer.review(extractor=mock_ext)

    assert report["commercial_gates_read"]["canonical_file"] == "commercial_gates_report.json"
    assert report["commercial_gates_read"]["diagnostic_file"] is not None
    assert report["commercial_gates_read"]["total_cg_count"] == 12
    assert "CG-WHATSAPP-LEAD" in report["commercial_gates_read"]["warnings_found"]


def test_cg_whatsapp_lead_detected(sample_v4_audit_dir):
    """CG-WHATSAPP-LEAD en diagnóstico → finding CG_WARNING_UNDISCLOSED."""
    reviewer = HonestyReviewer(sample_v4_audit_dir)
    mock_ext = MockPromiseExtractor([])
    report = reviewer.review(extractor=mock_ext)

    cg_warnings = [
        f for f in report["findings"]
        if f.get("type") == FINDING_CG_WARNING_UNDISCLOSED
    ]
    assert len(cg_warnings) > 0
    whatsapp_findings = [
        f for f in cg_warnings
        if f.get("cg_reference") == "CG-WHATSAPP-LEAD"
    ]
    assert len(whatsapp_findings) > 0


def test_over_presentation_detected(sample_v4_audit_dir, mock_extractor):
    """Mock extrae 'cifras verificadas' con tier B → OVER_PRESENTATION."""
    reviewer = HonestyReviewer(sample_v4_audit_dir)
    report = reviewer.review(extractor=mock_extractor)

    over_presentations = [
        f for f in report["findings"]
        if f.get("type") == FINDING_OVER_PRESENTATION
    ]
    assert len(over_presentations) > 0
    assert over_presentations[0]["evidence_tier_declared"] == "B"
    assert "verificación" in over_presentations[0]["description"].lower() or \
           "evidence_tier=b" in over_presentations[0]["description"].lower()


def test_missing_scenario_detected(tmp_path):
    """Fixture con solo escenario optimista → MISSING_SCENARIO."""
    v4_audit = tmp_path / "v4_audit"
    v4_audit.mkdir()

    financial_scenarios = {
        "scenarios": {
            "optimistic": 1264435.2,
        },
        "breakdown": {"evidence_tier": "B"},
    }
    (v4_audit / "financial_scenarios_20260904.json").write_text(
        json.dumps(financial_scenarios, indent=2), encoding="utf-8"
    )
    (v4_audit / "commercial_gates_report.json").write_text(
        json.dumps({"results": []}, indent=2), encoding="utf-8"
    )
    (v4_audit / "02_PROPUESTA_COMERCIAL_20260904.md").write_text("# Propuesta", encoding="utf-8")

    reviewer = HonestyReviewer(v4_audit)
    mock_ext = MockPromiseExtractor([])
    report = reviewer.review(extractor=mock_ext)

    missing = [
        f for f in report["findings"]
        if f.get("type") == FINDING_MISSING_SCENARIO
    ]
    assert len(missing) == 2
    missing_descriptions = [f["description"].lower() for f in missing]
    assert any("conservador" in d for d in missing_descriptions)
    assert any("realista" in d for d in missing_descriptions)


def test_tier_mismatch_detected(tmp_path):
    """Claim con tier declarado ≠ tier real → TIER_MISMATCH."""
    v4_audit = tmp_path / "v4_audit"
    v4_audit.mkdir()

    financial_scenarios = {
        "scenarios": {
            "conservative": 100,
            "realistic": 200,
            "optimistic": 300,
        },
        "breakdown": {"evidence_tier": "B"},
    }
    (v4_audit / "financial_scenarios_20260904.json").write_text(
        json.dumps(financial_scenarios, indent=2), encoding="utf-8"
    )
    (v4_audit / "commercial_gates_report.json").write_text(
        json.dumps({"results": []}, indent=2), encoding="utf-8"
    )
    (v4_audit / "02_PROPUESTA_COMERCIAL_20260904.md").write_text("# Propuesta", encoding="utf-8")

    promises = [
        VerbalPromise(
            text="datos con tier A de evidencia",
            service_hint="general",
            location="Intro",
            confidence=0.9,
        ),
    ]
    mock_ext = MockPromiseExtractor(promises)

    reviewer = HonestyReviewer(v4_audit)
    report = reviewer.review(extractor=mock_ext)

    mismatches = [
        f for f in report["findings"]
        if f.get("type") == FINDING_TIER_MISMATCH
    ]
    assert len(mismatches) > 0
    assert mismatches[0]["evidence_tier_declared"] == "B"
    assert "tier a" in mismatches[0]["claim_text"].lower()


def test_serialization_to_disk(sample_v4_audit_dir, mock_extractor):
    """JSON escrito y re-leído (R2.4)."""
    reviewer = HonestyReviewer(sample_v4_audit_dir)
    output_path = reviewer.write_report(extractor=mock_extractor)

    assert output_path.exists()
    with open(output_path, "r", encoding="utf-8") as f:
        loaded = json.load(f)

    assert loaded["reviewer"] == "honesty_reviewer"
    assert loaded["clause"] == "P6.5"
    assert "findings" in loaded
    assert "commercial_gates_read" in loaded
    assert "summary" in loaded


def test_mock_extractor_no_real_llm(sample_v4_audit_dir, mock_extractor):
    """Tests no llaman LLM real (siempre mock)."""
    reviewer = HonestyReviewer(sample_v4_audit_dir)
    report = reviewer.review(extractor=mock_extractor)

    assert report["reviewer"] == "honesty_reviewer"
    assert isinstance(report["findings"], list)
    assert isinstance(mock_extractor.promises, list)
