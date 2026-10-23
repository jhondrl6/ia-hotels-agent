"""AC2 (FASE-C, ítem C): el veredicto condicional publica `conditional_reason`.

Las tres causas se provocan con protocolos sintéticos (acta + informes de revisor
fabricados) y se LEEN del `acta_revision.json` que escribe el `ActaWriter` real
(R2.4 / L-P3A.2: la clave la dicta el parser del artefacto serializado, nunca el
diccionario en memoria).

Mutation check (R2.8 / L-T4A.5): los asserts del veredicto usan el LITERAL del
contrato, no la constante `VERDICT_CONDITIONAL`. Si alguien restaura el nombre
largo viejo (reconstruido por piezas en `VIEJO_LITERAL`) o elimina la causa del
acta, estos tests se ponen en rojo; el par rojo/verde queda en
`evidence/CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22/FASE-C/`.
"""

import json
from pathlib import Path

from modules.quality_gates.tribunal.acta_writer import ActaWriter
from modules.quality_gates.tribunal.judge import TribunalJudge
from modules.quality_gates.tribunal.outcome import (
    EXPECTED_REVIEWERS,
    ReviewerReport,
    ReviewerStatus,
    not_run_reports,
)
from modules.quality_gates.tribunal.review_inputs import ReviewInputs

# El literal viejo se reconstruye POR PIEZAS: AC2 exige 0 ocurrencias vivas del
# literal completo en la población de código/tests (grep crudo en evidencia), y el
# mutation check necesita el string completo para fallar si alguien lo restaura en
# el artefacto serializado.
VIEJO_LITERAL = "APROBADO-CONDICIONAL" + "-PENDING-ONBOARDING"


def _clauses(status="PASS"):
    return {
        f"P6.{i}": {
            "status": status,
            "source_artifact": "protocolo-sintetico",
            "finding": "protocolo sintetico",
        }
        for i in range(1, 7)
    }


def _reports_ok():
    return [
        ReviewerReport(
            reviewer=spec.reviewer,
            status=ReviewerStatus.OK_NO_FINDINGS,
            clauses=spec.clauses,
        )
        for spec in EXPECTED_REVIEWERS
    ]


def _judge(tmp_path, has_onboarding):
    """Juez real sobre insumos sintéticos; `has_onboarding` viaja en el manifiesto."""
    audit = tmp_path / "v4_audit"
    audit.mkdir(parents=True, exist_ok=True)
    manifest = {"run_id": "ac2-sintetico", "documents": []}
    if has_onboarding is not None:
        manifest["has_onboarding"] = has_onboarding
    inputs = ReviewInputs(v4_audit_dir=audit, manifest=manifest)
    return TribunalJudge(
        v4_audit_dir=audit,
        deliveries_dir=tmp_path / "deliveries",
        hotel_id="hotel-ac2",
        review_inputs=inputs,
    )


def _acta_base(tier, first_floor_applied, clauses):
    return {
        "verdict": "PRE-REVISION",
        "conditional_reason": None,
        "evidence_tier": tier,
        "clauses_evaluated": 6,
        "clauses": clauses,
        "reviewer_reports": [],
        "first_floor_rule": {
            "applied": first_floor_applied,
            "reason": "protocolo sintetico",
            "source_artifact": "protocolo-sintetico",
        },
        "timestamp": "2026-10-23T00:00:00",
        "hotel_id": "hotel-ac2",
    }


def _cerrar_y_leer(tmp_path, acta, reports):
    """finalize() + ActaWriter real; retorna el JSON LEÍDO del disco y el MD."""
    judge_acta = acta
    json_path, md_path = ActaWriter(tmp_path / "out").write(judge_acta)
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    md_text = Path(md_path).read_text(encoding="utf-8")
    return data, md_text


def _protocolo(tier, first_floor, clauses, reports, has_onboarding, tmp_path):
    judge = _judge(tmp_path, has_onboarding)
    acta = judge.enrich(_acta_base(tier, first_floor, clauses), reports)
    judge.finalize(acta, reports, blocks=False)
    return _cerrar_y_leer(tmp_path, acta, reports)


# ── Causa 1: ANALYTICS_CEILING ─────────────────────────────────────────────


def test_analytics_ceiling_con_onboarding_verificado(tmp_path):
    """Tier B+ (primer piso) + onboarding verificado → ANALYTICS_CEILING.

    Lo único que falta es analytics; la etiqueta humana NO dice «Pendiente de
    onboarding».
    """
    data, md_text = _protocolo(
        tier="B+",
        first_floor=True,
        clauses=_clauses(),
        reports=_reports_ok(),
        has_onboarding=True,
        tmp_path=tmp_path,
    )

    assert data["verdict"] == "APROBADO-CONDICIONAL"
    assert data["conditional_reason"] == "ANALYTICS_CEILING"
    assert "ANALYTICS_CEILING" in md_text
    assert "Pendiente de onboarding" not in md_text


# ── Causa 2: ONBOARDING_INCOMPLETE ─────────────────────────────────────────


