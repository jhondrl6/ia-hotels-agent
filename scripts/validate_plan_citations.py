#!/usr/bin/env python3
"""Verificador de citas de linea en los planes de `.opencode/plans/` (FASE-HOTFIX H9).

Materializa como mecanico lo que la regla R2.2 del executor (`phased_project_executor.md`
v2.19.0) dice en prosa: **en criterios de aceptacion, prompts de fase y evidencia se
cita simbolo, nunca `archivo:123`**.

POR QUE EXISTE (medido, no supuesto)
    FASE-VERIFY audito las citas de linea que usaban los criterios de aceptacion del
    plan `ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` y encontro **14 de 16 desfasadas**
    (desplazamientos entre -88 y +104 lineas; S-V6/L-V4). FASE-A habia hallado ya 4
    citas **falsas** en el propio plan, una repetida 12 veces en 6 archivos. La causa
    es estructural: un plan multi-fase cita posiciones en archivos que **las mismas
    fases reescriben**, asi que la cita caduca durante la ejecucion del plan.
    Escribir la regla y no medirla es exactamente el mecanismo que acabo en S15.

POBLACION MEDIDA (2026-09-04) — re-medible con:
    grep -rEoh "[A-Za-z0-9_/]+\\.py:[0-9]+" .opencode/plans --include=*.md | wc -l
    (723 en todo `.opencode/plans`; 381 en ESTABILIZACION-PRE-TRIBUNAL-2026-09-03;
     179 de ellas dentro de secciones de AC/tareas/fases = 24 %)

ALCANCE ELEGIDO: **(1) hacia delante + (2) delta**, no (3) por seccion.
    (1) Un plan NUEVO (ausente del baseline) no introduce ninguna cita numerica.
    (2) El inventario de los planes EXISTENTES no puede CRECER: documentar una
        medicion nueva en un documento historico esta permitido solo si se actualiza
        el baseline explicitamente (`--update-baseline`), que es un acto visible.
    (3) se descarto por medida: el 76 % de las citas vive en prosa historica que
        registra lo que ocurrio; borrarla o reescribirla seria **falsificar el
        registro**, y limitarse a las secciones de AC habria dejado fuera 559 citas.

PROHIBIDO AUTO-ARREGLAR. `validate_opencode_refs.py` puede reparar porque un basename
    es unico y converge a la verdad; una linea de codigo no tiene a que converger, y
    reescribirla produciria una cita que apunta a un sitio que ya no contiene lo citado
    (el defecto de S15 con apariencia de arreglado). Este script **reporta**.

Uso:
    python scripts/validate_plan_citations.py                  # verificar
    python scripts/validate_plan_citations.py --update-baseline # re-fijar inventario
    python scripts/validate_plan_citations.py --plans-dir D --baseline F  # (tests)

Salida: 0 = sin violaciones; 1 = violaciones; 2 = error de uso/estado.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PLANS = ROOT / ".opencode" / "plans"
DEFAULT_BASELINE = ROOT / ".opencode" / "plans" / "plan_citations_baseline.json"

# `archivo.ext:123` y `archivo.ext:123-456`; tambien `L123` pegado a un archivo.
CITATION_RE = re.compile(
    r"[A-Za-z0-9_\-./\\]+\.(?:py|md|yaml|yml|json|txt|html|csv|lock|toml|ini|sh|bat):"
    r"\d+(?:\s*[-\u2013]\s*\d+)?"
)

SCHEMA_VERSION = "1.0"


def contar_citas(md_files, base: Path) -> dict:
    """`{ruta_relativa_a_base: numero_de_citas}` (solo los archivos con > 0).

    Las claves son **relativas al directorio de planes**: un baseline con rutas
    absolutas convertiria cada archivo en «nuevo» al clonar el repo en otra ruta,
    que es justo el defecto de las metricas que no sobreviven al clone.
    """
    conteo = {}
    for md in sorted(md_files):
        try:
            texto = md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        n = len(CITATION_RE.findall(texto))
        if n:
            conteo[Path(md).resolve().relative_to(Path(base).resolve()).as_posix()] = n
    return conteo


def cargar_baseline(path: Path) -> dict:
    if not path.exists():
        return {"schema_version": SCHEMA_VERSION, "created_at": None, "files": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"[2] baseline ilegible en {path}: {exc}")
    data.setdefault("files", {})
    return data


def verificar(plans_dir: Path, baseline: dict) -> list:
    """Violaciones: planes nuevos con citas, o archivos con MAS citas que su baseline."""
    archivos = contar_citas(plans_dir.rglob("*.md"), plans_dir)
    conocidos = set(baseline["files"])
    violaciones = []

    # (1) hacia delante: un archivo que no esta en el inventario no introduce citas.
    for ruta, n in sorted(archivos.items()):
        if ruta not in conocidos:
            violaciones.append(
                f"NUEVO con citas numericas ({n}): {ruta} "
                "|| Citar simbolos (`def classify_promised_services`, "
                "`BLOCKING_GATE_NAMES`), no lineas (R2.2 del executor)."
            )

    # (2) delta: el inventario historico no crece sin acto visible.
    for ruta, n in sorted(archivos.items()):
        anterior = baseline["files"].get(ruta)
        if anterior is not None and n > anterior:
            violaciones.append(
                f"CRECIO {anterior} -> {n}: {ruta} "
                "|| Lo historico se conserva, no se amplía con citas nuevas. "
                "Si la medicion nueva es legítima, fijarla con --update-baseline "
                "(acto visible en el diff)."
            )
    return violaciones


def escribir_baseline(path: Path, plans_dir: Path) -> dict:
    datos = {
        "schema_version": SCHEMA_VERSION,
        "plans_dir": plans_dir.name,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "comando_de_medicion": (
            'grep -rEoh "[A-Za-z0-9_/]+\\\\.py:[0-9]+" .opencode/plans --include=*.md | wc -l'
        ),
        "files": contar_citas(plans_dir.rglob("*.md"), plans_dir),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(datos, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return datos


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--plans-dir", default=str(DEFAULT_PLANS))
    ap.add_argument("--baseline", default=str(DEFAULT_BASELINE))
    ap.add_argument("--update-baseline", action="store_true",
                    help="re-fijar el inventario (acto visible; lo hace quien documenta)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    plans_dir = Path(args.plans_dir)
    baseline_path = Path(args.baseline)
    if not plans_dir.is_dir():
        print(f"[2] no existe el directorio de planes: {plans_dir}")
        return 2

    if args.update_baseline:
        datos = escribir_baseline(baseline_path, plans_dir)
        print(f"Baseline fijado: {len(datos['files'])} archivos, "
              f"{sum(datos['files'].values())} citas en {plans_dir}")
        return 0

    baseline = cargar_baseline(baseline_path)
    if not baseline["files"]:
        print("[2] baseline vaco o ausente: "
              f"{baseline_path}\n    Fijarlo con --update-baseline antes de exigir nada.")
        return 2

    violaciones = verificar(plans_dir, baseline)
    total = sum(contar_citas(plans_dir.rglob("*.md"), plans_dir).values())

    if violaciones:
        if not args.quiet:
            print(f"[FAIL] Plan citations: {len(violaciones)} violacion(es) "
                  f"(inventario actual: {total} citas)")
        for v in violaciones:
            print(f"  - {v}")
        return 1

    if not args.quiet:
        print(f"[OK] Plan citations: {total} citas historicas, 0 nuevas y 0 crecimientos "
              f"({len(baseline['files'])} archivos en el inventario)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
