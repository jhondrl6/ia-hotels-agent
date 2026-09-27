#!/usr/bin/env python3
"""Verificar los packs de briefing contra lo que el **escritor** produce en el árbol de un commit.

Existe por **S19** (medido 2026-09-26): la frescura de un pack la gobierna el `sha256` de `sources[]`, y el
generador no está entre sus propias fuentes. Editar al escritor deja entonces los packs commiteados con
texto viejo mientras `build_phase_briefing.py --check` dice `EXIT=0`: ese check compara fuentes, no producto.
Este verificador cierra el hueco por el otro lado — regenera y compara el producto.

No compara bytes crudos: el escritor estampa su reloj. Medido, los únicos tokens no deterministas del
conjunto son 53 líneas de 9.481 (el sello `generado` en prosa y `generated_at`/`head` en el bloque meta),
y al normalizarlos dos corridas sucesivas dan el mismo digest por pack. Se normaliza también `head` porque
el commit que generó el pack y la revisión materializada rara vez coinciden, y AC21 ya declaró ese campo
no-gobernante.

Materializa con `clon_fiel` (S20): un clon heredando el `core.autocrlf` del ámbito system reescribe LF→CRLF
y cualquier comparación por bytes corta rojo falso sobre un commit correcto.

Salida: 0 = el árbol reproduce sus packs; 1 = al menos uno diverge; 2 = el método no produjo árbol
evaluable, o algún pack quedó **no evaluable** porque el escritor declaró una fuente fuera del árbol
materializado (un veredicto que no puede ver su insumo no se disfraza ni de verde ni de rojo).
"""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_index_in_committed_tree import ENTORNO_UTF8, clon_fiel  # noqa: E402
from build_phase_briefing import resolver_plan  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ESCRITOR = "scripts/build_phase_briefing.py"
SCRATCH = "_verif-packs-scratch"
PLAN_CANONICO = "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"

NORMALIZAR = (
    (re.compile(r"· generado `[0-9TZ:.+-]+`"), ""),
    (re.compile(r'"generated_at": "[0-9TZ:.+-]+"'), '"generated_at": "N"'),
    (re.compile(r"HEAD `[0-9a-f]{7,40}`"), "HEAD `H`"),
    (re.compile(r'"head": "[0-9a-f]{7,}"'), '"head": "H"'),
)


def _normalizado(texto: str) -> str:
    for patron, reemplazo in NORMALIZAR:
        texto = patron.sub(reemplazo, texto)
    return texto


def _digest(texto: str) -> str:
    return hashlib.sha256(_normalizado(texto).encode("utf-8")).hexdigest()


def _primera_diferencia(antes: str, despues: str) -> tuple[int, str]:
    """Cuánto diverge y dónde: un [DIVERGE] sin atribución obliga a reproducir la corrida a mano.

    Muestra la diferencia **en su contexto**, no el prefijo de la línea: las líneas de un pack son frases
    largas y el token que cambia suele estar al final (medido: `[8/11]` queda detrás de 110 caracteres).
    """
    a = _normalizado(antes).splitlines()
    b = _normalizado(despues).splitlines()
    indices = [n for n in range(max(len(a), len(b))) if (a[n:n + 1] or [""]) != (b[n:n + 1] or [""])]
    if not indices:
        return 0, "(misma línea a línea, distinto ensamblado)"
    n = indices[0]
    x = (a[n] if n < len(a) else "").strip()
    y = (b[n] if n < len(b) else "").strip()
    k = 0
    while k < min(len(x), len(y)) and x[k] == y[k]:
        k += 1
    desde = max(0, k - 24)
    return len(indices), (f"L{n + 1} ...{x[desde:k + 34]!r} -> ...{y[desde:k + 34]!r}")


def _pares(carpetas: tuple[Path, Path]) -> list[str]:
    """Nombres de pack en cualquiera de los dos lados: lo que falta también es una divergencia."""
    a = {p.name for p in carpetas[0].glob("FASE-*.md")} if carpetas[0].is_dir() else set()
    b = {p.name for p in carpetas[1].glob("FASE-*.md")} if carpetas[1].is_dir() else set()
    return sorted(a | b)


def _no_avaluables(corrida: subprocess.CompletedProcess) -> dict[str, str]:
    """El escritor no emite un pack cuya fuente declarada no existe: eso es límite del método, no rojo.

    Devuelve `{fase: documento}` leído de su propio log (`[pack] FASE-X: FUENTE-AUSENTE -> no emitido`
    seguido de la línea `    - <documento>: fuente ausente`). Contarlo como divergencia acusaría al
    commit de algo que el árbol materializado no puede ver.
    """
    texto = (corrida.stderr or "") + (corrida.stdout or "")
    out: dict[str, str] = {}
    fase_actual = None
    for linea in texto.splitlines():
        m = re.match(r"\[pack\] (FASE-[^:]+): FUENTE-AUSENTE", linea.strip())
        if m:
            fase_actual = m.group(1)
            out.setdefault(fase_actual, "(documento no nombrado)")
            continue
        if fase_actual and "fuente ausente" in linea:
            documento = linea.strip().lstrip("- ").split(":", 1)[0].strip()
            out[fase_actual] = documento
            fase_actual = None
    return out


