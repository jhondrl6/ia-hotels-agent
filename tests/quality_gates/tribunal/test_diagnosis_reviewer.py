"""Tests del DiagnosisReviewer — Bot 1 del tribunal de certificación.

Tests deterministas sobre fixtures y artefactos reales.
Verifica trazabilidad pain_id, fuente declarada, recall vacuo S-I1.
"""

import json
import shutil
from pathlib import Path

import pytest

from modules.quality_gates.tribunal.diagnosis_reviewer import (
    DiagnosisReviewer,
    FINDING_VACUOUS_RECALL,
    FINDING_UNTRACEABLE_PAIN,
    SEVERITY_CRITICAL,
    VERDICT_APROBADO,
    VERDICT_BLOQUEAR,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
FASE_I_AUDIT_DIR = (
    PROJECT_ROOT / "evidence" / "FASE-I" / "corrida" / "hotelsalentoreal" / "v4_audit"
)


@pytest.fixture
def tmp_audit_dir(tmp_path):
    """Copia artefactos de FASE-I a un directorio temporal."""
    if not FASE_I_AUDIT_DIR.exists():
        pytest.skip("FASE-I artifacts not available")
    dest = tmp_path / "v4_audit"
    shutil.copytree(FASE_I_AUDIT_DIR, dest)
    return dest


@pytest.fixture
def empty_audit_dir(tmp_path):
    """Directorio de auditoría vacío."""
    audit = tmp_path / "v4_audit_empty"
    audit.mkdir()
    return audit


@pytest.fixture
def audit_with_vacuous_recall(tmp_path):
    """Fixture con critical_recall=1.0 y details:{} (recall vacuo S-I1)."""
    audit = tmp_path / "v4_audit_vacuous"
    audit.mkdir()

    gate_report = {
        "ready": True,
        "status": "READY_FOR_PUBLICATION",
        "gate_results": [
            {
                "gate_name": "critical_recall",
                "passed": True,
                "status": "PASS",
                "value": 1.0,
                "message": "critical_recall OK",
                "details": {},
            }
        ],
        "blocking_issues": [],
        "summary": {
            "total_gates": 1,
            "passed": 1,
            "failed": 0,
            "not_evaluated": [],
            "blocked": False,
        },
    }
    (audit / "gate_report_20260910.json").write_text(
        json.dumps(gate_report), encoding="utf-8"
    )

    pain_ledger = {
        "pain_ledger_version": "1.0",
        "entries": [
            {
                "pain_id": "no_whatsapp_visible",
                "source_module": "data_validation",
                "source_file": "cross_validator.py",
                "severity": "HIGH",
                "confidence": 0.9,
                "status": "DETECTED",
                "human_label": "Sin WhatsApp visible",
                "evidence_refs": [],
            }
        ],
    }
    (audit / "pain_ledger.json").write_text(
        json.dumps(pain_ledger), encoding="utf-8"
    )

    coherence_validation = {
        "is_coherent": True,
        "overall_score": 0.85,
        "checks": [],
        "errors": [],
        "warnings": [],
        "timestamp": "2026-09-10T00:00:00",
        "version": "4.2.0",
    }
    (audit / "coherence_validation.json").write_text(
        json.dumps(coherence_validation), encoding="utf-8"
    )

    return audit


@pytest.fixture
def audit_with_founded_recall(tmp_path):
    """Fixture con critical_recall=1.0 y details.critical_issues_count=3 (recall fundado)."""
    audit = tmp_path / "v4_audit_founded"
    audit.mkdir()

    gate_report = {
        "ready": True,
        "status": "READY_FOR_PUBLICATION",
        "gate_results": [
            {
                "gate_name": "critical_recall",
                "passed": True,
                "status": "PASS",
                "value": 1.0,
                "message": "critical_recall OK",
                "details": {
                    "critical_issues_count": 3,
                    "recall_basis": "audit_present_no_critical_issues",
                },
            }
        ],
        "blocking_issues": [],
        "summary": {
            "total_gates": 1,
            "passed": 1,
            "failed": 0,
            "not_evaluated": [],
            "blocked": False,
        },
    }
    (audit / "gate_report_20260910.json").write_text(
        json.dumps(gate_report), encoding="utf-8"
    )

    pain_ledger = {
        "pain_ledger_version": "1.0",
        "entries": [
            {
                "pain_id": "no_whatsapp_visible",
                "source_module": "data_validation",
                "source_file": "cross_validator.py",
                "severity": "HIGH",
                "confidence": 0.9,
                "status": "DETECTED",
                "human_label": "Sin WhatsApp visible",
                "evidence_refs": [],
            }
        ],
    }
    (audit / "pain_ledger.json").write_text(
        json.dumps(pain_ledger), encoding="utf-8"
    )

    coherence_validation = {
        "is_coherent": True,
        "overall_score": 0.85,
        "checks": [],
        "errors": [],
        "warnings": [],
        "timestamp": "2026-09-10T00:00:00",
        "version": "4.2.0",
    }
    (audit / "coherence_validation.json").write_text(
        json.dumps(coherence_validation), encoding="utf-8"
    )

    return audit


@pytest.fixture
def audit_with_untraceable_pain(tmp_path):
    """Fixture con brecha en diagnóstico sin pain_id en ledger."""
    audit = tmp_path / "v4_audit_untraceable"
    audit.mkdir()

    pain_ledger = {
        "pain_ledger_version": "1.0",
        "entries": [
            {
                "pain_id": "no_whatsapp_visible",
                "source_module": "data_validation",
                "source_file": "cross_validator.py",
                "severity": "HIGH",
                "confidence": 0.9,
                "status": "DETECTED",
                "human_label": "Sin WhatsApp visible",
                "evidence_refs": [],
            }
        ],
    }
    (audit / "pain_ledger.json").write_text(
        json.dumps(pain_ledger), encoding="utf-8"
    )

    diagnostic_md = """# Diagnóstico y Oportunidad

## Trazabilidad: Brechas Identificadas

### Brecha 1: Sin WhatsApp visible
- **pain_id:** no_whatsapp_visible
- **Detalle:** No se encuentra botón de WhatsApp
- **Por que importa:** 0.8

### Brecha 2: Missing llms.txt
- **pain_id:** missing_llmstxt
- **Detalle:** Archivo llms.txt ausente
- **Por que importa:** 0.6
"""
    (audit / "01_DIAGNOSTICO_Y_OPORTUNIDAD_20260910.md").write_text(
        diagnostic_md, encoding="utf-8"
    )

    coherence_validation = {
        "is_coherent": True,
        "overall_score": 0.85,
        "checks": [],
        "errors": [],
        "warnings": [],
        "timestamp": "2026-09-10T00:00:00",
        "version": "4.2.0",
    }
    (audit / "coherence_validation.json").write_text(
        json.dumps(coherence_validation), encoding="utf-8"
    )

    gate_report = {
        "ready": True,
        "status": "READY_FOR_PUBLICATION",
        "gate_results": [
            {
                "gate_name": "critical_recall",
                "passed": True,
                "status": "PASS",
                "value": 1.0,
                "message": "critical_recall OK",
                "details": {"critical_issues_count": 2, "recall_basis": "audit_present"},
            }
        ],
        "blocking_issues": [],
        "summary": {
            "total_gates": 1,
            "passed": 1,
            "failed": 0,
            "not_evaluated": [],
            "blocked": False,
        },
    }
    (audit / "gate_report_20260910.json").write_text(
        json.dumps(gate_report), encoding="utf-8"
    )

    return audit


def test_review_produces_findings_list(empty_audit_dir):
    """Salida tiene clave 'findings' como lista."""
    reviewer = DiagnosisReviewer(v4_audit_dir=empty_audit_dir)
    report = reviewer.review()

    assert "findings" in report
    assert isinstance(report["findings"], list)
    assert "summary" in report
    assert "verdict_recommendation" in report
    assert report["reviewer"] == "diagnosis_reviewer"
    assert report["clause"] == "P6.1"


def test_vacuous_recall_detected(audit_with_vacuous_recall):
    """Fixture con critical_recall=1.0, details:{} → finding VACUOUS_RECALL."""
    reviewer = DiagnosisReviewer(v4_audit_dir=audit_with_vacuous_recall)
    report = reviewer.review()

    vacuous_findings = [
        f for f in report["findings"]
        if f["finding_type"] == FINDING_VACUOUS_RECALL
    ]

    assert len(vacuous_findings) == 1
    finding = vacuous_findings[0]
    assert finding["severity"] == SEVERITY_CRITICAL
    assert finding["clause"] == "P6.1"
    assert finding["source_artifact"] == "gate_report_*.json"
    assert "vacuo" in finding["description"].lower() or "vacuous" in finding["description"].lower()


def test_founded_recall_not_flagged(audit_with_founded_recall):
    """Fixture con details.critical_issues_count=3 → sin finding de recall."""
    reviewer = DiagnosisReviewer(v4_audit_dir=audit_with_founded_recall)
    report = reviewer.review()

    vacuous_findings = [
        f for f in report["findings"]
        if f["finding_type"] == FINDING_VACUOUS_RECALL
    ]

    assert len(vacuous_findings) == 0


def test_untraceable_pain_detected(audit_with_untraceable_pain):
    """Brecha en diagnóstico sin pain_id en ledger → finding UNTRACEABLE_PAIN."""
    reviewer = DiagnosisReviewer(v4_audit_dir=audit_with_untraceable_pain)
    report = reviewer.review()

    untraceable_findings = [
        f for f in report["findings"]
        if f["finding_type"] == FINDING_UNTRACEABLE_PAIN
    ]

    assert len(untraceable_findings) >= 1
    missing_pain_ids = [f["pain_id"] for f in untraceable_findings]
    assert "missing_llmstxt" in missing_pain_ids


def test_serialization_to_disk(tmp_path, audit_with_vacuous_recall):
    """Escribe JSON real, lo re-lee, verifica claves (R2.4)."""
    reviewer = DiagnosisReviewer(v4_audit_dir=audit_with_vacuous_recall)
    output_path = tmp_path / "output" / "revision_diagnostico.json"

    written_path = reviewer.write_report(output_path=output_path)

    assert written_path.exists()
    assert written_path.suffix == ".json"

    with open(written_path, "r", encoding="utf-8") as f:
        loaded = json.load(f)

    required_keys = {"reviewer", "clause", "findings", "summary", "verdict_recommendation"}
    assert required_keys.issubset(loaded.keys())
    assert isinstance(loaded["findings"], list)
    assert isinstance(loaded["summary"], dict)
    assert "total_findings" in loaded["summary"]


def test_resolves_timestamped_gate_report(audit_with_vacuous_recall):
    """Glob resuelve gate_report_*.json."""
    reviewer = DiagnosisReviewer(v4_audit_dir=audit_with_vacuous_recall)

    gate_report_path = reviewer._resolve_artifact("gate_report_*.json")
    assert gate_report_path is not None
    assert gate_report_path.name.startswith("gate_report_")
    assert gate_report_path.name.endswith(".json")


def test_does_not_import_gate_internals():
    """Grep: diagnosis_reviewer.py no importa publication_gates internals."""
    reviewer_path = (
        PROJECT_ROOT / "modules" / "quality_gates" / "tribunal" / "diagnosis_reviewer.py"
    )
    content = reviewer_path.read_text(encoding="utf-8")

    forbidden_imports = [
        "from modules.quality_gates.publication_gates import",
        "from modules.quality_gates import publication_gates",
        "import publication_gates",
        "check_publication_readiness",
        "BLOCKING_GATE_NAMES",
    ]

    for forbidden in forbidden_imports:
        assert forbidden not in content, (
            f"diagnosis_reviewer.py contains forbidden import: {forbidden}"
        )


def test_never_block_on_missing_artifacts(empty_audit_dir):
    """El revisor NUNCA lanza excepción por artefacto ausente (never-block)."""
    reviewer = DiagnosisReviewer(v4_audit_dir=empty_audit_dir)
    report = reviewer.review()

    assert report["reviewer"] == "diagnosis_reviewer"
    assert isinstance(report["findings"], list)
    assert report["verdict_recommendation"] in (VERDICT_APROBADO, VERDICT_BLOQUEAR, "DEVOLVER-PRUEBAS")


def test_critical_priority_inflation_detected(tmp_path):
    """pain_id CRITICAL con confidence < 0.5 → finding de prioridad inflada."""
    audit = tmp_path / "v4_audit_inflated"
    audit.mkdir()

    pain_ledger = {
        "pain_ledger_version": "1.0",
        "entries": [
            {
                "pain_id": "inflated_critical",
                "source_module": "test",
                "source_file": "test.py",
                "severity": "CRITICAL",
                "confidence": 0.3,
                "status": "DETECTED",
                "human_label": "Critical inflado",
                "evidence_refs": [],
            }
        ],
    }
    (audit / "pain_ledger.json").write_text(
        json.dumps(pain_ledger), encoding="utf-8"
    )

    reviewer = DiagnosisReviewer(v4_audit_dir=audit)
    report = reviewer.review()

    priority_findings = [
        f for f in report["findings"]
        if "prioridad" in f["description"].lower() or "inflada" in f["description"].lower()
    ]
    assert len(priority_findings) >= 1


def test_verdict_blocks_on_critical_findings(audit_with_vacuous_recall):
    """Finding CRITICAL → veredicto BLOQUEAR."""
    reviewer = DiagnosisReviewer(v4_audit_dir=audit_with_vacuous_recall)
    report = reviewer.review()

    assert report["verdict_recommendation"] == VERDICT_BLOQUEAR
    assert report["summary"]["critical"] >= 1
