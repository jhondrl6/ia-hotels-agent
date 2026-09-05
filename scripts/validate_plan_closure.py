#!/usr/bin/env python3
"""Verificador de cierre de planes en `.opencode/plans/` (regla R2.5, 2026-09-05).

POR QUÉ EXISTE (medido, no supuesto)
    El plan ESTABILIZACION-PRE-TRIBUNAL-2026-09-03 se cerró el 2026-09-04 con
    v4.75.0 y su §1 siguió publicando «FASE-RELEASE ⬜ Pendiente» — la tabla
    resumen contradecía a su propio §10 (Cierre del plan COMPLETADO). Lo detectó
    una sesión posterior a mano (reproceso); este check lo vuelve mecánico en el
    pre-commit hook (check 5/5).

QUÉ VERIFICA
    Para cada plan VIVO (directorio de primer nivel de `.opencode/plans/`, fuera
    de `Archives/`): si `10-analisis-post-implementacion.md` declara cierre
    (sección «Cierre del plan» que afirme COMPLETADO), entonces el archivo no
    puede contener filas «⬜ Pendiente» en su Resumen de Ejecución (§1).

ALCANCE
    Solo planes vivos. Los de `Archives/` son histórico congelado que no se
    reescribe (misma regla del verificador de citas).

PROHIBIDO AUTO-ARREGLAR: la corrección es una decisión de redacción (actualizar
    la fila con nota datada o retirar la declaración de cierre); el script
    reporta, no reescribe.

Uso:
    python scripts/validate_plan_closure.py                     # verificar
    python scripts/validate_plan_closure.py --plans-dir D       # (tests)

Salida: 0 = sin violaciones; 1 = violaciones; 2 = error de estado.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PLANS = ROOT / ".opencode" / "plans"
ANALISIS = "10-analisis-post-implementacion.md"

CLOSURE_HEADING = re.compile(r"^#{1,3}\s.*Cierre del plan", re.MULTILINE)
DECLARA_COMPLETADO = re.compile(r"COMPLETADO")
PENDING_ROW = re.compile(r"^[^\S\n]*\|[^\n]*⬜[^\n]*", re.MULTILINE)


def verificar(plans_dir: Path) -> list:
    """Violaciones: planes vivos que declaran cierre y publican «⬜ Pendiente»."""
    violaciones = []
    if not plans_dir.is_dir():
        return violaciones
    for plan in sorted(p for p in plans_dir.iterdir() if p.is_dir()):
        if plan.name == "Archives":
            continue  # histórico congelado, fuera de alcance
        doc = plan / ANALISIS
        if not doc.exists():
            continue  # plan sin análisis post-implementación: nada que vigilar
        try:
            texto = doc.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if not (CLOSURE_HEADING.search(texto) and DECLARA_COMPLETADO.search(texto)):
            continue  # plan vivo o sin declaración de cierre: las ⬜ son legítimas
        for match in PENDING_ROW.finditer(texto):
            linea = texto.count("\n", 0, match.start()) + 1
            violaciones.append(
                f"{plan.relative_to(plans_dir).as_posix()}/{ANALISIS}:{linea} — "
                "el plan declara cierre pero su Resumen publica «⬜ Pendiente» "
                "(la tabla contradice a su propio §10)."
            )
    return violaciones


def main() -> int:
    parser = argparse.ArgumentParser(description="Verificador de cierre de planes")
    parser.add_argument("--plans-dir", type=Path, default=DEFAULT_PLANS)
    args = parser.parse_args()
    if not args.plans_dir.is_dir():
        print(f"[2] el directorio de planes no existe: {args.plans_dir}")
        return 2
    violaciones = verificar(args.plans_dir)
    if violaciones:
        print(f"[FAIL] Cierre de planes: {len(violaciones)} violacion(es):")
        for v in violaciones:
            print(f"  - {v}")
        print("Un plan COMPLETADO no publica filas «⬜ Pendiente» (regla R2.5).")
        print("Corrige la fila con nota datada (convención del archivo) y re-commitea.")
        return 1
    print("[OK] Cierre de planes: ningún plan vivo declara cierre con filas pendientes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
