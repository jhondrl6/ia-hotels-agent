"""S31: la ruta del plan del arnés la resuelve **el escritor**, no un literal del arnés.

`resolver_plan()` de `scripts/build_phase_briefing.py` es la función que sabe dónde vive un plan: en
`plans/`, en `plans/Archives/` o en la ruta que se le dé. Un arnés que pinea la ruta a pelo queda ciego
en cuanto el plan cambia de sitio — medido: el `git mv` de D-c (`3c2e6a3`, 2026-09-26) tiró **seis**
constantes `PLAN` de las selecciones FASE-C y FASE-D y metió **42** rojos en la suite sin que ningún
producto hubiera cambiado (fila §S31 de `dependencias-fases.md` del plan
`VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20`).

Este módulo es el puente: carga el escritor por ruta (como hacen los `conftest.py` de las dos
selecciones) y expone `ruta_plan()`, que delega en `resolver_plan()`. No reimplementa la resolución:
una sola copia de la regla, en el escritor.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ESCRITOR = ROOT / "scripts" / "build_phase_briefing.py"
PLANS = ROOT / ".opencode" / "plans"
NOMBRE_PLAN = "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"


def cargar_escritor(nombre: str = "bpb_puente_arnes"):
    """El escritor bajo prueba, cargado por ruta y bajo nombre unico (los `conftest` hacen lo mismo)."""
    spec = importlib.util.spec_from_file_location(nombre, ESCRITOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ruta_plan(nombre: str = NOMBRE_PLAN, plans_dir: Path = PLANS, escritor=None) -> Path:
    """La ruta del plan por `resolver_plan()` del escritor, con la semantica de error del literal.

    El arnés pineado fallaba con `FileNotFoundError` al leer la ruta que ya no estaba. Si el escritor
    no resuelve, se levanta **ese mismo** error nombrando las rutas intentadas — no un `None` que
    reviente tres líneas más tarde con un `AttributeError` que no dice qué plan faltaba (R2.9).
    """
    bpb = escritor or cargar_escritor()
    resuelto = bpb.resolver_plan(nombre, plans_dir)
    if resuelto is None:
        raise FileNotFoundError(
            f"el escritor no resolvio el plan {nombre!r} bajo {plans_dir.as_posix()}: se intentaron "
            f"{bpb.rutas_intentadas(nombre, plans_dir)}")
    return resuelto
