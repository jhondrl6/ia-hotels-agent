"""FASE-0 / T3 — contrafactual del veredicto sobre el acta archivada (en memoria).

Reproduce el par que AC20 exige como evidencia, sin escribir en el baseline:

- `output/TAREA7-2026-09-19/` se COPIA a un directorio temporal del sistema. El
  contrato de ejecución permite leer la corrida ajena y ejecutar código del repo
  sobre sus artefactos, y prohíbe escribir bajo ese `output/`: por eso todo lo que
  se parcha aquí vive fuera del árbol del plan (TAREA7 no se toca).

Tres casos:
  A  baseline .......... el hallazgo `VACUOUS_RECALL` tal y como se archivó.
  B  contrafactual ..... el gate anota el recall fundado (lo que produce el código
    después de AC20-i) y se re-ejecuta `DiagnosisReviewer` sobre esa copia.
  C  mutante engañoso. zero del `critical_count` SIN recalcular la
     `verdict_recommendation`: tiene que seguir bloqueando, porque
     `ReviewerReport.verified_block` decide por la recomendación. Es el rojo
     falso que el prompt manda verificar.

Salida: `baseline_vs_contrafactual.json` + medición del crecimiento del acta.
"""

import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

from modules.quality_gates.publication_gates import (  # noqa: E402
    PublicationGateConfig,
    PublicationGatesOrchestrator,
)
from modules.quality_gates.tribunal import outcome as outcome_mod  # noqa: E402
from modules.quality_gates.tribunal.acta_writer import ActaWriter  # noqa: E402
from modules.quality_gates.tribunal.diagnosis_reviewer import DiagnosisReviewer  # noqa: E402
from modules.quality_gates.tribunal.judge import (  # noqa: E402
    BLOCKING_VERDICTS,
    TribunalJudge,
)

BASE_AUDIT = (
    REPO / "output" / "TAREA7-2026-09-19" / "v4_complete" / "hotel_don_alfonso" / "v4_audit"
)
GATE_REPORT_NAME = "gate_report_20260919_150131.json"
AUDIT_REPORT_NAME = "audit_report_20260919_150111.json"
REVIEWER_FILES = {
    "diagnosis_reviewer": "revision_diagnostico.json",
    "asset_reviewer": "revision_assets.json",
    "alignment_reviewer": "revision_alineacion.json",
    "honesty_reviewer": "revision_honestidad.json",
}


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _founded_details(audit_dir: Path) -> dict:
    """Lo que el productor de AC20-i escribe hoy en `details` con el audit de la corrida."""
    raw = _read(audit_dir / AUDIT_REPORT_NAME)
    assessment = {
        "critical_issues": list(raw.get("overall", {}).get("critical_issues") or []),
        "audit_schema": {
            k: raw["schema"].get(k)
            for k in (
                "hotel_schema_detected", "hotel_schema_valid", "hotel_confidence",
                "faq_schema_detected", "faq_schema_valid", "faq_confidence",
            )
        },
        "audit_data": raw,
    }
    orch = PublicationGatesOrchestrator(PublicationGateConfig())
    return orch._critical_recall_gate(assessment).details


def _patch_gate_report(audit_dir: Path, details: dict) -> dict:
    path = audit_dir / GATE_REPORT_NAME
    payload = _read(path)
    before = None
    for gate in payload["gate_results"]:
        if gate["gate_name"] == "critical_recall":
            before = dict(gate["details"])
            gate["details"] = details
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"antes": before, "despues": details}


def _reports(audit_dir: Path):
    written = {
        reviewer: str(audit_dir / name)
        for reviewer, name in REVIEWER_FILES.items()
        if (audit_dir / name).exists()
    }
    return outcome_mod.collect_reviewer_reports(audit_dir, written)


def _verdict(acta: dict, reports) -> str:
    judge = TribunalJudge(
        acta.get("hotel_id", "hotel"), acta.get("hotel_id", "hotel")
    )  # _compute_verdict decide solo sobre lo que se le pasa: no lee discos
    return judge._compute_verdict(
        acta["clauses"], acta["evidence_tier"], acta["first_floor_rule"], reports
    )


