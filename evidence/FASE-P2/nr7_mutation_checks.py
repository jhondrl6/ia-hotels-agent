"""NR7 mutation checks - FASE-P2 (AC-E0, AC-E1, AC-E2, AC-E3, AC-E4, AC-E5).

Por cada AC se desactiva la garantia y se comprueba que el test dirigido se pone
ROJO. Un test que no puede fallar no certifica el AC (NR7, de L-T4A.5/L-T2C.4 /
L-VUP-5: una fase sin un solo rojo real es un falso verde).

Ocho mutaciones:
  AC-E0-a  colapsar dos estados de revisor (ARTIFACT_MISSING → READER_FAILED)
  AC-E0-b  devolver el guard `if reviewer_reports:` al writer (sección que se omite)
  AC-E1    el acta deja de poblarse desde el DTO (vuelve al [] literal)
  AC-E2    `_compute_verdict` deja de consumir `reviewer_reports` (la del contrato)
  AC-E3    el lector del informe relanza en vez de registrar READER_FAILED
  AC-E4    el bloqueo ignora `GATE_BLOCKING_ENABLED` (siempre bloquea)
  AC-E5-a  `suppress()` renombra en lugar de borrar
  AC-E5-b  `corrective_actions` se vacía con veredicto bloqueante

Ejecuta:  python evidence/FASE-P2/nr7_mutation_checks.py
Escribe:  evidence/FASE-P2/NR7-<ac>.txt   (par verde/rojo por mutacion)

Cada archivo mutado se restaura desde su contenido original en memoria y se
verifica el arbol al terminar.
"""

import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = Path(__file__).resolve().parent

JUDGE = ROOT / "modules" / "quality_gates" / "tribunal" / "judge.py"
OUTCOME = ROOT / "modules" / "quality_gates" / "tribunal" / "outcome.py"
ACTA = ROOT / "modules" / "quality_gates" / "tribunal" / "acta_writer.py"
PACKAGER = ROOT / "modules" / "delivery" / "delivery_packager.py"

V2 = "tests/quality_gates/tribunal/test_p2_veredicto_enriquecido.py"
Q2 = "tests/delivery/test_p2_cuarentena_zip.py"


MUTATIONS = [
    {
        "ac": "AC-E0-a",
        "desc": "Colapsar dos estados: un artefacto ausente se reporta como lector fallido",
        "archivo": OUTCOME,
        "viejo": """        if not path.exists():
            reports.append(ReviewerReport(reviewer=spec.reviewer, status=ReviewerStatus.ARTIFACT_MISSING, clauses=spec.clauses))
            continue""",
        "nuevo": """        if not path.exists():  # MUTACION NR7: colapso de estados
            reports.append(ReviewerReport(reviewer=spec.reviewer, status=ReviewerStatus.READER_FAILED, clauses=spec.clauses))
            continue""",
        "tests": [f"{V2}::test_los_tres_estados_no_colapsan",
                  f"{V2}::test_artefacto_ausente"],
    },
    {
        "ac": "AC-E0-b",
        "desc": "Devolver al writer el guard que omite la seccion cuando la lista viene vacia",
        "archivo": ACTA,
        "viejo": """        lines.extend(self._render_reviewer_reports(acta.get("reviewer_reports") or []))""",
        "nuevo": """        if acta.get("reviewer_reports"):  # MUTACION NR7: el guard de antes
            lines.extend(self._render_reviewer_reports(acta.get("reviewer_reports") or []))""",
        "tests": [f"{V2}::test_la_seccion_de_revisores_nunca_se_omite"],
    },
    {
        "ac": "AC-E1",
        "desc": "El acta deja de poblarse desde el DTO (vuelve el literal [] de pre-P2)",
        "archivo": JUDGE,
        "viejo": """        acta["reviewer_reports"] = [r.to_dict() for r in reports]""",
        "nuevo": """        acta["reviewer_reports"] = []  # MUTACION NR7: sin poblado desde el DTO""",
        "tests": [f"{V2}::test_reviewer_reports_refleja_los_cuatro_revisores",
                  f"{V2}::test_los_4_revisores_no_hallan_nada"],
    },
    {
        "ac": "AC-E2",
        "desc": "_compute_verdict deja de consumir reviewer_reports (la mutacion del contrato)",
        "archivo": JUDGE,
        "viejo": """        if any(r.verified_critical or r.verified_block for r in reviewer_reports):
            return VERDICT_BLOCKED""",
        "nuevo": """        # MUTACION NR7: fila 2 de la matriz eliminada — el ZIP se decide sin revisores""",
        "tests": [f"{V2}::test_bloquear_de_un_revisor_bloquea_la_entrega",
                  f"{V2}::test_critical_verificado_por_un_revisor_bloquea",
                  f"{V2}::test_el_orden_de_la_matriz_es_parte_del_contrato",
                  f"{Q2}::test_veredicto_bloqueante_del_tribunal_suprime_el_zip_real"],
    },
    {
        "ac": "AC-E3",
        "desc": "El lector del informe relanza en vez de registrar READER_FAILED (nunca-block roto)",
        "archivo": OUTCOME,
        "viejo": """    try:
        import json

        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError):
        return None""",
        "nuevo": """    import json  # MUTACION NR7: sin captura, el fallo aborta la corrida

    return json.loads(path.read_text(encoding="utf-8"))""",
        "tests": [f"{V2}::test_lector_fallido",
                  f"{V2}::test_revisor_que_revienta_no_rompe_la_corrida"],
    },
    {
        "ac": "AC-E4",
        "desc": "El bloqueo ignora GATE_BLOCKING_ENABLED: apagar el knob ya no salva la corrida",
        "archivo": OUTCOME,
        "viejo": """        blocks_publish=bool(blocks) and enabled,""",
        "nuevo": """        blocks_publish=bool(blocks),  # MUTACION NR7: knob ignorado""",
        "tests": [f"{V2}::test_el_knob_apagado_no_bloquea_pero_lo_declara"],
    },
    {
        "ac": "AC-E5-a",
        "desc": "suppress() renombra en lugar de borrar: el ZIP queda publicado igual",
        "archivo": PACKAGER,
        "viejo": """        tmp = Path(tmp_zip_path)
        if not tmp.exists():
            return
        try:
            tmp.unlink()""",
        "nuevo": """        tmp = Path(tmp_zip_path)  # MUTACION NR7: suprimir pasa a publicar
        if not tmp.exists():
            return
        try:
            published_path_for(tmp).write_bytes(tmp.read_bytes())
            tmp.unlink()""",
        "tests": [f"{Q2}::test_suprimir_la_cuarentena_no_deja_ningun_zip",
                  f"{Q2}::test_veredicto_bloqueante_del_tribunal_suprime_el_zip_real"],
    },
    {
        "ac": "AC-E5-b",
        "desc": "corrective_actions se vacia con veredicto bloqueante (bloqueo sin reparacion)",
        "archivo": OUTCOME,
        "viejo": """    actions: list = []
    for report in reports:""",
        "nuevo": """    actions: list = []
    if blocking:  # MUTACION NR7: veredicto bloqueante sin acciones correctivas
        return actions
    for report in reports:""",
        "tests": [f"{V2}::test_veredicto_bloqueante_deja_acciones_correctivas_con_dueno",
                  f"{V2}::test_bloqueo_por_gate_sin_hallazgo_de_revisor_tambien_tiene_dueno",
                  f"{Q2}::test_veredicto_bloqueante_del_tribunal_suprime_el_zip_real"],
    },
]


