#!/usr/bin/env python3
"""Verificar la frescura del índice de lecciones **en el árbol de un commit**, no en el de trabajo.

Existe por una medición de 2026-09-26: el commit `911f8d7` llevaba un índice vencido y el hook
`[6/7]` lo dio en verde, porque ese check corre `build_lesson_index.py --check` contra el árbol de
trabajo. El rojo solo apareció al correr el mismo check dentro de un clon del commit. De ahí la regla
que esta herramienta convierte en máquina: *verde en mi árbol no es verde en mi commit*.

No se usa `git archive` para extraer el árbol: `_git_fecha` del generador devuelve `None` ante un
documento sin repositorio, así que una extracción limpia declara `SIN-FUENTE` en las 11 entradas
fechadas por commit y el check falla **por diseño** esté el índice como esté. Un clon sí trae historial.

Y el clon se configura **por dentro** antes de materializar (S20): `git clone` no copia el config local de
la fuente, así que sin `core.autocrlf=input` escrito en el clon el `checkout` hereda el `true` del ámbito
system y reescribe LF→CRLF. Sobre ese árbol re-escrito, cualquier comparación de bytes —el `--check` de
briefing, no el del índice— corta rojo falso.

Salida: 0 = fresco en ese árbol; 1 = vencido; 2 = el método no pudo producir un árbol evaluable.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# `docs` y `.agents` no las consume el índice, pero sí los packs de briefing: FASE-RELEASE declara como
# fuente `docs/CONTRIBUTING.md`, y sin esa ruta en el árbol el escritor la declara `FUENTE-AUSENTE` y no
# emite el pack (medido 2026-09-26 al construir verify_packs_in_committed_tree). Materializar la unión
# cuesta ~1 s más y hace evaluable al verificador de derivados.
MATERIALIZAR = ("scripts", ".opencode", "docs", ".agents")
GENERADOR = "scripts/build_lesson_index.py"
# Sin esto, el hijo escribe en la codepage de la consola (cp1252 en Windows) y quien capture la salida
# guarda bytes ilegibles en UTF-8: el veredicto sobrevive, la línea `[fechas]` ya no es comparable.
ENTORNO_UTF8 = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _rutas_esperadas(clon: Path, rev: str) -> list[str]:
    salida = _git(["ls-files", "--full-name", "-z", "--", *MATERIALIZAR], clon)
    if salida.returncode != 0:
        return []
    return [p for p in salida.stdout.split("\0") if p]


def _presentes(clon: Path, rutas: list[str]) -> list[str]:
    return [r for r in rutas if not (clon / r).is_file()]


def clon_fiel(destino: Path, rev: str) -> tuple[Path | None, list[str]]:
    """Materializar `rev` en un clon cuyo árbol sea byte a byte el del commit.

    Devuelve `(clon, [])` o `(None, [motivo])`. Está separado de `revisar` porque hay un segundo
    verificador de derivados que necesita el mismo árbol: la fidelidad es propiedad del materializado,
    no del check, y duplicar el clon sería duplicar también la trampa de S20.
    """
    clon = (destino / "arbol").resolve()
    if clon.exists():
        shutil.rmtree(clon, ignore_errors=True)

    if _git(["rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}"], ROOT).returncode != 0:
        return None, [f"revisión inexistente en este repositorio: {rev}"]

    clonada = _git(
        ["-c", "core.autocrlf=input", "clone", "--local", "--no-checkout", str(ROOT), str(clon)],
        ROOT,
    )
    if clonada.returncode != 0:
        return None, [f"no se pudo clonar el repositorio: {clonada.stderr.strip()[:400]}"]

    # Las dos trampas del materializado se resuelven DENTRO del clon, no en la línea de comandos:
    # `git clone` no copia el config local de la fuente, y el `-c` que se le pasa solo gobierna ese
    # proceso. El `checkout` de abajo corre ya dentro del clon y lee la config **del clon**.
    # - Sin `longpaths`, el checkout aborta en las rutas largas de `.opencode/.qoder` y deja un árbol
    #   parcial (medido: 519 de 6106 archivos) con el que cualquier veredicto es ruido.
    # - Sin `autocrlf`, el clon hereda el `true` del ámbito *system* de Windows y el checkout reescribe
    #   LF→CRLF al materializar (medido 2026-09-26, S20, sobre `c85dff9`): con `input` el `--check` de
    #   briefing da `EXIT=0`, con `true` da `EXIT=1` y `SHA-DISTINTO` **en el mismo commit**.
    for clave, valor in (("core.longpaths", "true"), ("core.autocrlf", "input")):
        fijada = _git(["config", clave, valor], clon)
        if fijada.returncode != 0:
            return None, [f"no se pudo fijar {clave}={valor}: "
                          f"{(fijada.stderr or fijada.stdout).strip()[:200]}"]

    # Se lee el valor efectivo en lugar de asumir que escribirlo funcionó: si el árbol no es fiel, el
    # veredicto no mide el commit y no debe salir como 0 ni como 1.
    efectiva = _git(["config", "--get", "core.autocrlf"], clon).stdout.strip()
    if efectiva != "input":
        return None, [f"autocrlf efectivo del clon es {efectiva!r}, no 'input': su árbol reescribe "
                      "remates y no es evaluable por bytes"]

    checkout = _git(["checkout", rev, "--", *MATERIALIZAR], clon)
    if checkout.returncode != 0:
        return None, [f"checkout parcial de {rev}: {checkout.stderr.strip()[:400]}"]

    esperadas = _rutas_esperadas(clon, rev)
    faltantes = _presentes(clon, esperadas)
    if faltantes:
        return None, [f"árbol incompleto: faltan {len(faltantes)} de {len(esperadas)} rutas"]

    return clon, []


def revisar(rev: str, destino: Path) -> int:
    """Correr en el árbol de `rev` el `--check` del generador de índice."""
    clon, motivo = clon_fiel(destino, rev)
    if clon is None:
        print(f"[ERROR] {motivo[0]}")
        return 2

    esperadas = _rutas_esperadas(clon, rev)
    corrida = subprocess.run(
        [sys.executable, GENERADOR, "--check"],
        cwd=str(clon),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=ENTORNO_UTF8,
    )
    marcas = ("[OK]", "[FAIL]", "[fechas]")
    resumen = [b for b in corrida.stdout.splitlines() if b.startswith(marcas)]
    for linea in resumen:
        print(linea)
    veredicto = "OK" if corrida.returncode == 0 else "VENCIDO"
    print(f"[{veredicto}] índice en el árbol de {rev} ({len(esperadas)} rutas materializadas)")
    return corrida.returncode


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--rev",
        default="HEAD",
        help="revisión cuyo árbol se verifica; fija en un test, nunca HEAD",
    )
    parser.add_argument(
        "--keep",
        type=Path,
        default=None,
        help="no borrar el clon, y ponerlo en esta ruta",
    )
    args = parser.parse_args()

    if args.keep:
        args.keep.mkdir(parents=True, exist_ok=True)
        return revisar(args.rev, args.keep)

    scratch = Path(tempfile.mkdtemp(prefix="verif-arbol-commit-"))
    try:
        return revisar(args.rev, scratch)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
