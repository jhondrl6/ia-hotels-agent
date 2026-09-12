#!/usr/bin/env python3
"""NR7 (R2.8) del plan PASO0-VERIFICADOR: mutation check **por detección**.

Un verde obtenido sin ningún rojo previo es sospechoso (L-VUP-5), y un verde que prueba
el fixture y no el guard es el defecto de D-T4B-A1. Por eso este runner no escribe un
duplicado del check dentro del test: **revierte la detección real** sobre el archivo
versionado `scripts/validate_lesson_capitalization.py`, corre los tests que esa detección
sostiene, guarda la salida en rojo, restaura, y guarda la salida en verde.

Qué es «revertir» aquí, en la forma estándar del mutation testing:
  - un guard que conduce a una violación se fuerza a `False` (la rama nunca se toma);
  - un guard que conduce al «pasa» se fuerza a `True` (nunca se llega a la violación).

Cada mutación se aplica sobre un ancla de texto que debe aparecer **exactamente una vez**
en el archivo: si el guard se reescribió o desapareció, el runner lo dice en vez de
declarar un rojo que no ocurrió. Las anclas están fijadas al fuente **ya formateado**
(black, línea 100), así que un reformatéo del script las mueve; eso pasó dos veces durante
FASE-V2 y en ambas el runner **se negó** en lugar de simular el mutation check.

Uso:
    python evidence/FASE-V2/run_nr7_capitalizacion.py          # las 13 detecciones
    python evidence/FASE-V2/run_nr7_capitalizacion.py C7a C8   # subconjunto

Salida: 0 = las 13 detecciones mataron sus tests y el archivo quedó intacto.
Evidencia: nr7-<id>-rojo.txt y nr7-<id>-verde.txt en este mismo directorio.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TARGET = ROOT / "scripts" / "validate_lesson_capitalization.py"
TESTS = ROOT / "tests" / "test_validate_lesson_capitalization.py"

# id -> (ancla del guard real, fuerza, tests que sostiene)
MUTACIONES: dict[str, tuple[str, str, list[str]]] = {
    "C1a": (
        '    if not ruta.exists():\n        return [\n            Violacion(\n                "C1",\n                "AUSENTE",',
        '    if False:\n        return [\n            Violacion(\n                "C1",\n                "AUSENTE",',
        ["test_c1_plan_en_alcance_sin_artefacto_declara_ausente_con_su_ruta"],
    ),
    "C1b": (
        '    if texto is None:\n        return [\n            Violacion("C1", "LECTOR-FALLIDO"',
        '    if False:\n        return [\n            Violacion("C1", "LECTOR-FALLIDO"',
        ["test_c1_artefacto_ilegible_es_lector_fallido_y_no_ausente"],
    ),
    "C2": (
        "        if secciones[numero] is None:",
        "        if False:",
        ["test_c2_sin_seccion_tres_no_hay_descartes_que_contar"],
    ),
    "C3a": (
        '        if any(t in fila[capa].lower() for t in CORPUS_WIDE) and "`" in fila[consulta]:',
        "        if True:",
        [
            "test_c3_consultas_que_solo_miran_al_predecesor_no_cuentan",
            "test_c3_consulta_corpus_wide_sin_comando_no_es_reejecutable",
        ],
    ),
    "C4a": (
        "    if not prometidos:",
        "    if False:",
        ["test_c4_fila_de_leccion_sin_efecto_nombrado_es_citar_no_capitalizar"],
    ),
    "C4b": (
        "    if prometidos & acs:",
        "    if True:",
        ["test_c4_un_ac_inventado_no_existe_en_el_maestro"],
    ),
    "C5": (
        "    if len(datos) >= MIN_DESCARTES:",
        "    if True:",
        ["test_c5_dos_descartes_no_prueban_que_se_miro_el_corpus"],
    ),
    "C6a": (
        "    if VERIFICADOR not in seccion:",
        "    if False:",
        ["test_c6_declaracion_que_no_nombra_al_verificador_queda_fosil"],
    ),
    "C6b": (
        "    if not any(f in bajo for f in LIMIT_PHRASES):",
        "    if False:",
        ["test_c6_declaracion_sin_limite_es_un_ok_sin_denominador"],
    ),
    "C7a": (
        "        if not LESSON_ID_RE.match(lid):",
        "        if False:",
        ["test_c7_celda_de_identificacion_que_no_es_un_id_del_corpus"],
    ),
    "C7b": (
        "        if dueno is None:",
        "        if False:",
        ["test_c7_id_inventado_no_esta_definido_en_el_corpus"],
    ),
    "C7c": (
        "        if dueno not in publicada:",
        "        if False:",
        ["test_c7_dueno_real_distinto_al_publicado_es_una_fila_mal_atribuida"],
    ),
    "C8": (
        "    if len(duenos) < MIN_DUENOS:",
        "    if False:",
        [
            "test_c8_todo_de_un_mismo_dueno_no_mira_el_corpus_completo",
            "test_corpus_sin_definiciones_no_produce_un_verde",
        ],
    ),
}


def _pytest(node_ids: list[str]) -> subprocess.CompletedProcess:
    relativa = TESTS.relative_to(ROOT).as_posix()
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            *[f"{relativa}::{n}" for n in node_ids],
            "-q",
            "--no-header",
        ],
        capture_output=True,
        text=True,
        cwd=ROOT,
        encoding="utf-8",
        errors="replace",
    )


def _escribir(bytes_nuevos: bytes) -> None:
    TARGET.write_bytes(bytes_nuevos)


def mutar(identificador: str) -> tuple[bool, str]:
    """Aplica la mutación, corre los tests, restaura. Devuelve (mataron, resumen).

    Todo el ciclo trabaja **en bytes**: reescribir el archivo en modo texto le cambiaría
    los finales de línea en Windows y el control de integridad acusaría falsamente.
    """
    ancla, fuerza, node_ids = MUTACIONES[identificador]
    original = TARGET.read_bytes()
    ancla_b, fuerza_b = ancla.encode("utf-8"), fuerza.encode("utf-8")
    apariciones = original.count(ancla_b)
    if apariciones != 1:
        return False, f"ancla encontrada {apariciones} vez(es) en el archivo versionado"
    try:
        _escribir(original.replace(ancla_b, fuerza_b, 1))
        rojo = _pytest(node_ids)
    finally:
        _escribir(original)
    if TARGET.read_bytes() != original:
        return False, "el archivo no quedó intacto tras restaurar"
    (HERE / f"nr7-{identificador}-rojo.txt").write_text(
        f"# comando: pytest {' '.join(node_ids)} -q\n# guard mutado: {ancla.strip()!r} -> {fuerza.strip()!r}\n"
        f"# exit={rojo.returncode}\n\n{rojo.stdout}\n{rojo.stderr}\n",
        encoding="utf-8",
    )
    verde = _pytest(node_ids)
    (HERE / f"nr7-{identificador}-verde.txt").write_text(
        f"# comando: pytest {' '.join(node_ids)} -q (guard activo, archivo restaurado)\n"
        f"# exit={verde.returncode}\n\n{verde.stdout}\n{verde.stderr}\n",
        encoding="utf-8",
    )
    mataron = rojo.returncode != 0 and verde.returncode == 0
    criterio = re.compile(r"passed|failed|error")
    ultima = next((f for f in rojo.stdout.splitlines() if criterio.search(f)), "").strip()
    resumen = (
        f"rojo={rojo.returncode} verde={verde.returncode} " f"| {len(node_ids)} test(s) | {ultima}"
    )
    return mataron, resumen


def main(argv: list[str]) -> int:
    ids = [a for a in argv if a in MUTACIONES] or list(MUTACIONES)
    hashes = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    fallaron = []
    for identificador in ids:
        mataron, resumen = mutar(identificador)
        print(f"  {'OK ' if mataron else 'NO'} {identificador}: {resumen}")
        if not mataron:
            fallaron.append(identificador)
    if hashlib.sha256(TARGET.read_bytes()).hexdigest() != hashes:
        print("  [!] el archivo mutado NO se restauró: revisar antes de commitear")
        return 2
    if fallaron:
        print(f"[FAIL] NR7 incompleto: {', '.join(fallaron)} no mataron sus tests")
        return 1
    print(
        f"[OK] NR7 (R2.8): {len(ids)} detecciones revertidas sobre el archivo versionado, "
        f"todas con rojo y verde en {HERE.name}/"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