def verificar(plans: list[str], rev: str, destino: Path, clon: Path | None = None,
              conservar: bool = False) -> int:
    if clon is None:
        clon, motivo = clon_fiel(destino, rev)
        if clon is None:
            print(f"[ERROR] {motivo[0]}")
            return 2

    total = 0
    divergentes = 0
    sin_evaluar = 0
    for plan in plans:
        # La ruta del plan se resuelve con el MISMO criterio que usa el escritor: `plans/<X>` o
        # `plans/Archives/<X>`. D-c archivó el plan canónico y este verificador, que tenía la ruta
        # montada a pelo, pasó a dar `AUSENTE-EN-VERSIONADO` sobre cinco packs perfectos — o sea el
        # rápido rojo por un defecto del instrumento, medido el 2026-09-27 sobre 3c2e6a3.
        resuelto = resolver_plan(plan, clon / ".opencode" / "plans")
        if resuelto is None:
            print(f"[NO-EVALUABLE] {plan}: el árbol materializado no tiene el plan "
                  "(ni bajo `plans/` ni bajo `plans/Archives/`)")
            sin_evaluar += 1
            continue
        raiz_plan = resuelto.resolve()
        versionados = raiz_plan / "briefing"
        generado = raiz_plan / SCRATCH
        if generado.exists():
            shutil.rmtree(generado, ignore_errors=True)

        # Sin `--informe` ni `--carga`: su default escribe dentro de evidencia cerrada de otra fase (S12).
        # `--briefing-dir` va ABSOLUTO: el subprocess corre con cwd=clon, y una ruta relativa se resolvería
        # contra el clon y escribiría en otro sitio (medido: el veredicto salía NO-PRODUCIDO general).
        corrida = subprocess.run(
            [sys.executable, ESCRITOR, "--plan", plan, "--briefing-dir", str(generado)],
            cwd=str(clon), capture_output=True, text=True, encoding="utf-8", errors="replace",
            env=ENTORNO_UTF8,
        )
        if corrida.returncode not in (0, 1):
            print(f"[ERROR] el escritor no produjo en el árbol de {plan}: rc={corrida.returncode} "
                  f"{(corrida.stderr or corrida.stdout).strip()[:200]}")
            return 2

        no_evaluables = _no_avaluables(corrida)

        for nombre in _pares((versionados, generado)):
            fase = nombre[:-3]
            total += 1
            ruta_antes, ruta_despues = versionados / nombre, generado / nombre
            if not ruta_despues.is_file() and fase in no_evaluables:
                sin_evaluar += 1
                print(f"[NO-EVALUABLE] {plan}/{nombre} "
                      f"(el escritor no lo emite: fuente fuera del árbol: {no_evaluables[fase]})")
                continue
            if not (ruta_antes.is_file() and ruta_despues.is_file()):
                divergentes += 1
                print(f"[DIVERGE] {plan}/{nombre} "
                      f"({'AUSENTE-EN-VERSIONADO' if not ruta_antes.is_file() else 'NO-PRODUCIDO'})")
                continue
            antes = ruta_antes.read_text(encoding="utf-8", errors="replace")
            despues = ruta_despues.read_text(encoding="utf-8", errors="replace")
            if _digest(antes) == _digest(despues):
                print(f"[OK] {plan}/{nombre}")
            else:
                divergentes += 1
                n, donde = _primera_diferencia(antes, despues)
                print(f"[DIVERGE] {plan}/{nombre} ({n} líneas) {donde}")
        if not conservar:
            shutil.rmtree(generado, ignore_errors=True)

    reproducidos = total - divergentes - sin_evaluar
    if divergentes:
        veredicto, codigo = "DIVERGE", 1
    elif sin_evaluar:
        veredicto, codigo = "INCOMPLETO", 2
    else:
        veredicto, codigo = "OK", 0
    print(f"[{veredicto}] packs en el árbol de {rev} "
          f"({reproducidos}/{total} reproducidos por el escritor, "
          f"{divergentes} divergentes, {sin_evaluar} no evaluables)")
    return codigo


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--rev", default="HEAD",
                        help="revisión cuyo árbol se verifica; fija en un test, nunca HEAD")
    parser.add_argument("--plan", action="append", default=None,
                        help=f"plan cuyos packs se verifican (repetible); por defecto {PLAN_CANONICO}")
    parser.add_argument("--clon", type=Path, default=None,
                        help="verificar sobre un árbol ya materializado (control negativo)")
    parser.add_argument("--keep", type=Path, default=None, help="no borrar el clon, y ponerlo aquí")
    args = parser.parse_args()

    plans = args.plan or [PLAN_CANONICO]
    if args.clon:
        return verificar(plans, args.rev, args.clon, clon=args.clon, conservar=True)

    if args.keep:
        args.keep.mkdir(parents=True, exist_ok=True)
        return verificar(plans, args.rev, args.keep, conservar=True)

    scratch = Path(tempfile.mkdtemp(prefix="verif-packs-"))
    try:
        return verificar(plans, args.rev, scratch)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
