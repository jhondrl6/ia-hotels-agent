"""FASE-P2 — Veredicto enriquecido: los cuatro estados del revisor y su consecuencia.

Cubren AC-E0 (cuatro estados distinguibles y sección siempre presente), AC-E1
(``reviewer_reports`` de longitud 4 poblado desde el DTO), AC-E2 (CRITICAL verificado
o BLOQUEAR → veredicto bloqueante), AC-E3 (never-block), AC-E4 (kill switch heredado)
y la no-colapso de estados que exige NR8.

Los estados se producen escribiendo el artefacto real del Bot (con la forma que
emite el pipeline, ver ``evidence/FASE-E2E/revision_*.json``), no con un fixture que
solo pudiera producir uno de ellos (L-PF10).
"""

import json

import pytest

from modules.quality_gates.tribunal.acta_writer import ActaWriter
from modules.quality_gates.tribunal.judge import (
    BLOCKING_VERDICTS,
    TribunalJudge,
    VERDICT_BLOCKED,
    VERDICT_CONDITIONAL,
    VERDICT_RETURN,
    blocks_delivery_zip,
)
from modules.quality_gates.tribunal.outcome import (
    EXPECTED_REVIEWERS,
    ReviewerStatus,
    collect_reviewer_reports,
)

REPORT_FILES = {spec.reviewer: spec.report_filename for spec in EXPECTED_REVIEWERS}
REPORT_CLAUSES = {spec.reviewer: list(spec.clauses) for spec in EXPECTED_REVIEWERS}

CRITICAL_FINDING = {
    "severity": "CRITICAL",
    "clause": "P6.1",
    "finding_type": "VACUOUS_RECALL",
    "source_artifact": "gate_report_*.json",
    "description": "critical_recall=1.0 sin critical_issues_count",
    "pain_id": "critical_recall",
}
WARNING_FINDING = {
    "severity": "WARNING",
    "clause": "P6.1",
    "finding_type": "UNTRACEABLE_PAIN",
    "source_artifact": "pain_ledger.json",
    "description": "brecha sin pain_id trazable",
    "pain_id": "whatsapp_lead",
}


def write_bot_report(audit_dir, reviewer, findings, recommendation="APROBADO"):
    """Escribe el artefacto de un Bot con la forma real del pipeline."""
    payload = {
        "reviewer": reviewer,
        "clause": REPORT_CLAUSES[reviewer][0],
        "findings": findings,
        "summary": {
            "total_findings": len(findings),
            "critical": sum(1 for f in findings if f["severity"] == "CRITICAL"),
            "warning": sum(1 for f in findings if f["severity"] == "WARNING"),
            "info": 0,
        },
        "verdict_recommendation": recommendation,
        "timestamp": "2026-09-14T12:00:00",
        "artifacts_read": [],
    }
    path = audit_dir / REPORT_FILES[reviewer]
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path



def run_all_four_clean(audit_dir):
    """Los cuatro Bots escriben su informe sin hallazgos → mapa revisor→ruta."""
    written = {}
    for spec in EXPECTED_REVIEWERS:
        write_bot_report(audit_dir, spec.reviewer, [])
        written[spec.reviewer] = audit_dir / spec.report_filename
    return written


@pytest.fixture
def audit_dir(tmp_path):
    d = tmp_path / "v4_audit"
    d.mkdir()
    return d


@pytest.fixture
def judge(audit_dir, tmp_path):
    deliveries = tmp_path / "deliveries"
    deliveries.mkdir()
    return TribunalJudge(v4_audit_dir=audit_dir, deliveries_dir=deliveries, hotel_id="testhotel")


def acta_base(judge, written):
    """Primera pasada + segunda pasada con los informes ya en disco."""
    reports = judge.collect_reviewer_reports(written)
    return judge.enrich(judge.evaluate(), reports), reports


# ── AC-E1: reviewer_reports tipado y poblado ─────────────────────────────────


def test_reviewer_reports_refleja_los_cuatro_revisores(judge, audit_dir):
    """AC-E1: cuatro entradas, una por Bot, cuando los cuatro corrieron."""
    written = run_all_four_clean(audit_dir)
    acta, _ = acta_base(judge, written)

    assert len(acta["reviewer_reports"]) == 4
    assert [r["reviewer"] for r in acta["reviewer_reports"]] == [
        spec.reviewer for spec in EXPECTED_REVIEWERS
    ]
    for entry in acta["reviewer_reports"]:
        # FASE-0 (AC20-ii) amplió la forma declarada del bloque: `findings` es
        # clave fija y `findings_omitted` solo aparece cuando se supera el tope.
        # Se ata a esa regla y a la coherencia interna (findings ⊂ conteo), no a
        # un literal congelado — L-V2.3.
        assert set(entry) >= {
            "reviewer", "status", "findings_count", "critical_count",
            "recommendation", "report_path", "findings",
        }
        assert set(entry) <= {
            "reviewer", "status", "findings_count", "critical_count",
            "recommendation", "report_path", "findings", "findings_omitted",
        }
        assert len(entry["findings"]) <= entry["findings_count"]
        assert entry["report_path"] == REPORT_FILES[entry["reviewer"]]


