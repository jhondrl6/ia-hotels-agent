"""FASE-P6-R (R1): matriz AC-G4/AC-G5 contra el FLUJO REAL, offline.

Diferencia con `test_ac_g4_g5_multi_hotel_matrix.py` (que queda como unitario del
Juez): aquí cada perfil corre el cableado completo de `main.py` FASE-T1 →
`packager.write()` (ZIP real `.zip.tmp`) → los 4 Bots leyendo artefactos y ZIP
reales → `collect_reviewer_reports` → `enrich` → `blocks_delivery_zip` →
`finalize` → `publish()`/`suppress()` con `package_evidence` (AC-G3).

Ningún acta se escribe a mano: el acta la produce el Juez y la modifican solo los
pasos reales del flujo (prohibición del plan: "no escribir un acta a mano como
sustituto del flujo").

Perfiles (sin datos sensibles):
  1. Tier A, gates OK, revisores OK            → APROBADO-PARA-ENTREGA → publish
  2. Tier B+ (caso Don Alfonso anonimizado), gates OK, honesty objeta con
     CRITICAL                                  → BLOQUEADO → suppress + evidencia
  3. Gates ya bloquean (P6.6 FAIL) con los 4 revisores limpios → BLOQUEADO por
     regla 1 (causalidad separada del caso 2)
  4. Tier B+ primer piso, todo limpio          → CONDITIONAL, el caller no bloquea
     → publish (L-P6.2: decisión partida Juez/caller)
  5. Como el 2 pero kill switch apagado        → ZIP publicado +
     `suppressed_by_operator` declarado (L-P6.1: las dos llaves separadas)
"""
import json
from datetime import datetime
from pathlib import Path

import pytest

from modules.delivery.delivery_packager import DeliveryPackager
from modules.quality_gates.tribunal import (
    AlignmentReviewer,
    AssetReviewer,
    DiagnosisReviewer,
    HonestyReviewer,
    TribunalJudge,
    blocks_delivery_zip,
)
from modules.quality_gates.tribunal.acta_writer import ActaWriter
from modules.quality_gates.tribunal.judge import (
    VERDICT_APPROVED,
    VERDICT_BLOCKED,
    VERDICT_CONDITIONAL,
)
from modules.quality_gates.tribunal.llm_extractor import (
    MockPromiseExtractor,
    VerbalPromise,
)

CORE_ASSETS = ["hotel_schema.json", "faq_schema.json", "boton_whatsapp.html"]
GEO_ASSETS = ["hotel_schema_rich.json", "faq_schema_rich.json", "boton_whatsapp_rich.html"]

PROPOSAL = "# PROPUESTA\n\nIncluimos el Botón de WhatsApp para su hotel.\n"

PROMISES = [VerbalPromise("Botón de WhatsApp", "whatsapp", "Intro", 0.95)]


def _ts():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _build_layout(tmp_path: Path, *, tier: str, coherence_pass: bool = True,
                  scenarios_complete: bool = True):
    """Crea output/<hotel>/ con assets + v4_audit/ y deliveries/, como el pipeline."""
    hotel_dir = tmp_path / "output" / "hotel"
    audit = hotel_dir / "v4_audit"
    audit.mkdir(parents=True)
    deliveries = tmp_path / "deliveries"
    deliveries.mkdir()

    for name in CORE_ASSETS + GEO_ASSETS:
        (hotel_dir / name).write_text(f"<!-- {name} -->\n", encoding="utf-8")

    gate_report = {
        "gate_results": [
            {"gate_name": "critical_recall", "passed": True, "value": 0.95,
             "message": "recall ok", "details": {"critical_issues_count": 0}},
            {"gate_name": "coherence", "passed": coherence_pass, "value": 0.9,
             "message": "coherencia ok" if coherence_pass else "coherencia FAIL",
             "details": {}},
            {"gate_name": "hard_contradictions", "passed": True, "value": 0,
             "message": "sin contradicciones duras", "details": {}},
        ]
    }
    (audit / f"gate_report_{_ts()}.json").write_text(
        json.dumps(gate_report), encoding="utf-8")

    scenarios = {
        "breakdown": {"evidence_tier": tier},
        "scenarios": {
            "conservative": {"adr": 200000, "occupancy": 0.45},
            "realistic": {"adr": 250000, "occupancy": 0.55},
        },
    }
    if scenarios_complete:
        scenarios["scenarios"]["optimistic"] = {"adr": 300000, "occupancy": 0.65}
    (audit / f"financial_scenarios_{_ts()}.json").write_text(
        json.dumps(scenarios), encoding="utf-8")

    (audit / "asset_generation_report.json").write_text(json.dumps({
        "summary": {"total_assets": len(CORE_ASSETS) + len(GEO_ASSETS),
                    "generated": len(CORE_ASSETS) + len(GEO_ASSETS), "failed": 0},
        "assets": [],
    }), encoding="utf-8")

    (audit / "proposal_asset_matrix.json").write_text(json.dumps({
        "entries": [{"service_name": "Botón de WhatsApp",
                     "pain_ids": ["no_whatsapp_visible"], "status": "LINKED"}],
        "delivery_ready": True,
        "summary": {"promised": 1},
    }, ensure_ascii=False), encoding="utf-8")

    (audit / "02_PROPUESTA_COMERCIAL.md").write_text(PROPOSAL, encoding="utf-8")

    return hotel_dir, audit, deliveries


