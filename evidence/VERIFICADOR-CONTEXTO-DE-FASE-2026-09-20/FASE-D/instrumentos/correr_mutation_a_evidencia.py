"""Instrumento de cierre de FASE-D: corre el arnes de AC23 y vuelca verde y rojo a un destino.

El destino se pasa **por argumento en el cierre**, no como constante dentro del arnes (S13, la
lección de FASE-A/FASE-C: un destino hardcodeado re-escribe evidencia cerrada de otra fase). Este
archivo es el unico lugar donde la ruta de evidencia de FASE-D se nombra, y lo hace con la ruta del
propio cierre.

Comando literal de la corrida (publicado en `mutation/resumen.txt`):

    ./venv/Scripts/python.exe \\
      evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/instrumentos/correr_mutation_a_evidencia.py \\
      --destino evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/mutation

Cero red y cero proveedor: FASE-D es determinista; el arnes solo genera packs sobre un directorio
temporal y apaga un simbolo del generador.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ARNES = ROOT / "tests" / "quality_gates" / "phase_briefing" / "test_briefing_mutation_no_truncar.py"
SALIDAS_ESPERADAS = ("verde_baseline.json", "mutante_M-AC23-guard-no-truncamiento.json",
                     "resumen.txt")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--destino", required=True, help="ruta explicita donde van verde y rojo")
    args = ap.parse_args()
    spec = importlib.util.spec_from_file_location("arnes_ac23", ARNES)
    arnes = importlib.util.module_from_spec(spec)
    sys.modules["arnes_ac23"] = arnes
    spec.loader.exec_module(arnes)
    resultado = arnes.correr_a_destino(Path(args.destino))
    v, r = resultado["verde"], resultado["rojo"]
    print(f"VERDE  guard activo   -> declara_recorte={v['declara_recorte']} bytes={v['bytes_pack']}")
    print(f"ROJO   guard apagado  -> declara_recorte={r['declara_recorte']} bytes={r['bytes_pack']}")
    print(f"destino: {resultado['destino']}")
    escritas = sorted(p.name for p in Path(args.destino).iterdir() if p.is_file())
    if not set(SALIDAS_ESPERADAS) <= set(escritas):
        print(f"[AC23-SALIDAS-INCOMPLETAS] {escritas}")
        return 2
    if r["declara_recorte"]:
        print("[AC23-ROJO-AUSENTE] apagar el guard no quito la declaracion: el mutante no "
              "observa la rama real (L-T4A.5)")
        return 1
    if not v["declara_recorte"]:
        print("[AC23-VERDE-ROTO] con el guard activo tampoco se declaro el recorte")
        return 2
    if not r["bytes_pack"] < v["bytes_pack"]:
        print("[AC23-SIN-TRUNCAMIENTO] el mutante no achico el pack: no prueba truncamiento")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