def test_onboarding_incomplete_sin_onboarding(tmp_path):
    """Tier B (primer piso) sin onboarding → ONBOARDING_INCOMPLETE."""
    data, _ = _protocolo(
        tier="B",
        first_floor=True,
        clauses=_clauses(),
        reports=_reports_ok(),
        has_onboarding=False,
        tmp_path=tmp_path,
    )

    assert data["verdict"] == "APROBADO-CONDICIONAL"
    assert data["conditional_reason"] == "ONBOARDING_INCOMPLETE"


def test_onboarding_incomplete_sin_transporte(tmp_path):
    """Sin `has_onboarding` en el manifiesto (None) cuenta como «sin verificado».

    DA-C3: la causa nombra lo que el tribunal pudo verificar; el transporte
    ausente no se lee como onboarding presente.
    """
    data, _ = _protocolo(
        tier="C",
        first_floor=True,
        clauses=_clauses(),
        reports=_reports_ok(),
        has_onboarding=None,
        tmp_path=tmp_path,
    )

    assert data["verdict"] == "APROBADO-CONDICIONAL"
    assert data["conditional_reason"] == "ONBOARDING_INCOMPLETE"


# ── Causa 3: UNCERTIFIABLE_CLAUSES ─────────────────────────────────────────


def test_uncertifiable_clauses_clausula_no_certificable(tmp_path):
    """Tier A sin primer piso, cláusula certificable no PASS → UNCERTIFIABLE_CLAUSES."""
    clauses = _clauses()
    clauses["P6.3"] = {
        "status": "NOT_EVALUABLE",
        "source_artifact": "protocolo-sintetico",
        "finding": "asset_generation_report no disponible",
    }
    data, _ = _protocolo(
        tier="A",
        first_floor=False,
        clauses=clauses,
        reports=_reports_ok(),
        has_onboarding=True,
        tmp_path=tmp_path,
    )

    assert data["verdict"] == "APROBADO-CONDICIONAL"
    assert data["conditional_reason"] == "UNCERTIFIABLE_CLAUSES"


def test_uncertifiable_clauses_revisores_no_leidos(tmp_path):
    """Tier A sin primer piso, revisores en NOT_RUN → UNCERTIFIABLE_CLAUSES."""
    data, _ = _protocolo(
        tier="A",
        first_floor=False,
        clauses=_clauses(),
        reports=not_run_reports(),
        has_onboarding=True,
        tmp_path=tmp_path,
    )

    assert data["verdict"] == "APROBADO-CONDICIONAL"
    assert data["conditional_reason"] == "UNCERTIFIABLE_CLAUSES"


# ── Contrato: causa solo en el condicional; sin literal viejo ──────────────


def test_veredictos_no_condicionales_publican_causa_nula(tmp_path):
    """Aprobado y bloqueado publican `conditional_reason: null` (causa = solo condicional)."""
    data_aprobado, _ = _protocolo(
        tier="A",
        first_floor=False,
        clauses=_clauses(),
        reports=_reports_ok(),
        has_onboarding=True,
        tmp_path=tmp_path / "aprobado",
    )
    assert data_aprobado["verdict"] == "APROBADO-PARA-ENTREGA"
    assert data_aprobado["conditional_reason"] is None

    clauses_bloqueadas = _clauses()
    clauses_bloqueadas["P6.1"] = {
        "status": "FAIL",
        "source_artifact": "protocolo-sintetico",
        "finding": "critical_recall FAIL",
    }
    data_bloqueado, _ = _protocolo(
        tier="A",
        first_floor=False,
        clauses=clauses_bloqueadas,
        reports=_reports_ok(),
        has_onboarding=True,
        tmp_path=tmp_path / "bloqueado",
    )
    assert data_bloqueado["verdict"] == "BLOQUEADO"
    assert data_bloqueado["conditional_reason"] is None


def test_acta_serializada_sin_el_literal_viejo(tmp_path):
    """El acta de las tres causas no contiene el literal viejo (JSON ni MD)."""
    clauses_no_certificable = _clauses()
    clauses_no_certificable["P6.3"] = {
        "status": "NOT_EVALUABLE",
        "source_artifact": "protocolo-sintetico",
        "finding": "asset_generation_report no disponible",
    }
    protocolos = [
        ("B+", True, _clauses(), _reports_ok(), True),
        ("B", True, _clauses(), _reports_ok(), False),
        ("A", False, clauses_no_certificable, _reports_ok(), True),
    ]
    for tier, first_floor, clauses, reports, has_onboarding in protocolos:
        data, md_text = _protocolo(
            tier=tier,
            first_floor=first_floor,
            clauses=clauses,
            reports=reports,
            has_onboarding=has_onboarding,
            tmp_path=tmp_path / tier.replace("+", "mas"),
        )
        serializado = json.dumps(data, ensure_ascii=False) + md_text
        assert VIEJO_LITERAL not in serializado
        assert data["conditional_reason"] in (
            "ANALYTICS_CEILING",
            "ONBOARDING_INCOMPLETE",
            "UNCERTIFIABLE_CLAUSES",
        )
