"""FASE-P4 / L-VUP-14 — diff **estructural** entre la corrida de observación y el
baseline del predecesor (`evidence/FASE-E2E/`), por claves numeradas.

Re-ejecutable:
    python evidence/FASE-P4/diff_estructural_corridas.py --selftest   # antes de la corrida
    python evidence/FASE-P4/diff_estructural_corridas.py --run <dir>  # despues de la corrida

Tres decisiones de diseño, cada una contra una lección del plan:

1. **Se comparan claves y formas, nunca valores, en el artefacto versionado.** El remoto
   es público y el baseline es material de cliente real; las cifras COP quedan solo en el
   detalle local (`corrida/detalle-valores.md`, ruta gitignoreada).
2. **El selftest es obligatorio antes de interpretar nada** (L-VUP-14): un parseo que no se
   probó contra el baseline convierte ruido en delta. El selftest exige además un conteo de
   claves > 0 por artefacto y una **mutación plantada** que debe detectarse — un comparator
   que no puede fallar no certifica nada (NR7, L-T4A.5).
3. **El baseline se lee desde el snapshot con hashes**, no desde la carpeta viva que otro
   plan puede reescribir (L-B4 / AC-O2).
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "evidence" / "FASE-E2E"
DETAIL = Path(__file__).resolve().parent / "corrida" / "detalle-valores.md"

# Stems canonicos del pipeline; se resuelven por prefijo porque van con timestamp.
ARTIFACT_STEMS = [
    "financial_scenarios",
    "gate_report",
    "audit_report",
    "acta_revision",
    "coherence_validation",
    "coherence_validation_post_gen",
    "pain_ledger",
    "pain_ledger_resolved",
    "asset_generation_report",
    "commercial_gates_report",
    "delivery_quality_report",
    "geo_flow_result",
    "ia_readiness_report",
    "proposal_asset_matrix",
    "revision_alineacion",
    "v4_complete_report",
]


def flatten(obj, prefix: str = "") -> dict:
    """Diccionario plano `clave.numerada -> valor` (listas con indice)."""
    out: dict = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else str(k)
            out.update(flatten(v, path))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(flatten(v, f"{prefix}[{i}]"))
    else:
        out[prefix or "<root>"] = obj
    return out


def shape(value) -> str:
    if isinstance(value, bool):
        return f"bool={value}"
    if isinstance(value, (int, float)):
        return type(value).__name__          # sin divulgar la cifra
    if isinstance(value, str):
        return f"str({len(value)})"
    if value is None:
        return "null"
    return type(value).__name__


def discover(run_dir: Path) -> dict:
    """`stem -> path` del artefacto JSON mas reciente de cada stem en el arbol del run.

    Matcheado con patron anclado y stems de mayor a menor longitud: con `startswith` el
    stem corto se queda el archivo del varianto (`coherence_validation` se comia a
    `coherence_validation_post_gen`) y el diff compara un archivo consigo mismo dando
    verde falso.
    """
    import re

    patterns = {
        stem: re.compile(rf"^{re.escape(stem)}(_[a-z]+)*(_\d{{8}}_\d{{6}})?\.json$")
        for stem in ARTIFACT_STEMS
    }
    ordered = sorted(patterns, key=len, reverse=True)
    candidates: dict[str, list[Path]] = {stem: [] for stem in patterns}
    claimed: set[Path] = set()
    for path in sorted(run_dir.rglob("*.json")):
        for stem in ordered:
            if path in claimed:
                break
            if patterns[stem].match(path.name):
                candidates[stem].append(path)
                claimed.add(path)
                break
    return {stem: max(paths, key=lambda p: p.stat().st_mtime)
            for stem, paths in candidates.items() if paths}


def load_flat(run_dir: Path) -> dict:
    return {stem: flatten(json.loads(p.read_text(encoding="utf-8")))
            for stem, p in sorted(discover(run_dir).items())}


def diff_artifact(before: dict, after: dict) -> tuple[list, list]:
    """(filas estructurales, filas de valor) — la segunda va solo al detalle local."""
    rows, value_rows = [], []
    for key in sorted(set(before) | set(after)):
        if key not in before:
            rows.append((key, "—", shape(after[key]), "ALTA"))
        elif key not in after:
            rows.append((key, shape(before[key]), "—", "BAJA"))
        elif before[key] != after[key]:
            rows.append((key, shape(before[key]), shape(after[key]), "CAMBIO_FORMA"))
            value_rows.append((key, before[key], after[key]))
        else:
            rows.append((key, shape(before[key]), shape(after[key]), "igual"))
    return rows, value_rows


def selftest() -> int:
    """Prueba el parseo contra el baseline ANTES de existir la corrida nueva."""
    if not BASELINE.exists():
        print(f"!! baseline no encontrado: {BASELINE}  (esta en .gitignore: solo existe en esta maquina)")
        return 2
    left = load_flat(BASELINE)
    right = load_flat(BASELINE)
    print(f"artefactos parseados: {len(left)}")
    failures = []

    paths = discover(BASELINE)
    seen: dict[Path, str] = {}
    for stem, path in sorted(paths.items()):
        if path in seen:
            failures.append(f"colisión de stem: `{seen[path]}` y `{stem}` resuelven a {path.name}")
        seen[path] = stem
    for stem, flat in sorted(left.items()):
        n = len(flat)
        print(f"  {stem:<36} claves={n}")
        if n == 0:
            failures.append(f"{stem}: parseo devuelve 0 claves (comparator vacuo)")
    if not left:
        failures.append("no se descubrio ningun artefacto del pipeline")

    # (a) identidad: mismo input -> cero diferencias estructurales
    for stem in left:
        rows, vals = diff_artifact(left[stem], right[stem])
        if any(r[3] != "igual" for r in rows) or vals:
            failures.append(f"{stem}: el diff no es cero sobre input identico")

    # (b) mutacion plantada: el comparator DEBE ver un cambio de valor y un alta de clave
    mutated = copy.deepcopy(left["financial_scenarios"])
    victim = next(k for k, v in mutated.items() if isinstance(v, (int, float)) and not isinstance(v, bool))
    mutated[victim] = mutated[victim] + 1
    mutated["__mutación_plantada__"] = 1
    rows, vals = diff_artifact(left["financial_scenarios"], mutated)
    if not any(r[0] == "__mutación_plantada__" and r[3] == "ALTA" for r in rows):
        failures.append("no detecta una clave nueva")
    if not any(k == victim for k, _a, _b in vals):
        failures.append("no detecta un cambio de valor escalar")

    print(f"\nmutacion plantada en `{victim}` -> filas CAMBIO/ALTA detectadas: "
          f"{sum(1 for r in rows if r[3] != 'igual')}")
    if failures:
        for f in failures:
            print(f"  [FALLO] {f}")
        return 1
    print("[OK] selftest: parseo no vacuo, diff cero con input identico, mutacion detectada")
    return 0


def run_diff(run_dir: Path) -> int:
    if not run_dir.exists():
        print(f"!! no existe la corrida: {run_dir}")
        return 2
    before = load_flat(BASELINE)
    after = load_flat(run_dir)
    missing = sorted(set(before) - set(after))
    lines = [
        "# Detalle de valores — FASE-P4 (local, NO versionado: material de cliente)",
        "",
        f"baseline: `{BASELINE.relative_to(ROOT)}`  |  corrida: `{run_dir.relative_to(ROOT)}`",
        "",
    ]
    if missing:
        lines.append(f"⚠️ artefactos del baseline sin par en la corrida: {missing}")
        lines.append("")
    total_value_rows = 0
    for stem in sorted(set(before) & set(after)):
        rows, value_rows = diff_artifact(before[stem], after[stem])
        total_value_rows += len(value_rows)
        lines.append(f"## {stem}")
        lines.append(f"- claves: baseline={len(before[stem])} corrida={len(after[stem])} "
                     f"cambios de valor={len(value_rows)}")
        for key, b, a in value_rows:
            lines.append(f"  - `{key}`: {b!r} → {a!r}")
        lines.append("")
    DETAIL.parent.mkdir(parents=True, exist_ok=True)
    DETAIL.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] diff estructural sobre {len(set(before) & set(after))} artefactos, "
          f"{total_value_rows} cambios de valor -> {DETAIL.relative_to(ROOT)}")
    for stem in sorted(set(before) & set(after)):
        rows, _ = diff_artifact(before[stem], after[stem])
        estructura = {r[3] for r in rows} - {"igual"}
        print(f"  {stem:<36} alta/baja/cambio_forma = {sorted(estructura) or 'ninguno'}")
    if missing:
        print(f"  sin par: {missing}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true", help="probar el parseo contra el baseline")
    parser.add_argument("--run", type=Path, help="directorio de la corrida nueva a comparar")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    if args.run:
        return run_diff(args.run if args.run.is_absolute() else ROOT / args.run)
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
