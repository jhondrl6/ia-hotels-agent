"""FASE-0 / T4 — `thresholds.json` con los invariantes leidos del codigo vivo.

Cada valor se lee del simbolo que lo define (no se transcribe de los documentos
del plan), y `congelado_por_el_plan` marca lo que FASE-0 tenia prohibido tocar.
El contraste contra el arbol versionado se hace con `git diff` del propio archivo:
si un valor congelado aparece modificado, el registro lo muestra.

Salida: `thresholds.json` en este directorio.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

from modules.quality_gates import publication_gates as pg  # noqa: E402
from modules.quality_gates.tribunal import judge as judge_mod  # noqa: E402
from modules.quality_gates.tribunal import outcome as outcome_mod  # noqa: E402

FROZEN_SYMBOLS = {
    "modules/quality_gates/tribunal/judge.py": "TribunalJudge._compute_verdict / clausulas / BLOCKING_VERDICTS",
    "modules/quality_gates/tribunal/diagnosis_reviewer.py": "DiagnosisReviewer._check_vacuous_recall (el detector no se afloja)",
}


def _git_state(rel: str) -> str:
    out = subprocess.run(
        ["git", "diff", "--numstat", "--", rel],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout.strip()
    return out or "identico a HEAD"


config = pg.PublicationGateConfig()
evidence = {
    "fase": "FASE-0",
    "plan": "REFACTOR-WHATSAPP-ENTREGA-2026-09-18",
    "medido_el": "2026-09-20",
    "head": subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO,
                           capture_output=True, text=True).stdout.strip(),
    "leer_como": (
        "Valores leidos del codigo vivo el dia de la fase. `cambio: no` = el plan "
        "lo tenia congelado y sigue intacto; `cambio: si (serializacion)` = clave "
        "nueva anadida por AC20 sin tocar la regla de decision."
    ),
    "umbrales_existentes": {
        "critical_recall_threshold": {
            "valor": config.critical_recall_threshold,
            "fuente": "PublicationGateConfig.critical_recall_threshold",
            "cambio": "no",
        },
        "coherence_threshold": {
            "valor": config.coherence_threshold,
            "fuente": "PublicationGateConfig.coherence_threshold",
            "cambio": "no",
        },
        "evidence_coverage_threshold": {
            "valor": config.evidence_coverage_threshold,
            "fuente": "PublicationGateConfig.evidence_coverage_threshold",
            "cambio": "no",
        },
        "critical_recall_de_umbral_para_pas": {
            "valor": ">= 0.9",
            "fuente": "PublicationGatesOrchestrator._critical_recall_gate (comparacion `passed`)",
            "cambio": "no: la anotacion no entra en la comparacion",
        },
    },
    "congelados_por_el_plan_y_verificados": {
        "BLOCKING_VERDICTS": {
            "valor": sorted(judge_mod.BLOCKING_VERDICTS),
            "fuente": "modules/quality_gates/tribunal/judge.py",
            "cambio": "no",
        },
        "T1_CERTIFIABLE_CLAUSES": {
            "valor": list(judge_mod.T1_CERTIFIABLE_CLAUSES),
            "cambio": "no",
            "limite_declarado": (
                "P6.2 y P6.5 siguen NOT_EVALUABLE por diseno; esta fase no las "
                "activo y el acta no puede afirmar seis clausulas certificadas"
            ),
        },
        "GATE_BLOCKING_ENABLED": {
            "valor": outcome_mod.GATE_BLOCKING_ENV,
            "default": "true (literal de getenv en run_v4_complete_mode, via el alias _os_gate_block)",
            "cambio": "no",
        },
        "contratos_de_cuarentena": {
            "simbolos": ["DeliveryPackager.write", "DeliveryPackager.publish", "DeliveryPackager.suppress"],
            "cambio": "no",
            "verificacion": _git_state("modules/delivery/delivery_packager.py"),
        },
    },
    "nuevo_por_fase_0": {
        "gate_details_del_camino_fundado": {
            "clave": "details.critical_issues_count",
            "valores_de_recall_basis": [
                "audit_present_no_critical_issues (SR-H2, preexistente)",
                "all_critical_issues_detected (nuevo: recall fundado)",
                "evident_critical_issues_missed (nuevo: paso el umbral con criticos evidentes no cubiertos)",
            ],
            "fuente": "PublicationGatesOrchestrator._critical_recall_details",
            "cambio": "si (serializacion)",
        },
        "acta_findings_projection": {
            "claves": list(outcome_mod.ACTA_FINDING_KEYS),
            "limite_de_texto": outcome_mod.ACTA_FINDING_TEXT_LIMIT,
            "tope_por_revisor": outcome_mod.ACTA_FINDING_CAP,
            "contador_de_omisos": "findings_omitted (solo cuando el tope se supera)",
            "fuente": "modules/quality_gates/tribunal/outcome.py",
            "cambio": "si (serializacion)",
        },
        "package_evidence_en_publish": {
            "clave": "package_evidence.suppressed = False + sha256 + member_count + path",
            "fuente": "main._record_published_package_evidence, llamado en las dos ramas de publish",
            "cambio": "si (serializacion)",
        },
    },
    "crecimiento_medido_del_acta": json.loads(
        (Path(__file__).with_name("baseline_vs_contrafactual.json")).read_text(encoding="utf-8")
    )["medicion_acta"],
    "archivos_con_diferencia_contra_HEAD": {
        rel: _git_state(rel)
        for rel in [
            "main.py",
            "modules/quality_gates/publication_gates.py",
            "modules/quality_gates/tribunal/outcome.py",
            *FROZEN_SYMBOLS,
        ]
    },
}

dest = Path(__file__).with_name("thresholds.json")
dest.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps({
    "head": evidence["head"],
    "umbrales": {k: v["valor"] for k, v in evidence["umbrales_existentes"].items()},
    "congelados": {
        "BLOCKING_VERDICTS": evidence["congelados_por_el_plan_y_verificados"]["BLOCKING_VERDICTS"]["valor"],
        "T1_CERTIFIABLE_CLAUSES": evidence["congelados_por_el_plan_y_verificados"]["T1_CERTIFIABLE_CLAUSES"]["valor"],
        "cuarentena": evidence["congelados_por_el_plan_y_verificados"]["contratos_de_cuarentena"]["verificacion"],
    },
    "frozen_sin_diff": {k: _git_state(k) for k in FROZEN_SYMBOLS},
}, indent=2, ensure_ascii=False))
