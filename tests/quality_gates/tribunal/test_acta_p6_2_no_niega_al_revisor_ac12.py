"""AC12: el acta deja de negar al revisor que corrió (L-VERIFY.4).

El texto de P6.2 en `judge.py` decía «Requiere Bot 2 (alignment_reviewer) — no
implementado en T1» mientras el propio acta publicaba el report de Bot 2 en
`reviewer_reports`. La verificación que importa aquí se hace **leyendo un acta generada
por la suite** (JSON y MD del writer real), no buscando el string en el código: L-V.2 y
L-VERIFY.4 existen porque la nota y el artefacto decían cosas distintas del árbol.

`T1_CERTIFIABLE_CLAUSES` NO cambia en esta fase: la decisión de cláusula queda diferida
con dueño (maestro §5, registrada en `10-analisis` §Seguimientos).
"""

import json
from pathlib import Path

from modules.quality_gates.tribunal.acta_writer import ActaWriter
from modules.quality_gates.tribunal.judge import (
    T1_CERTIFIABLE_CLAUSES,
    TribunalJudge,
)


REVISION_ALINEACION = {
    "reviewer": "alignment_reviewer",
    "clause": "P6.2",
    "findings": [],
    "verdict_recommendation": "APROBADO",
    "extraccion": {
        "estado": "OK_SIN_PROMESAS",
        "motivo": "propuesta leída, sin promesas verbales",
        "promesas_leidas": 0,
        "via": "extract_checked",
    },
}


def generar_acta(tmp_path: Path) -> dict:
    """Corre el Juez con Bot 2 habiendo escrito su report, y serializa con el writer real."""
    v4_audit = tmp_path / "v4_audit"
    v4_audit.mkdir(parents=True)
    deliveries = tmp_path / "deliveries"
    deliveries.mkdir(parents=True)

    reporte = v4_audit / "revision_alineacion.json"
    reporte.write_text(json.dumps(REVISION_ALINEACION, ensure_ascii=False), encoding="utf-8")

    judge = TribunalJudge(
        v4_audit_dir=v4_audit, deliveries_dir=deliveries, hotel_id="hotelx"
    )
    acta = judge.evaluate()
    reports = judge.collect_reviewer_reports({"alignment_reviewer": reporte})
    acta = judge.enrich(acta, reports)

    json_path, md_path = ActaWriter(tmp_path / "actas").write(acta)
    return {
        "acta": acta,
        "json": json.loads(json_path.read_text(encoding="utf-8")),
        "md": md_path.read_text(encoding="utf-8"),
        "json_path": json_path,
        "md_path": md_path,
    }


def _bloque_p6_2(acta_json: dict) -> dict:
    return acta_json["clauses"]["P6.2"]


def _report_de_bot2(acta_json: dict) -> dict:
    for report in acta_json["reviewer_reports"]:
        if report["reviewer"] == "alignment_reviewer":
            return report
    raise AssertionError("el acta no publicó el report de Bot 2")


def test_el_acta_generada_no_niega_al_revisor_que_corrio(tmp_path):
    """El hallazgo de P6.2 ya no afirma una ausencia que el mismo acta desmiente."""
    acta = generar_acta(tmp_path)
    hallazgo = _bloque_p6_2(acta["json"])["finding"]

    assert "no implementado" not in hallazgo.lower()
    assert "requiere bot 2" not in hallazgo.lower()
    # Lo que el acta sí puede leer quien la abre:
    assert "revision_alineacion.json" in _bloque_p6_2(acta["json"])["source_artifact"]
    assert _report_de_bot2(acta["json"])["status"] == "OK_NO_FINDINGS"


def test_la_clausula_sigue_no_evaluable_por_decision_de_contrato(tmp_path):
    """AC12 no re-certifica P6.2: sigue NOT_EVALUABLE, y el texto dice por qué."""
    acta = generar_acta(tmp_path)
    bloque = _bloque_p6_2(acta["json"])

    assert bloque["status"] == "NOT_EVALUABLE"
    assert "P6.2" not in T1_CERTIFIABLE_CLAUSES
    assert "decisi" in bloque["finding"] and "contrato" in bloque["finding"]
    # La causa explícita: no es ausencia del revisor.
    assert "no por ausencia" in bloque["finding"]


def test_el_md_del_acta_repite_el_texto_verdadero(tmp_path):
    """La vía MD del acta es la que lee un humano: también dejó de negar al revisor."""
    acta = generar_acta(tmp_path)

    assert "no implementado" not in acta["md"].lower()
    seccion = acta["md"].split("### P6.2")[1].split("### P6.3")[0]
    assert "revision_alineacion.json" in seccion
    assert "NOT_EVALUABLE" in seccion
    assert "implementado" in seccion


def test_el_acta_no_lleva_la_etiqueta_vencida_de_t4_a(tmp_path):
    """Anti-regresión sobre el artefacto: ni el literal que negaba al revisor ni su fuente T4-A."""
    acta = generar_acta(tmp_path)
    bloque = _bloque_p6_2(acta["json"])

    assert bloque["finding"] != "Requiere Bot 2 (alignment_reviewer) — no implementado en T1"
    assert "(T4-A)" not in bloque["source_artifact"]
    assert "(T4-A)" not in acta["md"]