def _run_flow(tmp_path: Path, *, tier: str, coherence_pass: bool = True,
              scenarios_complete: bool = True, gate_blocking_enabled: bool = True):
    """Réplica del cableado main.py FASE-T1 → write → 4 Bots → T1b → entrega."""
    hotel_dir, audit, deliveries = _build_layout(
        tmp_path, tier=tier, coherence_pass=coherence_pass,
        scenarios_complete=scenarios_complete)

    judge = TribunalJudge(audit, deliveries, hotel_id="hotel")
    acta = judge.evaluate()

    packager = DeliveryPackager(tmp_path / "output", deliveries)
    zip_tmp = packager.write(
        hotel_id="hotel",
        output_dir=str(hotel_dir),
        hotel_name="Hotel Sintético",
        geo_score=80,
        core_assets=list(CORE_ASSETS),
        geo_assets=list(GEO_ASSETS),
    )

    extractor = MockPromiseExtractor(list(PROMISES))
    written = {}
    for key, run in (
        ("diagnosis_reviewer", lambda: DiagnosisReviewer(audit).write_report()),
        ("asset_reviewer", lambda: AssetReviewer(audit, deliveries).write_report()),
        ("alignment_reviewer", lambda: AlignmentReviewer(audit).write_report(extractor)),
        ("honesty_reviewer", lambda: HonestyReviewer(audit, deliveries).write_report(extractor)),
    ):
        try:
            written[key] = run()
        except Exception:  # noqa: BLE001 — igual que main.py: never-block → None
            written[key] = None

    reports = judge.collect_reviewer_reports(written)
    acta = judge.enrich(acta, reports)
    blocks = blocks_delivery_zip(acta)
    outcome = judge.finalize(
        acta, reports, blocks=blocks, gate_blocking_enabled=gate_blocking_enabled)

    ActaWriter(audit).write(acta)

    if outcome.blocks_publish:
        from main import _compute_package_evidence
        acta["package_evidence"] = {
            "suppressed": True, "path": str(zip_tmp),
            **_compute_package_evidence(Path(zip_tmp)),
        }
        ActaWriter(audit).write(acta)
        packager.suppress(zip_tmp)
        final_zip = None
    else:
        final_zip = packager.publish(zip_tmp)

    return {
        "acta": acta, "outcome": outcome, "audit": audit,
        "deliveries": deliveries, "final_zip": final_zip, "zip_tmp": zip_tmp,
        "reports": reports,
    }


def _zips_in(deliveries: Path):
    return sorted(p.name for p in deliveries.glob("*.zip*"))