def run(tests):
    cmd = [sys.executable, "-m", "pytest", *tests,
           "-v", "--tb=line", "-p", "no:cacheprovider"]
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                          encoding="utf-8", errors="replace",
                          env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    return proc.returncode, proc.stdout + proc.stderr


def main():
    targets = {m["archivo"] for m in MUTATIONS}
    originals = {p: p.read_text(encoding="utf-8") for p in targets}
    failures = []

    for m in MUTATIONS:
        path = m["archivo"]
        if m["viejo"] not in originals[path]:
            print(f"!! {m['ac']}: el texto a mutar no esta en {path.name} — abortando")
            failures.append(m["ac"])
            continue

        rc_green, out_green = run(m["tests"])

        try:
            path.write_text(
                originals[path].replace(m["viejo"], m["nuevo"], 1), encoding="utf-8"
            )
            rc_red, out_red = run(m["tests"])
        finally:
            path.write_text(originals[path], encoding="utf-8")

        mutated_failed = rc_red != 0
        report = (
            f"# NR7 mutation check — {m['ac']}\n"
            f"# Mutacion: {m['desc']}\n"
            f"# Archivo: {path.relative_to(ROOT).as_posix()}\n"
            f"# Tests dirigidos: {len(m['tests'])}\n"
            f"#\n"
            f"# VERDE (sin mutar): rc={rc_green} — esperado 0\n"
            f"# ROJO (mutado):     rc={rc_red} — esperado != 0 → "
            f"{'OK, el test puede fallar' if mutated_failed else 'FALLO: el test NO falla, no certifica el AC'}\n"
            f"\n{'='*70}\n=== SALIDA VERDE (rc={rc_green}) ===\n{'='*70}\n"
            f"{out_green}\n"
            f"\n{'='*70}\n=== SALIDA ROJA — MUTADO (rc={rc_red}) ===\n{'='*70}\n"
            f"{out_red}\n"
        )
        out_file = EVIDENCE / f"NR7-{m['ac']}.txt"
        out_file.write_text(report, encoding="utf-8")

        status = "OK" if (rc_green == 0 and mutated_failed) else "FALLO"
        print(f"[{status}] {m['ac']}: verde rc={rc_green}, rojo rc={rc_red} -> {out_file.name}")
        if status == "FALLO":
            failures.append(m["ac"])

    for p, orig in originals.items():
        assert p.read_text(encoding="utf-8") == orig, f"{p.name} no se restauró"
    print("\nArbol restaurado: judge.py, outcome.py, acta_writer.py y delivery_packager.py "
          "identicos al original.")

    if failures:
        print(f"\nNR7 NO cumplido en: {failures}")
        sys.exit(1)
    print(f"\nNR7 cumplido en los {len(MUTATIONS)} pares "
          f"(AC-E0 a/b, AC-E1, AC-E2, AC-E3, AC-E4, AC-E5 a/b).")


if __name__ == "__main__":
    main()
