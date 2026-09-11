"""Contrato de *ubicación* de la propuesta comercial en el paquete tribunal.

La lección de la auditoría de FASE-T4-B (§6.1) es que el fixture de la fase replicó el
contenido de los artefactos reales pero puso la propuesta dentro de `v4_audit_dir`, que
es justo donde el pipeline NO la escribe: la escribe en `v4_complete/`, dos niveles
arriba de `<hotel>/v4_audit/`. Estos fixtures reproducen la estructura real sin
depender del baseline en disco.
"""

import json
from pathlib import Path

import pytest

from modules.quality_gates.tribunal.alignment_reviewer import AlignmentReviewer
from modules.quality_gates.tribunal.artifact_paths import resolve_latest
from modules.quality_gates.tribunal.honesty_reviewer import HonestyReviewer
from modules.quality_gates.tribunal.llm_extractor import MockPromiseExtractor


PROPOSAL = """# Propuesta Comercial

## Contacto
WhatsApp: 316 6296142
"""


def build_real_like_layout(root: Path, proposal_at_v4_complete: bool = True) -> Path:
    """Reproduce v4_complete/{02_PROPUESTA…, deliveries/, <hotel>/v4_audit/}."""
    v4_complete = root / "v4_complete"
    v4_audit = v4_complete / "hotelsalentoreal" / "v4_audit"
    v4_audit.mkdir(parents=True)
    (v4_complete / "deliveries" / "hotelsalentoreal_20260831").mkdir(parents=True)

    target = v4_complete if proposal_at_v4_complete else v4_audit
    (target / "02_PROPUESTA_COMERCIAL_20260831_122803.md").write_text(PROPOSAL, encoding="utf-8")

    (v4_audit / "commercial_gates_report.json").write_text(
        json.dumps({"results": []}), encoding="utf-8"
    )
    (v4_audit / "proposal_asset_matrix.json").write_text(
        json.dumps({"entries": []}), encoding="utf-8"
    )
    (v4_audit / "financial_scenarios_20260831_122757.json").write_text(
        json.dumps({
            "scenarios": {"conservative": 1, "realistic": 2, "optimistic": 3},
            "breakdown": {"evidence_tier": "B"},
        }),
        encoding="utf-8",
    )
    return v4_audit


def test_honesty_reviewer_encuentra_propuesta_en_v4_complete(tmp_path):
    """D1 en estructura real: sin el ascendente el revisor declaraba falta espuria."""
    v4_audit = build_real_like_layout(tmp_path)
    reviewer = HonestyReviewer(v4_audit)

    assert reviewer._load_proposal() is not None
    report = reviewer.review(extractor=MockPromiseExtractor([]))
    types = {f["type"] for f in report["findings"]}
    assert "MISSING_ARTIFACT" not in types
    assert report["verdict_recommendation"] == "APROBADO"


def test_alignment_reviewer_encuentra_propuesta_en_v4_complete(tmp_path):
    """T4-A arrastraba el mismo defecto de resolución (verificado en la auditoría)."""
    v4_audit = build_real_like_layout(tmp_path)
    reviewer = AlignmentReviewer(v4_audit)

    assert reviewer._load_proposal() is not None
    report = reviewer.review(extractor=MockPromiseExtractor([]))
    assert "No se encontró 02_PROPUESTA_COMERCIAL" not in json.dumps(report, ensure_ascii=False)


def test_resolver_toma_el_mas_reciente_por_mtime_aun_de_otro_nivel(tmp_path):
    """Con dos propuestas en niveles distintos gana la más reciente, no la más cercana."""
    v4_audit = build_real_like_layout(tmp_path)
    older = v4_audit.parent.parent / "02_PROPUESTA_COMERCIAL_20260101_000000.md"
    older.write_text("# vieja", encoding="utf-8")
    older.touch()
    newer = v4_audit / "02_PROPUESTA_COMERCIAL_20260901_000000.md"
    newer.write_text("# nueva", encoding="utf-8")
    newer.touch()

    resolved = resolve_latest("02_PROPUESTA_COMERCIAL*.md", v4_audit)
    assert resolved == newer


def test_resolutor_devuelve_none_cuando_realmente_no_existe(tmp_path):
    """MISSING_ARTIFACT sigue siendo válido cuando el artefacto falta de verdad."""
    v4_audit = build_real_like_layout(tmp_path)
    for path in (tmp_path / "v4_complete").rglob("02_PROPUESTA_COMERCIAL*.md"):
        path.unlink()

    assert resolve_latest("02_PROPUESTA_COMERCIAL*.md", v4_audit) is None
    reviewer = HonestyReviewer(v4_audit)
    report = reviewer.review(extractor=MockPromiseExtractor([]))
    assert [f["type"] for f in report["findings"]] == ["MISSING_ARTIFACT"]
    assert report["verdict_recommendation"] == "BLOQUEAR"