def test_perfil1_tier_a_todo_ok_publica():
    """Camino causal 1 (flujo real): gates OK + revisores OK → publish."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        r = _run_flow(Path(td), tier="A")
        assert r["outcome"].verdict == VERDICT_APPROVED, \
            f"verdict={r['outcome'].verdict} clauses={ {k: v['status'] for k, v in r['acta']['clauses'].items()} } " \
            f"reports={ [(x.reviewer, x.status.value, x.critical_count, x.recommendation) for x in r['reports']] }"
        assert not r["outcome"].blocks_publish
        assert r["final_zip"] and Path(r["final_zip"]).exists()
        assert not Path(r["zip_tmp"]).exists()
        assert _zips_in(r["deliveries"]) == ["hotel_" + datetime.now().strftime("%Y%m%d") + ".zip"]


def test_perfil2_donalfonso_anonimizado_gates_ok_revisor_objeta_bloquea():
    """Camino causal 2 (flujo real): MISMAS gates que el perfil 1, revisor objeta
    con CRITICAL → BLOQUEADO → ZIP suprimido + package_evidence en el acta (AC-G3).

    Perfil = caso Don Alfonso anonimizado: techo B+ por analítica ausente y
    bloqueo por hallazgo verificado de un revisor (como en la corrida del 2026-09-14).
    """
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        r = _run_flow(Path(td), tier="B+", scenarios_complete=False)
        assert r["acta"]["evidence_tier"] == "B+"
        assert r["outcome"].verdict == VERDICT_BLOCKED
        assert r["outcome"].blocks_publish
        honesty = [x for x in r["reports"] if x.reviewer == "honesty_reviewer"][0]
        assert honesty.critical_count >= 1
        assert not Path(r["zip_tmp"]).exists()
        assert _zips_in(r["deliveries"]) == []
        pe = r["acta"].get("package_evidence") or {}
        assert pe.get("suppressed") is True
        assert pe.get("sha256") and len(pe["sha256"]) == 64
        assert pe.get("member_count", 0) > 0
        md = (r["audit"] / "acta_revision.md").read_text(encoding="utf-8")
        assert "Evidencia del Paquete Suprimido" in md
        assert pe["sha256"] in md


def test_perfil3_gates_ya_bloquean_con_revisores_limpios():
    """Camino causal 3 (flujo real): gate FAIL (P6.6) con los 4 revisores limpios
    → BLOQUEADO por regla 1. Causa separada del perfil 2 (crítico: mismo ZIP
    suprimido, distinto mecanismo — AC-G5 pide separar las causas)."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        r = _run_flow(Path(td), tier="A", coherence_pass=False)
        assert r["acta"]["clauses"]["P6.6"]["status"] == "FAIL"
        assert all(x.critical_count == 0 for x in r["reports"]), \
            f"los revisores deben estar limpios: {[(x.reviewer, x.critical_count) for x in r['reports']]}"
        assert r["outcome"].verdict == VERDICT_BLOCKED
        assert r["outcome"].blocks_publish
        assert _zips_in(r["deliveries"]) == []


def test_perfil4_primer_piso_bplus_decision_partida():
    """L-P6.2 en flujo real: tier B+ con todo limpio → el Juez cap en CONDITIONAL
    (no BLOCKED) y `blocks_delivery_zip` no bloquea → la entrega la decide el
    caller. Con gates permitiendo, el ZIP se publica."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        r = _run_flow(Path(td), tier="B+")
        assert r["outcome"].verdict == VERDICT_CONDITIONAL
        assert r["acta"]["first_floor_rule"]["applied"] is True
        assert not r["outcome"].blocks_publish
        assert r["final_zip"] and Path(r["final_zip"]).exists()


def test_perfil5_kill_switch_llaves_separadas():
    """L-P6.1 en flujo real: mismo input que el perfil 2 pero
    `gate_blocking_enabled=False` → la segunda llave del `and` abre la publicación
    y el acta lo declara (`suppressed_by_operator`), nunca en silencio."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        r = _run_flow(Path(td), tier="B+", scenarios_complete=False,
                      gate_blocking_enabled=False)
        assert r["outcome"].verdict == VERDICT_BLOCKED
        assert not r["outcome"].blocks_publish
        assert r["acta"]["enforcement"]["suppressed_by_operator"] is True
        assert r["final_zip"] and Path(r["final_zip"]).exists()


def test_acg1_orden_publicado_usa_ruta_real_del_zip():
    """AC-G1 (R6): el IMPLEMENTATION_ORDER.md dentro del ZIP publicado muestra la
    ruta real del asset (dest que el packager escribió), no el nombre suelto."""
    import tempfile
    import zipfile
    with tempfile.TemporaryDirectory() as td:
        r = _run_flow(Path(td), tier="A")
        with zipfile.ZipFile(r["final_zip"]) as zf:
            order = zf.read("IMPLEMENTATION_ORDER.md").decode("utf-8")
        assert "ASSETS/hotel_schema.json" in order
        assert "ASSETS/boton_whatsapp_rich.html" in order
        # no stub (F-P4.1): secciones con contenido real, muy por encima de los ~470 B
        assert len(order.encode("utf-8")) > 1000
        assert "### 1." in order
