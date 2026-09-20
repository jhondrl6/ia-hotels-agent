"""FASE-0 / T1 PRE — camino real del `critical_recall = 1.0` de la corrida medida.

Reproduce EN MEMORIA el gate sobre el assessment de `output/TAREA7-2026-09-19/`
(sin escribir ni modificar nada bajo `output/`, contrato de ejecución §"Lectura de
corridas ajenas") y responde las tres preguntas que el prompt exige antes de editar:

1. ¿Qué rama produjo el 1.0? Se identifica por el SÍMBOLO que la devuelve (R2.2),
   no por número de línea:
     - campo directo `assessment["critical_recall"]`
     - `return 1.0` de `PublicationGatesOrchestrator._extract_critical_recall`
       con `critical_issues` NO vacío y `_evident_critical_missed == 0`  → fundado
     - `return 1.0` con `critical_issues` vacío + `audit_schema`         → derivado SR-H2
2. ¿Qué viajó serializado? Compara lo reconstruido contra el `gate_report_*.json`
   archivado (valor y `details`).
3. ¿El writer del reporte filtra `details`? Se lee la fuente de
   `main._build_gate_report_payload` y se comprueba si ya serializa `r.details`.

Salida: `pre_camino_gate.json` en este mismo directorio.
"""

import inspect
import json
import sys
from pathlib import Path
from types import SimpleNamespace

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

from main import _build_gate_report_payload  # noqa: E402
from modules.assessment_builder import AssessmentBuilder  # noqa: E402
from modules.quality_gates.publication_gates import (  # noqa: E402
    PublicationGateConfig,
    PublicationGatesOrchestrator,
)

RUN = REPO / "output" / "TAREA7-2026-09-19" / "v4_complete" / "hotel_don_alfonso" / "v4_audit"
SCHEMA_KEYS = (
    "hotel_schema_detected",
    "hotel_schema_valid",
    "hotel_confidence",
    "faq_schema_detected",
    "faq_schema_valid",
    "faq_confidence",
)


def _load(name):
    with open(RUN / name, "r", encoding="utf-8") as fh:
        return json.load(fh)


class AuditShim:
    """Reconstruye lo que `with_audit` / `with_audit_data` leen del auditor."""

    def __init__(self, raw):
        self._raw = raw
        self.critical_issues = list(raw.get("overall", {}).get("critical_issues") or [])
        self.schema = SimpleNamespace(**{k: raw["schema"].get(k) for k in SCHEMA_KEYS})

    def to_dict(self):
        return self._raw


def main():
    audit_raw = _load("audit_report_20260919_150111.json")
    geo_flow = _load("geo_flow_result.json")
    archived_gate_report = _load("gate_report_20260919_150131.json")

    builder = AssessmentBuilder()
    builder.with_core("https://www.donalfonsohotel.com/", "Hotel Don Alfonso")
    audit = AuditShim(audit_raw)
    # `with_audit` asigna la MISMA lista del auditor y `with_geo_flow` le anexa el
    # issue de banda GEO: se copia antes de construir para medir el delta real.
    audit_issues_de_audit = list(audit.critical_issues)
    builder.with_audit(audit)
    builder.with_audit_data(audit.to_dict())
    builder.with_geo_flow(geo_flow)
    assessment = builder.build()

    orch = PublicationGatesOrchestrator(PublicationGateConfig())
    critical_issues = list(assessment.get("critical_issues") or [])
    missed = orch._evident_critical_missed(assessment, critical_issues)
    value = orch._extract_critical_recall(assessment)
    gate_result = orch._critical_recall_gate(assessment)

    if "critical_recall" in assessment:
        branch = "_extract_critical_recall: campo directo assessment['critical_recall']"
    elif critical_issues:
        branch = (
            "_extract_critical_recall: `return 1.0  # All critical issues were detected` "
            "(critical_issues no vacio y _evident_critical_missed == 0) -> RECALL FUNDADO"
            if not missed
            else "_extract_critical_recall: ratio critical_issues/(critical_issues+missed)"
        )
    elif assessment.get("audit_schema"):
        branch = (
            "_extract_critical_recall: `return 1.0` con critical_issues vacio + audit_schema "
            "-> camino derivado SR-H2 (el que el gate ya anota)"
        )
    else:
        branch = "_extract_critical_recall: `return None` (metrica realmente ausente)"

    archived_recall = next(
        g for g in archived_gate_report["gate_results"] if g["gate_name"] == "critical_recall"
    )

    payload_src = inspect.getsource(_build_gate_report_payload)
    writer_serializes_details = '"details": r.details' in payload_src

    out = {
        "fuente": str(RUN.relative_to(REPO)).replace("\\", "/"),
        "critical_issues_reconstruidos": critical_issues,
        "critical_issues_count": len(critical_issues),
        "critical_issues_detectados_por_el_audit": len(audit_issues_de_audit),
        "geo_flow_aporto_issue": len(critical_issues) - len(audit_issues_de_audit),
        "performance_status": audit_raw.get("performance", {}).get("status"),
        "audit_schema_no_vacio": bool(assessment.get("audit_schema")),
        "critical_recall_directo_en_assessment": "critical_recall" in assessment,
        "evident_critical_missed": missed,
        "valor_extraido": value,
        "ruta_identificada_por_simbolo": branch,
        "gate_reconstruido": {
            "passed": gate_result.passed,
            "status": gate_result.status.value,
            "value": gate_result.value,
            "details": gate_result.details,
        },
        "gate_archivado": {
            "passed": archived_recall["passed"],
            "status": archived_recall["status"],
            "value": archived_recall["value"],
            "details": archived_recall["details"],
        },
        "coincide_con_el_archivo": (
            gate_result.value == archived_recall["value"]
            and gate_result.details == archived_recall["details"]
        ),
        "_build_gate_report_payload_ya_serializa_details": writer_serializes_details,
        "conclusion": (
            "El 1.0 viaj\u00f3 con details vac\u00edo porque la \u00fanica rama anotada del gate es la "
            "derivada SR-H2; la corrida tom\u00f3 la rama FUNDADA (critical_issues no vac\u00edo y "
            "_evident_critical_missed == 0). El writer del reporte NO filtra details, "
            "as\u00ed que no se toca."
        ),
    }
    dest = Path(__file__).with_name("pre_camino_gate.json")
    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