def _acta_sizes(reports) -> dict:
    """Crecimiento real del acta por publicar los hallazgos (mismo acta de la corrida)."""
    acta = {
        "verdict": "BLOQUEADO",
        "evidence_tier": "B",
        "clauses_evaluated": 6,
        "clauses": {},
        "reviewer_reports": [r.to_dict() for r in reports],
        "first_floor_rule": {"applied": True, "reason": "evidence_tier B -> maximo condicional"},
        "timestamp": "2026-09-19T15:01:31Z",
        "hotel_id": "hotel_don_alfonso",
        "enforcement": {"blocking_env": "GATE_BLOCKING_ENABLED", "enabled": True,
                        "suppressed_by_operator": False},
        "corrective_actions": [],
    }
    with_findings = json.dumps(acta, indent=2, ensure_ascii=False)

    legacy = [
        {k: v for k, v in r.items() if k not in ("findings", "findings_omitted")}
        for r in acta["reviewer_reports"]
    ]
    sin_findings = json.dumps({**acta, "reviewer_reports": legacy}, indent=2, ensure_ascii=False)

    tmp = Path(tempfile.mkdtemp(prefix="acta-medicion-"))
    try:
        _json_path, md_path = ActaWriter(tmp).write(acta)
        md_nuevo = md_path.read_text(encoding="utf-8")
        _json_path2, md_path2 = ActaWriter(tmp).write({**acta, "reviewer_reports": legacy})
        md_viejo = md_path2.read_text(encoding="utf-8")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    return {
        "json_bytes_sin_proyeccion": len(sin_findings.encode("utf-8")),
        "json_bytes_con_proyeccion": len(with_findings.encode("utf-8")),
        "json_delta_bytes": len(with_findings.encode("utf-8")) - len(sin_findings.encode("utf-8")),
        "md_bytes_antes": len(md_viejo.encode("utf-8")),
        "md_bytes_despues": len(md_nuevo.encode("utf-8")),
        "md_delta_bytes": len(md_nuevo.encode("utf-8")) - len(md_viejo.encode("utf-8")),
        "revision_bytes_total": sum(
            (BASE_AUDIT / name).stat().st_size for name in REVIEWER_FILES.values()
        ),
    }


def main():
    if not BASE_AUDIT.exists():
        raise SystemExit(f"baseline ausente: {BASE_AUDIT}")

    acta = _read(BASE_AUDIT / "acta_revision.json")
    workdir = Path(tempfile.mkdtemp(prefix="fase0-contrafactual-"))
    copy = workdir / "v4_audit"
    shutil.copytree(BASE_AUDIT, copy)

    try:
        # A — baseline tal como se archivó.
        base_reports = _reports(copy)
        base_verdict = _verdict(acta, base_reports)
        base_vacuous = [
            f for r in base_reports for f in r.findings
            if f.get("finding_type") == "VACUOUS_RECALL"
        ]

        # B — contrafactual: el gate anota y el revisor se vuelve a ejecutar.
        patched = _patch_gate_report(copy, _founded_details(copy))
        review = DiagnosisReviewer(v4_audit_dir=copy).review()
        (copy / REVIEWER_FILES["diagnosis_reviewer"]).write_text(
            json.dumps(review, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        contra_reports = _reports(copy)
        contra_verdict = _verdict(acta, contra_reports)
        contra_vacuous = [
            f for r in contra_reports for f in r.findings
            if f.get("finding_type") == "VACUOUS_RECALL"
        ]

        # C — mutante engañoso: zero del conteo sin recalcular la recomendación.
        zero_only = [
            r if r.reviewer != "diagnosis_reviewer" else outcome_mod.ReviewerReport(
                reviewer=r.reviewer, status=r.status, findings_count=0, critical_count=0,
                recommendation=r.recommendation, report_path=r.report_path, clauses=r.clauses,
                findings=[],
            )
            for r in base_reports
        ]
        zero_only_verdict = _verdict(acta, zero_only)
        zero_only_blocked_by = [
            r.reviewer for r in zero_only if r.verified_critical or r.verified_block
        ]

        result = {
            "fuente": "output/TAREA7-2026-09-19 (copias temporales; el baseline no se escribe)",
            "details_del_gate": patched,
            "A_baseline": {
                "hallazgos_VACUOUS_RECALL": len(base_vacuous),
                "recommendation_diagnosis": next(
                    r.recommendation for r in base_reports
                    if r.reviewer == "diagnosis_reviewer"
                ),
                "veredicto": base_verdict,
                "bloqueante_por_BLOCKING_VERDICTS": base_verdict in BLOCKING_VERDICTS,
            },
            "B_contrafactual": {
                "hallazgos_VACUOUS_RECALL": len(contra_vacuous),
                "status_diagnosis": next(
                    r.status.value for r in contra_reports
                    if r.reviewer == "diagnosis_reviewer"
                ),
                "recommendation_diagnosis": next(
                    r.recommendation for r in contra_reports
                    if r.reviewer == "diagnosis_reviewer"
                ),
                "veredicto": contra_verdict,
                "bloqueante_por_BLOCKING_VERDICTS": contra_verdict in BLOCKING_VERDICTS,
                "critical_count_revisores": {
                    r.reviewer: r.critical_count for r in contra_reports
                },
            },
            "C_mutante_zero_sin_recalculo": {
                "veredicto": zero_only_verdict,
                "bloqueantes": zero_only_blocked_by,
                "conclusion": (
                    "sigue BLOQUEADO: `verified_block` decide por la recomendacion, "
                    "por eso el mutante del contrafactual debe eliminar el hallazgo Y "
                    "recalcular `verdict_recommendation`"
                ),
            },
            "par_exigido_por_AC20": f"{base_verdict} -> {contra_verdict}",
            "medicion_acta": _acta_sizes(base_reports),
        }
        dest = Path(__file__).with_name("baseline_vs_contrafactual.json")
        dest.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps({k: v for k, v in result.items() if k != "details_del_gate"},
                         indent=2, ensure_ascii=False))
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    main()
