"""Instrumento de cierre de FASE-D: reimprime el par `stat` de carga desde `carga.json`.

AC20 exige que la resta sea reproducible con `stat -c %s` sobre rutas publicadas. Este archivo hace
esa impresión y nada más: lee las rutas de `carga.json` → `rutas_stat.before` / `.after` (con su
**multiplicidad por fase**, porque cada sesión abre su propia copia: deduplicarlas daría una lista
que no reproduce la suma medida), corre `stat -c %s` sobre cada una y escribe los dos archivos del
par con su línea `SUMA`.

Por qué es un instrumento versionado y no un comando suelto de esta sesión: el par que produce es
**huevo dependiente** —cambia cada vez que cambia cualquier `.md` del corpus que el generador
copia—, así que FASE-RELEASE va a necesitar re-imprimirlo después del `git mv`. Su destino se
resuelve contra la evidencia de FASE-D y no hardcodea ningún otro archivo (S12/S13).

Uso:

    ./venv/Scripts/python.exe \\
      evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/instrumentos/reimprimir_par_carga.py \\
      --evidencia evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def _lado(ev: Path, carga: dict, lado: str, archivo: str, nombre: str, stamp: str) -> int:
    lineas = [f"# PAR {nombre} (carga de lectura) — FASE-D, medido {stamp}",
              "# comando: stat -c %s <ruta>, una linea por fase-lectura; sin deduplicar "
              "(cada sesion abre su copia)",
              "# rutas: las publica carga.json en rutas_stat." + lado]
    total = 0
    for ruta in carga["rutas_stat"][lado]:
        r = subprocess.run(["stat", "-c", "%s", ruta], capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit(f"[2] stat fallo en {ruta}: {r.stderr.strip()}")
        bytes_ = int(r.stdout.strip())
        total += bytes_
        lineas.append(f"{bytes_} {ruta}")
    lineas.append(f"SUMA {total}")
    (ev / archivo).write_text("\n".join(lineas) + "\n", encoding="utf-8", newline="\n")
    print(f"{lado}: SUMA {total} sobre {len(carga['rutas_stat'][lado])} rutas -> {archivo}")
    return total


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidencia", required=True, type=Path)
    args = ap.parse_args()
    raiz = Path(__file__).resolve().parents[4]
    ev = args.evidencia if args.evidencia.is_absolute() else raiz / args.evidencia
    carga = json.loads((ev / "carga.json").read_text(encoding="utf-8"))
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    pre = _lado(ev, carga, "before", "faseD_carga_pre.txt", "PRE", stamp)
    post = _lado(ev, carga, "after", "faseD_carga_post.txt", "POST", stamp)
    coste = sum(f["after"]["coste_de_generacion"] for f in carga["por_fase"])
    t = carga["total"]
    print(f"esperado: before={t['before']['total']} after={t['after']['total']} (stat + coste {coste})")
    if pre != t["before"]["total"] or post + coste != t["after"]["total"]:
        print("[DESCUADRE] el par impreso no reproduce el JSON: volver a generar los packs antes")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
