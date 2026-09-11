"""Tests de serialización del acta — JSON + MD writers."""

import json
import shutil
from pathlib import Path

import pytest

from modules.quality_gates.tribunal.judge import TribunalJudge
from modules.quality_gates.tribunal.acta_writer import ActaWriter

PROJECT_ROOT = Path(__file__).resolve().parents[3]
FASE_I_AUDIT_DIR = (
    PROJECT_ROOT / "evidence" / "FASE-I" / "corrida" / "hotelsalentoreal" / "v4_audit"
)


@pytest.fixture
def acta_output(tmp_path):
    """Genera un acta real con writer y retorna las rutas."""
    if not FASE_I_AUDIT_DIR.exists():
        pytest.skip("FASE-I artifacts not available")

    audit_dir = tmp_path / "v4_audit"
    shutil.copytree(FASE_I_AUDIT_DIR, audit_dir)

    deliveries = tmp_path / "deliveries"
    hotel_dir = deliveries / "hotelsalentoreal_20260904"
    hotel_dir.mkdir(parents=True)
    manifest = {
        "hotel_id": "hotelsalentoreal",
        "quality_metadata": {"evidence_tier": "B"},
    }
    (hotel_dir / "MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")

    judge = TribunalJudge(
        v4_audit_dir=audit_dir,
        deliveries_dir=deliveries,
        hotel_id="hotelsalentoreal",
    )
    acta = judge.evaluate()

    output_dir = tmp_path / "output"
    writer = ActaWriter(output_dir)
    json_path, md_path = writer.write(acta)

    return {
        "acta": acta,
        "json_path": json_path,
        "md_path": md_path,
        "output_dir": output_dir,
    }


def test_acta_json_serialization(acta_output):
    """Lee el JSON del writer real (no objeto en memoria), verifica claves."""
    json_path = acta_output["json_path"]
    assert json_path.exists()

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    required_keys = [
        "verdict",
        "evidence_tier",
        "clauses_evaluated",
        "clauses",
        "reviewer_reports",
        "first_floor_rule",
        "timestamp",
        "hotel_id",
    ]
    for key in required_keys:
        assert key in data, f"Missing key: {key}"

    assert data["verdict"] in (
        "APROBADO-PARA-ENTREGA",
        "APROBADO-CONDICIONAL-PENDING-ONBOARDING",
        "DEVOLVER-CORRECCIONES",
        "BLOQUEADO",
    )
    assert data["evidence_tier"] in ("A", "B", "C")
    assert data["clauses_evaluated"] == 6

    for clause_id in ["P6.1", "P6.2", "P6.3", "P6.4", "P6.5", "P6.6"]:
        assert clause_id in data["clauses"]
        clause = data["clauses"][clause_id]
        assert "status" in clause
        assert "source_artifact" in clause
        assert "finding" in clause
        assert clause["status"] in ("PASS", "FAIL", "ADVISORY", "NOT_EVALUABLE")


def test_acta_md_has_six_clauses(acta_output):
    """El MD contiene secciones P6.1-P6.6."""
    md_path = acta_output["md_path"]
    assert md_path.exists()

    content = md_path.read_text(encoding="utf-8")

    for clause_id in ["P6.1", "P6.2", "P6.3", "P6.4", "P6.5", "P6.6"]:
        assert clause_id in content, f"Missing clause section: {clause_id}"

    assert "Acta de Revisión" in content
    assert "Veredicto" in content
    assert "Evidence Tier" in content


def test_acta_md_references_source_artifacts(acta_output):
    """El MD referencia los artefactos fuente de cada cláusula."""
    md_path = acta_output["md_path"]
    content = md_path.read_text(encoding="utf-8")

    assert "gate_report" in content
    assert "MANIFEST.json" in content


def test_acta_json_roundtrip(acta_output):
    """El JSON del acta es serializable y deserializable sin pérdida."""
    json_path = acta_output["json_path"]
    original = acta_output["acta"]

    with open(json_path, "r", encoding="utf-8") as f:
        loaded = json.load(f)

    assert loaded["verdict"] == original["verdict"]
    assert loaded["evidence_tier"] == original["evidence_tier"]
    assert loaded["clauses_evaluated"] == original["clauses_evaluated"]
    assert loaded["hotel_id"] == original["hotel_id"]
    assert len(loaded["clauses"]) == len(original["clauses"])
