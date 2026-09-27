"""Poblacion S16 re-medida con DOS criterios, uno de ellos el lector real.

Criterio A (el de la sesion anterior, `13-poblacion-s16.py`): prompts que tienen una linea que
arranca por `Lee `, admitiendo sangrado y prefijo de cita.
Criterio B (el que goberna el pack): importar `parsear_lista_lectura` del propio generador y
pedirle la lista declarada a cada prompt archivado. Es el lector real, no una imitacion.
"""
import importlib.util
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
RAIZ = pathlib.Path(__file__).resolve().parents[4]
spec = importlib.util.spec_from_file_location("bp", RAIZ / "scripts" / "build_phase_briefing.py")
bp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bp)

arch = RAIZ / ".opencode" / "plans" / "Archives"
prompts = sorted(arch.glob("*/05-prompt-inicio-sesion-fase-*.md"))
print(f"prompts de fase bajo Archives/             : {len(prompts)}")


def lee_texto(p):
    return p.read_text(encoding="utf-8", errors="replace")


criterio_a = [p for p in prompts if re.search(r"^\s*(?:>\s*)?Lee ", lee_texto(p), re.M)]
print(f"A) linea que arranca `Lee ` (cualquier forma): {len(criterio_a)}")

resueltos = []
for p in prompts:
    try:
        items = bp.parsear_lista_lectura(lee_texto(p))
    except Exception as e:  # el lector real tambien puede caer: se declara, no se asume ausencia
        print(f"   LECTOR-FALLIDO en {p.as_posix()}: {type(e).__name__}")
        continue
    if items:
        resueltos.append((p, len(items)))

print(f"B) items parseados por el generador (no vacio): {len(resueltos)}")
for p, n in resueltos:
    print(f"   {n:3d}  {p.parent.name}/{p.name}")

de_otro_plan = [p for p, _ in resueltos if "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20" not in p.as_posix()]
print(f"   de ellos, ajenos a este plan            : {len(de_otro_plan)}")
print(f"A sin B (linea `Lee ` que el generador no resuelve): "
      f"{len([p for p in criterio_a if p not in [q for q, _ in resueltos]])}")
print(f"poblacion que NO declara lectura (criterio B): {len(prompts) - len(resueltos)}")
