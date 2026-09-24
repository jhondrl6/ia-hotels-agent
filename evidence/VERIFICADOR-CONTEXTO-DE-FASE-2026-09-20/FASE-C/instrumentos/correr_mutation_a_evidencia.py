"""Instrumento de cierre de FASE-C: corre el arnes de AC14 y vuelca verde y rojo a un destino.

El destino se pasa **por argumento en el cierre**, no como constante dentro del arnes (S13). Este archivo
es el unico lugar donde la ruta de evidencia de FASE-C se nombra, y lo hace con la ruta del propio cierre.

Comando literal de la corrida (publicado en `mutation/resumen.txt`):

    IAH_DECISION_PROVIDER=falso-pertinencia \
    IAH_DECISION_PROVIDERS_DIR=tests/quality_gates/lesson_relevance/falsos_proveedores_triage \
    ./venv/Scripts/python.exe evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/instrumentos/correr_mutation_a_evidencia.py \
      --destino evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/mutation

Cero red: el emisor es el proveedor FALSO determinista de la seleccion; no hay credencial en el entorno
y el instrumentno no abre sockets.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ARNES = ROOT / "tests" / "quality_gates" / "lesson_relevance" / "test_triage_mutation_aditividad.py"
FALOS = ROOT / "tests" / "quality_gates" / "lesson_relevance" / "falsos_proveedores_triage"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--destino", required=True, help="ruta explicita donde van verde y rojo")
    args = ap.parse_args()
    os.environ["IAH_DECISION_PROVIDER"] = "falso-pertinencia"
    os.environ["IAH_DECISION_PROVIDERS_DIR"] = str(FALOS)
    spec = importlib.util.spec_from_file_location("arnes_ac14", ARNES)
    arnes = importlib.util.module_from_spec(spec)
    sys.modules["arnes_ac14"] = arnes
    spec.loader.exec_module(arnes)
    resultado = arnes.correr_a_destino(Path(args.destino))
    v, r = resultado["verde"], resultado["rojo"]
    print(f"VERDE  guard activo   -> removed={v['removed']} cuestionadas={len(v['cuestionadas'])}")
    print(f"ROJO   guard apagado  -> removed={r['removed']}")
    print(f"destino: {resultado['destino']}")
    if not r["removed"]:
        print("[AC14-ROJO-AUSENTE] apagar el guard no filtr6 nada: el mutante no observa la rama real")
        return 1
    if v["removed"]:
        print("[AC14-VERDE-ROTO] con el guard activo tambien desaparecio una fila")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
