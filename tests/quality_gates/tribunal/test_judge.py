"""Tests del TribunalJudge — deterministas sobre artefactos reales + fixtures."""

import json
import shutil
import tempfile
from pathlib import Path

import pytest

from modules.quality_gates.tribunal.judge import (
    TribunalJudge,
    VERDICT_APPROVED,
    VERDICT_BLOCKED,
    VERDICT_CONDITIONAL,
    VERDICT_RETURN,
    blocks_delivery_zip,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
FASE_I_AUDIT_DIR = (
    PROJECT_ROOT / "evidence" / "FASE-I" / "corrida" / "hotelsalentoreal" / "v4_audit"
)
FASE_D_DELIVERIES_DIR = (
    PROJECT_ROOT
    / "output"
    / "FASE-D_salentoreal_post_guard"
    / "v4_complete"
    / "deliveries"
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
def tmp_deliveries_dir_b(tmp_path):
    """Crea deliveries_dir con MANIFEST.json Tier B."""
    deliveries = tmp_path / "deliveries"
    hotel_dir = deliveries / "hotelsalentoreal_20260904"
    hotel_dir.mkdir(parents=True)
    manifest = {
        "hotel_id": "hotelsalentoreal",
        "quality_metadata": {"evidence_tier": "B"},
    }
    (hotel_dir / "MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
    return deliveries


@pytest.fixture
def tmp_deliveries_dir_a(tmp_path):
    """Crea deliveries_dir con MANIFEST.json Tier A."""
    deliveries = tmp_path / "deliveries"
    hotel_dir = deliveries / "testhotel_20260904"
    hotel_dir.mkdir(parents=True)
    manifest = {
        "hotel_id": "testhotel",
        "quality_metadata": {"evidence_tier": "A"},
    }
    (hotel_dir / "MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
    return deliveries


@pytest.fixture
def tmp_deliveries_dir_c(tmp_path):
    """Crea deliveries_dir con MANIFEST.json Tier C."""
    deliveries = tmp_path / "deliveries"
    hotel_dir = deliveries / "testhotel_20260904"
    hotel_dir.mkdir(parents=True)
    manifest = {
        "hotel_id": "testhotel",
        "quality_metadata": {"evidence_tier": "C"},
    }
    (hotel_dir / "MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
    return deliveries


def test_verdict_tier_b_is_conditional(tmp_audit_dir, tmp_deliveries_dir_b):
    """Artefacto SalenteReal (Tier B) → APROBADO-CONDICIONAL-PENDING-ONBOARDING."""
    judge = TribunalJudge(
        v4_audit_dir=tmp_audit_dir,
        deliveries_dir=tmp_deliveries_dir_b,
        hotel_id="hotelsalentoreal",
    )
    acta = judge.evaluate()

    assert acta["verdict"] == VERDICT_CONDITIONAL
    assert acta["evidence_tier"] == "B"
    assert acta["first_floor_rule"]["applied"] is True


def test_verdict_tier_a_can_be_approved(tmp_audit_dir, tmp_deliveries_dir_a):
    """Fixture Tier A + coherence ≥ 0.8 + gates en verde → APROBADO-PARA-ENTREGA."""
    judge = TribunalJudge(
        v4_audit_dir=tmp_audit_dir,
        deliveries_dir=tmp_deliveries_dir_a,
        hotel_id="testhotel",
    )
    acta = judge.evaluate()

    assert acta["verdict"] == VERDICT_APPROVED
    assert acta["evidence_tier"] == "A"
    assert acta["first_floor_rule"]["applied"] is False


def test_first_floor_rule_blocks_delivery(tmp_audit_dir, tmp_deliveries_dir_c):
    """Tier C → nunca APROBADO-PARA-ENTREGA."""
    judge = TribunalJudge(
        v4_audit_dir=tmp_audit_dir,
        deliveries_dir=tmp_deliveries_dir_c,
        hotel_id="testhotel",
    )
    acta = judge.evaluate()

    assert acta["verdict"] != VERDICT_APPROVED
    assert acta["verdict"] == VERDICT_CONDITIONAL
    assert acta["evidence_tier"] == "C"
    assert acta["first_floor_rule"]["applied"] is True


def test_resolves_timestamped_artifacts(tmp_audit_dir, tmp_deliveries_dir_b):
    """Glob resuelve gate_report_*.json sin hardcodear timestamp."""
    judge = TribunalJudge(
        v4_audit_dir=tmp_audit_dir,
        deliveries_dir=tmp_deliveries_dir_b,
        hotel_id="hotelsalentoreal",
    )

    gate_report_path = judge._resolve_artifact("gate_report_*.json")
    assert gate_report_path is not None
    assert gate_report_path.name.startswith("gate_report_")
    assert gate_report_path.name.endswith(".json")

    acta = judge.evaluate()
    p6_6 = acta["clauses"]["P6.6"]
    assert p6_6["status"] != "NOT_EVALUABLE"
    assert p6_6["source_artifact"] == "gate_report_*.json"


def test_does_not_reimplement_gates():
    """Grep: judge.py no importa publication_gates internals."""
    judge_path = (
        PROJECT_ROOT / "modules" / "quality_gates" / "tribunal" / "judge.py"
    )
    content = judge_path.read_text(encoding="utf-8")

    forbidden_imports = [
        "from modules.quality_gates.publication_gates import",
        "from modules.quality_gates import publication_gates",
        "import publication_gates",
        "check_publication_readiness",
        "BLOCKING_GATE_NAMES",
    ]

    for forbidden in forbidden_imports:
        assert forbidden not in content, (
            f"judge.py contains forbidden import: {forbidden}"
        )


def test_never_block_on_missing_artifacts(tmp_path):
    """El Juez NUNCA lanza excepción por artefacto ausente (never-block)."""
    empty_audit = tmp_path / "v4_audit"
    empty_audit.mkdir()
    empty_deliveries = tmp_path / "deliveries"
    empty_deliveries.mkdir()

    judge = TribunalJudge(
        v4_audit_dir=empty_audit,
        deliveries_dir=empty_deliveries,
        hotel_id="nonexistent",
    )

    acta = judge.evaluate()
    assert acta["verdict"] in (VERDICT_CONDITIONAL, VERDICT_BLOCKED)
    assert acta["evidence_tier"] == "C"
    assert acta["clauses_evaluated"] == 6

    for clause_id, clause in acta["clauses"].items():
        assert clause["status"] in ("PASS", "FAIL", "ADVISORY", "NOT_EVALUABLE")


def test_p6_1_reads_critical_recall_gate(tmp_audit_dir, tmp_deliveries_dir_b):
    """P6.1 lee gate critical_recall del gate_report."""
    judge = TribunalJudge(
        v4_audit_dir=tmp_audit_dir,
        deliveries_dir=tmp_deliveries_dir_b,
        hotel_id="hotelsalentoreal",
    )
    acta = judge.evaluate()

    p6_1 = acta["clauses"]["P6.1"]
    assert p6_1["status"] == "PASS"
    assert "gate_report" in p6_1["source_artifact"]


def test_p6_3_reads_asset_generation_report(tmp_audit_dir, tmp_deliveries_dir_b):
    """P6.3 lee asset_generation_report.json."""
    judge = TribunalJudge(
        v4_audit_dir=tmp_audit_dir,
        deliveries_dir=tmp_deliveries_dir_b,
        hotel_id="hotelsalentoreal",
    )
    acta = judge.evaluate()

    p6_3 = acta["clauses"]["P6.3"]
    assert p6_3["status"] == "PASS"
    assert "asset_generation_report" in p6_3["source_artifact"]


def test_p6_4_reads_proposal_asset_matrix(tmp_audit_dir, tmp_deliveries_dir_b):
    """P6.4 lee proposal_asset_matrix.json."""
    judge = TribunalJudge(
        v4_audit_dir=tmp_audit_dir,
        deliveries_dir=tmp_deliveries_dir_b,
        hotel_id="hotelsalentoreal",
    )
    acta = judge.evaluate()

    p6_4 = acta["clauses"]["P6.4"]
    assert p6_4["status"] == "PASS"
    assert "proposal_asset_matrix" in p6_4["source_artifact"]


def test_zero_evidence_tier_a_is_not_approved(tmp_deliveries_dir_a, tmp_path):
    """Tier A sin ningún artefacto de evidencia NUNCA certifica APROBADO-PARA-ENTREGA."""
    empty_audit = tmp_path / "v4_audit"
    empty_audit.mkdir()

    judge = TribunalJudge(
        v4_audit_dir=empty_audit,
        deliveries_dir=tmp_deliveries_dir_a,
        hotel_id="testhotel",
    )
    acta = judge.evaluate()

    assert acta["verdict"] == VERDICT_CONDITIONAL
    assert acta["evidence_tier"] == "A"
    unevaluable = [
        key for key, clause in acta["clauses"].items() if clause["status"] == "NOT_EVALUABLE"
    ]
    assert set(unevaluable) >= {"P6.1", "P6.3", "P6.4", "P6.6"}


def test_p6_2_deferred_does_not_block_approval(tmp_audit_dir, tmp_deliveries_dir_a):
    """P6.2 difiere a T4-A: su NOT_EVALUABLE no impide el veredicto máximo en T1."""
    judge = TribunalJudge(
        v4_audit_dir=tmp_audit_dir,
        deliveries_dir=tmp_deliveries_dir_a,
        hotel_id="testhotel",
    )
    acta = judge.evaluate()

    assert acta["clauses"]["P6.2"]["status"] == "NOT_EVALUABLE"
    assert acta["verdict"] == VERDICT_APPROVED


def test_zip_blocking_policy_covers_both_negative_verdicts():
    """Bloquean el ZIP BLOQUEADO y DEVOLVER-CORRECCIONES; la ausencia de acta no."""
    assert blocks_delivery_zip({"verdict": VERDICT_BLOCKED}) is True
    assert blocks_delivery_zip({"verdict": VERDICT_RETURN}) is True
    assert blocks_delivery_zip({"verdict": VERDICT_APPROVED}) is False
    assert blocks_delivery_zip({"verdict": VERDICT_CONDITIONAL}) is False
    assert blocks_delivery_zip(None) is False


def test_devolver_correcciones_blocks_zip(tmp_deliveries_dir_a, tmp_path):
    """Assets fallidos → DEVOLVER-CORRECCIONES → el ZIP queda bloqueado."""
    audit = tmp_path / "v4_audit_failed"
    audit.mkdir()
    (audit / "asset_generation_report.json").write_text(
        json.dumps({"summary": {"total_assets": 5, "generated": 3, "failed": 2}}),
        encoding="utf-8",
    )

    judge = TribunalJudge(
        v4_audit_dir=audit,
        deliveries_dir=tmp_deliveries_dir_a,
        hotel_id="testhotel",
    )
    acta = judge.evaluate()

    assert acta["clauses"]["P6.3"]["status"] == "FAIL"
    assert acta["verdict"] == VERDICT_RETURN
    assert blocks_delivery_zip(acta) is True