# ── AC-E0 / NR8: un test por estado, nombrado por su causa ───────────────────


def test_los_4_revisores_no_hallan_nada(judge, audit_dir):
    """OK_NO_FINDINGS: los cuatro leyeron y no objetan nada."""
    written = run_all_four_clean(audit_dir)
    acta, reports = acta_base(judge, written)

    assert all(r.status is ReviewerStatus.OK_NO_FINDINGS for r in reports)
    assert all(r.findings_count == 0 and r.critical_count == 0 for r in reports)
    assert acta["verdict"] not in BLOCKING_VERDICTS


def test_artefacto_ausente(judge, audit_dir):
    """ARTIFACT_MISSING: el Bot corrió pero su informe no está en disco."""
    for spec in EXPECTED_REVIEWERS:
        write_bot_report(audit_dir, spec.reviewer, [])
    written = {
        spec.reviewer: audit_dir / "no_escrito_por_nadie.json"
        for spec in EXPECTED_REVIEWERS
    }
    acta, reports = acta_base(judge, written)

    assert {r.status for r in reports} == {ReviewerStatus.ARTIFACT_MISSING}
    assert acta["verdict"] not in BLOCKING_VERDICTS


def test_lector_fallido(judge, audit_dir):
    """READER_FAILED: el informe existe pero no es legible como tal."""
    for spec in EXPECTED_REVIEWERS:
        (audit_dir / spec.report_filename).write_text("{ no es json", encoding="utf-8")
    written = {spec.reviewer: audit_dir / spec.report_filename for spec in EXPECTED_REVIEWERS}
    acta, reports = acta_base(judge, written)

    assert {r.status for r in reports} == {ReviewerStatus.READER_FAILED}
    assert acta["verdict"] not in BLOCKING_VERDICTS


def test_los_revisores_no_corrieron(judge, audit_dir):
    """NOT_RUN: canario de cableado — nadie fue al Juez (contrato DA-P1.6 regla 4)."""
    acta, reports = acta_base(judge, {})

    assert {r.status for r in reports} == {ReviewerStatus.NOT_RUN}
    assert acta["verdict"] not in BLOCKING_VERDICTS
    assert all(r.report_path is None for r in reports)


def test_los_tres_estados_no_colapsan(judge, audit_dir):
    """NR8: sin hallazgos, ausente, fallido y no-corrido son cuatro cosas distintas.

    Colapsarlos convierte una mejora upstream en bloqueo o un fallo de lectura en
    aprobación; este test se rompe si la implementación vuelve a una sola clave.
    """
    write_bot_report(audit_dir, "diagnosis_reviewer", [])
    write_bot_report(audit_dir, "asset_reviewer", [WARNING_FINDING], "DEVOLVER-PRUEBAS")
    (audit_dir / REPORT_FILES["alignment_reviewer"]).write_text("{ roto", encoding="utf-8")

    written = {
        "diagnosis_reviewer": audit_dir / REPORT_FILES["diagnosis_reviewer"],
        "asset_reviewer": audit_dir / REPORT_FILES["asset_reviewer"],
        "alignment_reviewer": audit_dir / REPORT_FILES["alignment_reviewer"],
        "honesty_reviewer": audit_dir / "no_escribio_nada.json",
    }
    acta, reports = acta_base(judge, written)

    assert [r.status for r in reports] == [
        ReviewerStatus.OK_NO_FINDINGS,
        ReviewerStatus.OK_WITH_FINDINGS,
        ReviewerStatus.READER_FAILED,
        ReviewerStatus.ARTIFACT_MISSING,
    ]
    assert len({r.status.value for r in reports}) == 4

    _, md_path = ActaWriter(audit_dir / "acta").write(acta)
    rendered = md_path.read_text(encoding="utf-8")
    for status in ("sin hallazgos", "con hallazgos", "lector fallido", "artefacto ausente"):
        assert status in rendered, f"el MD no distingue el estado {status}"

    collapsed = {r.status.value for r in collect_reviewer_reports(audit_dir, {})}
    assert collapsed != {r.status.value for r in reports}, (
        "NOT_RUN debe seguir siendo distinguible de los fallos de lectura"
    )


