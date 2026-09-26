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


# ⟦ Anotacion de vigencia del reproductor, anadida el 2026-09-26 al pie del archivo. No reescribe
# la corrida del 2026-09-24 ni toca su expediente: es una nota sobre lo que este script ya no
# puede reproducir.
#
# La linea 39 (`resultado = arnes.correr_a_destino(Path(args.destino))`) **no reproduce sobre el
# codigo actual**. Medido sin ejecutar el arnes y sin escribir en ninguna ruta: la firma vigente en
# `tests/quality_gates/phase_briefing/test_briefing_mutation_no_truncar.py:93` es
# `correr_a_destino(destino: Path, caso: dict, bpb=None)`, y enlazarla con el unico argumento que
# pasa esta linea devuelve `TypeError: missing a required argument: 'caso'`.
#
# No es solo el arity. `FASE-D/mutation/resumen.txt` documenta la corrida con el pack **real** de
# FASE-RELEASE del plan (279.306 B el verde / 278.773 B el rojo); el arnes de hoy **planta** su
# insumo y emite una fase `X` bajo un arbol temporal, asi que una corrida corregida de este script
# tampoco volveria a producir ese crudo. `FASE-D/mutation/` queda como evidencia de la corrida
# cerrada: no se re-mide ni se re-escribe (S12/S13, y mandato expreso de esta sesion).
#
# Forma correcta hoy. El insumo lo fabrica `plantear()` en
# `tests/quality_gates/phase_briefing/conftest.py:108`, fixture de pytest sobre `tmp_path` que
# devuelve el dict que pide `caso` (claves `raiz`, `plan_dir`, `nombre`, `doc1`, `fases`): planta
# `01-doc.md` con secciones 1 y 2, `.agents/workflows/phased_project_executor.md` y el prompt
# `05-prompt-inicio-sesion-fase-X.md` declarando la lectura con recorte. De ahi que la via viva de
# reproduccion sea pytest y no este archivo: `test_briefing_mutation_no_truncar.py:163`
# (`test_las_dos_salidas_van_a_destino_explicito_y_no_al_expediente_ajeno`) llama a
# `correr_a_destino(destino, caso)` con destino y caso explicitos. La equivalencia para este
# script seria montar bajo un directorio temporal propio ese mismo `caso` y pasar los dos
# argumentos: `arnes.correr_a_destino(Path(args.destino), caso)`.
#
# Y una comprobacion que cambia quien esta mal: con `git log --reverse` sobre el archivo del arnes,
# este entra al repositorio en `ae21d09` **ya** con `caso` obligatorio, y el instrumento se commiteo
# despues, en `8681f95` (`ae21d09` es ancestro de `8681f95`, medido con `git merge-base`). O sea: no
# existe ninguna revision publicada en la que la linea 39 funcionara. El arnes de una sola firma con
# el que se corrio la evidencia del 2026-09-24 vivia solo en el arbol de trabajo, y la cura del
# insumo plantado (bloque B de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md`, 2026-09-25) quedo
# versionada antes que el script que la invoca mal.⟧
