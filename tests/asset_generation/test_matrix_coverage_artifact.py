"""FASE-HOTFIX-PRE-RELEASE / H3 (AC6, S-V3): `coverage_ratio` debe ser legible
en `proposal_asset_matrix.json`.

AC6 exige dos cosas: disolver el `is_coherent=false` estructural (cerrado y
medido) **y** que el ratio deje de ser algebraico. FASE-VERIFY certifico ⚠️
porque la clave ni siquiera existia en el artefacto: el unico ratio visible
vivia en `gate_report.details.alignment`.

Estos tests escriben con el escritor de produccion (`AssetAlignmentMatrix.save`
→ `to_dict` + `json.dump`) sobre insumos reales de la unica corrida del plan, y
leen **el JSON que quedo en disco** (L-V1 / L-F3).
"""

import json
from pathlib import Path

from modules.asset_generation.proposal_asset_alignment import (
    AssetAlignmentMatrix,
    ProposalAssetMatrixEntry,
)
from modules.asset_generation.site_presence_adapter import normalize_site_presence
from modules.quality_gates.alignment_result import AlignmentResult

AUDIT_DIR = Path("evidence/FASE-I/corrida/hotelsalentoreal/v4_audit")
MATRIX_ARTIFACT = AUDIT_DIR / "proposal_asset_matrix.json"
SNAPSHOT_ARTIFACT = AUDIT_DIR / "site_presence_snapshot.json"
GATE_REPORT_ARTIFACT = AUDIT_DIR / "gate_report_20260904_120413.json"


def _real_presence():
    """Snapshot de la corrida real, pasado por el normalizador canonico (L-F1)."""
    raw = json.loads(SNAPSHOT_ARTIFACT.read_text(encoding="utf-8"))
    return normalize_site_presence(raw["snapshot"])


def _real_entries():
    """Las 4 entradas que la corrida real prometio, reconstruidas del artefacto."""
    data = json.loads(MATRIX_ARTIFACT.read_text(encoding="utf-8"))
    return [
        ProposalAssetMatrixEntry(
            service_name=e["service_name"],
            pain_ids=e["pain_ids"],
            asset_type=e["asset_type"],
            asset_path=e.get("asset_path"),
            confidence=e["confidence"],
            status=e["status"],
        )
        for e in data["entries"]
    ]


def _save_and_read(tmp_path: Path, matrix: AssetAlignmentMatrix) -> dict:
    path = tmp_path / "proposal_asset_matrix.json"
    matrix.save(path)
    return json.loads(path.read_text(encoding="utf-8"))


class TestMatrizPublicaCoverageEnDisco:
    def test_ratio_legible_en_el_artifact(self, tmp_path):
        matrix = AssetAlignmentMatrix(
            entries=_real_entries(), site_presence_report=_real_presence()
        )
        d = _save_and_read(tmp_path, matrix)
        assert "coverage_ratio" in d
        assert d["coverage_ratio"] == 1.0
        # El denominador viaja con el numerador: sin el, un 1.0 no se puede leer.
        assert d["alignment"]["actionable_total"] == 4
        assert d["summary"]["actionable_total"] == 4

    def test_el_ratio_de_la_matriz_es_el_del_gate(self, tmp_path):
        """Un solo oraculo, dos artefactos: si divergen, el defecto A4 volvio."""
        matrix = AssetAlignmentMatrix(
            entries=_real_entries(), site_presence_report=_real_presence()
        )
        d = _save_and_read(tmp_path, matrix)
        gate = json.loads(GATE_REPORT_ARTIFACT.read_text(encoding="utf-8"))
        alignment = next(
            g["details"]["alignment"]
            for g in gate["gate_results"]
            if g["gate_name"] == "proposal_asset_alignment"
        )
        assert d["coverage_ratio"] == alignment["coverage_ratio"]
        assert d["alignment"] == alignment

    def test_matriz_de_test_sin_snapshot_sigue_publicando(self, tmp_path):
        """`to_dict()` no puede reventar cuando no hay presence (ruta de tests)."""
        d = _save_and_read(tmp_path, AssetAlignmentMatrix(entries=_real_entries()))
        assert d["coverage_ratio"] == AlignmentResult.from_asset_alignment_matrix(
            AssetAlignmentMatrix(entries=_real_entries())
        ).coverage_ratio


class TestMatrizCoverageDiscrimina:
    """El AC6 no se cierra con un 1.0: hay que probar que el numero **se mueve**.

    El caso negativo ya esta candado en `test_brecha_sin_asset_generado_es_deuda_visible`;
    aqui se candado que ese numero **llegue al artefacto**, que era el hueco.
    """

    def test_asset_faltante_baja_el_ratio_en_el_json(self, tmp_path):
        entries = _real_entries()
        sin_asset = [
            ProposalAssetMatrixEntry(
                service_name=e.service_name,
                pain_ids=list(e.pain_ids),
                asset_type=e.asset_type,
                asset_path=None,
                confidence=0.0,
                status="MISSING_ASSET",
            )
            if e.status == "LINKED" else e
            for e in entries
        ]
        matrix = AssetAlignmentMatrix(
            entries=sin_asset, site_presence_report=_real_presence()
        )
        d = _save_and_read(tmp_path, matrix)
        # 3 presentes en produccion / 4 accionables, y el llms_txt NO existe en
        # el snapshot de la corrida (status not_exists) -> no se auto-cubre.
        assert d["coverage_ratio"] == 0.75
        assert d["alignment"]["actionable_total"] == 4
        assert d["alignment"]["unresolved"] == 1
        assert d["delivery_ready"] is False

    def test_nada_comprometido_no_es_lo_mismo_que_no_evaluado(self, tmp_path):
        """vacio != ausente: denominador 0 se lee como denominador 0."""
        d = _save_and_read(tmp_path, AssetAlignmentMatrix(entries=[]))
        assert d["coverage_ratio"] == 1.0
        assert d["alignment"]["actionable_total"] == 0
        assert d["summary"]["promised"] == 0
        # ...y el artefacto sigue afirmando que si se evaluo (no esta mudo):
        assert d["not_promised"] == []
        assert d["unknown_services"] == []

    def test_nuevo_campo_no_rompe_lectores_legacy(self, tmp_path):
        """Las 7 claves medidas por VERIFY en el artefacto pre-2.1 siguen alli."""
        matrix = AssetAlignmentMatrix(
            entries=_real_entries(), site_presence_report=_real_presence()
        )
        d = _save_and_read(tmp_path, matrix)
        claves_pre_hotfix = {
            "alignment_status_version", "delivery_ready", "entries", "not_promised",
            "proposal_asset_matrix_version", "summary", "unknown_services",
        }
        assert claves_pre_hotfix <= set(d)