def test_la_seccion_de_revisores_nunca_se_omite(judge, audit_dir):
    """AC-E0: un acta sin informes renderiza la sección, no la borra del MD."""
    acta = judge.evaluate()
    acta["reviewer_reports"] = []
    _, md_path = ActaWriter(audit_dir / "acta").write(acta)

    rendered = md_path.read_text(encoding="utf-8")
    assert "## Reportes de Revisores" in rendered
    for spec in EXPECTED_REVIEWERS:
        assert spec.reviewer in rendered
    assert "no corrió" in rendered


# ── AC-E2: la objeción verificada decide, y en el orden del contrato ─────────


def test_bloquear_de_un_revisor_bloquea_la_entrega(judge, audit_dir):
    """AC-E2: recomendación BLOQUEAR de un Bot → veredicto BLOQUEADO."""
    written = run_all_four_clean(audit_dir)
    write_bot_report(audit_dir, "diagnosis_reviewer", [CRITICAL_FINDING], "BLOQUEAR")

    acta, _ = acta_base(judge, written)
    assert acta["verdict"] == VERDICT_BLOCKED
    assert blocks_delivery_zip(acta) is True


def test_critical_verificado_por_un_revisor_bloquea(judge, audit_dir):
    """AC-E2: CRITICAL con status OK_* → BLOQUEADO, aunque su recomendación sea otra."""
    written = run_all_four_clean(audit_dir)
    write_bot_report(audit_dir, "asset_reviewer", [CRITICAL_FINDING], "DEVOLVER-PRUEBAS")

    acta, _ = acta_base(judge, written)
    assert acta["verdict"] == VERDICT_BLOCKED


def test_warning_de_revisor_no_degrada_bajo_el_primer_piso(judge, audit_dir):
    """Fila 5: solo WARNING/INFO no cambia el veredicto que darían los gates."""
    written = run_all_four_clean(audit_dir)
    write_bot_report(audit_dir, "diagnosis_reviewer", [WARNING_FINDING], "DEVOLVER-PRUEBAS")

    sin_revisores, _ = acta_base(judge, {})
    con_warning, _ = acta_base(judge, written)
    assert con_warning["verdict"] == sin_revisores["verdict"] == VERDICT_CONDITIONAL


def test_el_orden_de_la_matriz_es_parte_del_contrato(judge, audit_dir):
    """Fila 2 antes que la 3: un CRITICAL verificado manda sobre el gate P6.3."""
    (audit_dir / "asset_generation_report.json").write_text(
        json.dumps({"summary": {"total_assets": 5, "generated": 3, "failed": 2}}),
        encoding="utf-8",
    )
    written = run_all_four_clean(audit_dir)
    write_bot_report(audit_dir, "diagnosis_reviewer", [CRITICAL_FINDING], "BLOQUEAR")

    acta, _ = acta_base(judge, written)
    assert acta["clauses"]["P6.3"]["status"] == "FAIL"
    assert acta["verdict"] == VERDICT_BLOCKED


def test_un_fallo_de_lectura_nunca_bloquea(judge, audit_dir):
    """Invariantes de la fila 4: ausente / fallido / no-corrido no suprimen nada."""
    cases = {
        "artefacto_ausente": {"diagnosis_reviewer": audit_dir / "nada.json"},
        "lector_fallido": {"diagnosis_reviewer": None},
        "no_corrio": {},
    }
    for label, written in cases.items():
        acta, reports = acta_base(judge, written)
        assert acta["verdict"] not in BLOCKING_VERDICTS, label
        assert any(r.status.blocks_approval for r in reports), label


def test_revisor_que_revienta_no_rompe_la_corrida(judge, audit_dir):
    """AC-E3 (never-block): el fallo se registra como READER_FAILED y sigue la corrida."""
    written = run_all_four_clean(audit_dir)
    written["asset_reviewer"] = None

    acta, reports = acta_base(judge, written)
    by_name = {r.reviewer: r for r in reports}

    assert by_name["asset_reviewer"].status is ReviewerStatus.READER_FAILED
    assert by_name["diagnosis_reviewer"].status is ReviewerStatus.OK_NO_FINDINGS
    assert acta["verdict"] not in BLOCKING_VERDICTS


# ── AC-E4: el knob único del operador, con escape honesto ────────────────────


def test_el_knob_apagado_no_bloquea_pero_lo_declara(judge, audit_dir):
    """AC-E4: GATE_BLOCKING_ENABLED=false → no bloquea y el acta lo dice."""
    written = run_all_four_clean(audit_dir)
    write_bot_report(audit_dir, "diagnosis_reviewer", [CRITICAL_FINDING], "BLOQUEAR")
    acta, reports = acta_base(judge, written)

    outcome = judge.finalize(acta, reports, blocks=True, gate_blocking_enabled=False)

    assert outcome.blocks_publish is False
    assert outcome.enforcement.blocking_env == "GATE_BLOCKING_ENABLED"
    assert outcome.enforcement.enabled is False
    assert outcome.enforcement.suppressed_by_operator is True
    assert acta["enforcement"]["suppressed_by_operator"] is True


def test_el_knob_forzado_a_on_ejercita_el_bloqueo(judge, audit_dir):
    """AC-E4: con el knob a true el mismo veredicto sí suprime la publicación."""
    written = run_all_four_clean(audit_dir)
    write_bot_report(audit_dir, "diagnosis_reviewer", [CRITICAL_FINDING], "BLOQUEAR")
    acta, reports = acta_base(judge, written)

    outcome = judge.finalize(acta, reports, blocks=True, gate_blocking_enabled=True)

    assert outcome.blocks_publish is True
    assert outcome.enforcement.suppressed_by_operator is False


# ── AC-E5: consecuencia del bloqueo con dueño declarado ──────────────────────


def test_veredicto_bloqueante_deja_acciones_correctivas_con_dueno(judge, audit_dir):
    """AC-E5: acciones no vacías, con artefacto e instruction, y el acta las deriva."""
    written = run_all_four_clean(audit_dir)
    write_bot_report(audit_dir, "diagnosis_reviewer", [CRITICAL_FINDING], "BLOQUEAR")
    acta, reports = acta_base(judge, written)
    outcome = judge.finalize(acta, reports, blocks=True, gate_blocking_enabled=True)

    assert outcome.corrective_actions
    assert acta["corrective_actions"]
    for action in acta["corrective_actions"]:
        assert action["owner"]
        assert action["artifact"] == CRITICAL_FINDING["source_artifact"]
        assert action["finding_type"] == CRITICAL_FINDING["finding_type"]
        assert action["severity"] == "CRITICAL"

    _, md_path = ActaWriter(audit_dir / "acta").write(acta)
    rendered = md_path.read_text(encoding="utf-8")
    assert "## Acciones correctivas" in rendered
    assert CRITICAL_FINDING["finding_type"] in rendered


def test_bloqueo_por_gate_sin_hallazgo_de_revisor_tambien_tiene_dueno(judge, audit_dir):
    """Un bloqueo que viene de gates no deja el acta sin camino de reparación."""
    (audit_dir / "gate_report_20260914.json").write_text(
        json.dumps({"gate_results": [
            {"gate_name": "critical_recall", "passed": False, "value": 0.4,
             "message": "recall 40% < 90%"},
        ]}),
        encoding="utf-8",
    )
    written = run_all_four_clean(audit_dir)
    acta, reports = acta_base(judge, written)
    outcome = judge.finalize(acta, reports, blocks=True, gate_blocking_enabled=True)

    assert acta["verdict"] == VERDICT_BLOCKED
    assert [a.owner for a in outcome.corrective_actions] == ["quality-gates"]


def test_veredicto_no_bloqueante_no_inventa_acciones(judge, audit_dir):
    """Sin hallazgo bloqueante, corrective_actions queda vacía y el MD lo dice."""
    written = run_all_four_clean(audit_dir)
    acta, reports = acta_base(judge, written)
    judge.finalize(acta, reports, blocks=False, gate_blocking_enabled=True)

    assert acta["corrective_actions"] == []
    _, md_path = ActaWriter(audit_dir / "acta").write(acta)
    assert "Ninguna: el acta no declaró hallazgos bloqueantes." in md_path.read_text(
        encoding="utf-8"
    )


# ── Seguimiento cerrado por P2: el acta describe el mecanismo que sí se usó ───


def test_el_acta_nombra_la_fuente_real_del_tier(judge, audit_dir):
    """Sin literales en el writer: la fuente del tier la publica el Juez que leyó."""
    acta = judge.evaluate()
    _, md_path = ActaWriter(audit_dir / "acta1").write(acta)
    rendered = md_path.read_text(encoding="utf-8")
    assert "sin fuente de tier" in rendered
    assert "**Artefacto fuente**: `MANIFEST.json" not in rendered

    (audit_dir / "financial_scenarios_20260914_120000.json").write_text(
        json.dumps({"breakdown": {"evidence_tier": "B"}}), encoding="utf-8"
    )
    acta = judge.evaluate()
    assert (
        acta["first_floor_rule"]["source_artifact"]
        == "financial_scenarios_20260914_120000.json → breakdown.evidence_tier"
    )
    _, md_path = ActaWriter(audit_dir / "acta2").write(acta)
    assert "financial_scenarios_20260914_120000.json" in md_path.read_text(encoding="utf-8")
