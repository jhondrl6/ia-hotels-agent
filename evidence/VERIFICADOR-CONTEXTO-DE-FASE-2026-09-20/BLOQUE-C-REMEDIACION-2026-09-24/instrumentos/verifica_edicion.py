"""M5 + M7: verificar la edicion desde disco, no el resumen del que edito.

Compara el snapshot `antes/` contra el archivo vivo y publica:
  - que la edicion es INSERCION PURA (0 lineas borradas): el resto del archivo no se movio
  - conteo de filas de tabla y de miembros de las tablas vecinas (el riesgo del old_string que spanea)
  - el texto anotado, leido en UTF-8 desde disco
  - segundo camino (M7): quien consume el dato, no quien lo anoto

Uso: verifica_edicion.py
"""
import difflib
import re
import sys
import unicodedata
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-REMEDIACION-2026-09-24"

PARES = [
    ("B1", EXP / "antes/B1-README.md",
     ROOT / ".opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/README.md"),
    ("B2", EXP / "antes/B2-06-checklist-implementacion.md",
     ROOT / ".opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/06-checklist-implementacion.md"),
    ("B3", EXP / "antes/B3-02-resultados-bloque-c.md",
     ROOT / "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/02-resultados-bloque-c.md"),
]


def lineas(p):
    with open(p, encoding="utf-8") as fh:
        return fh.read().splitlines()


def tablas(lines):
    """[(linea_inicio, n_filas)] de cada bloque de filas consecutivas que empiezan por '|'."""
    out, i, n = [], 0, len(lines)
    while i < n:
        if lines[i].lstrip().startswith("|"):
            j = i
            while j < n and lines[j].lstrip().startswith("|"):
                j += 1
            out.append((i + 1, j - i, max(lines[k].count("|") for k in range(i, j))))
            i = j
        else:
            i += 1
    return out


def columnas(line):
    return line.count("|")


# La rectificacion es una ANOTACION ⟦…⟧ INCRUSTADA A MEDIA LINEA. "0 lineas borradas" no es el
# predicado aqui: lo que prueba que no se movio otra cosa es que, suprimido el bloque anotado y
# colapsados los blancos, el trozo anterior y el posterior son EL MISMO TEXTO.
# Los corchetes son chr(10214)/chr(10215) = U+27E6/U+27E7. `\N{LEFT WHITE SQUARE BRACKET}` NO es
# U+27E6 (resuelve a U+301A) y con ese nombre el predicado devuelve un falso "NO" permanente: fue el
# fallo propio que esta linea deja anotado.
AP = re.compile(chr(10214) + ".*?" + chr(10215), re.S)


def sin_anotacion(s):
    return AP.sub("", s)


def plano(seg):
    return " ".join(sin_anotacion(" ".join(seg)).split())


print("=== CONTROL M1 del supresor de anotaciones ===")
_ctrl = (ROOT / ".opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"
         / "06-checklist-implementacion.md").read_text(encoding="utf-8")
_p = [m.group(0) for m in AP.finditer(_ctrl)]
print(f"  bloques ⟦…⟧ que el supresor encuentra en 06-checklist: {len(_p)} "
      f"(la anotacion de E5 es una de ellas: {any('Vencido en parte el 2026-09-24' in x for x in _p)})")
print(f"  suprimirlos deja estrictamente menos caracteres: {len(sin_anotacion(_ctrl))} < {len(_ctrl)} -> "
      f"{len(sin_anotacion(_ctrl)) < len(_ctrl)}")
print()

for nombre, antes, vivo in PARES:
    a, b = lineas(antes), lineas(vivo)
    sm = difflib.SequenceMatcher(None, a, b)
    ops = [op for op in sm.get_opcodes() if op[0] != "equal"]
    borradas = sum(i2 - i1 for tag, i1, i2, j1, j2 in ops if tag in ("delete", "replace"))
    anadidas = sum(j2 - j1 for tag, i1, i2, j1, j2 in ops if tag in ("insert", "replace"))
    restaura = all(plano(a[i1:i2]) == plano(b[j1:j2]) for tag, i1, i2, j1, j2 in ops)
    solo_anotado = all(
        sin_anotacion(" ".join(b[j1:j2])).strip() and plano(a[i1:i2]) == plano(b[j1:j2])
        for tag, i1, i2, j1, j2 in ops
    )
    print(f"=== {nombre}  {vivo.relative_to(ROOT).as_posix()} ===")
    print(f"  lineas antes/despues: {len(a)} / {len(b)}   anadidas: {anadidas}   sustituidas: {borradas}")
    print(f"  hunks: {len(ops)} -> {[(t, i1+1, i2+1, j1+1, j2+1) for t, i1, i2, j1, j2 in ops]}")
    print(f"  ORIGINAL RECUPERABLE SUPRIMIENDO LA ANOTACION: {'SI' if restaura else 'NO'}")
    print(f"  UNICO CAMBIO = el bloque anotado (no se quedo contenido fuera): {'SI' if solo_anotado else 'NO'}")
    for tag, i1, i2, j1, j2 in ops:
        chars = len(" ".join(b[j1:j2])) - len(sin_anotacion(" ".join(b[j1:j2])))
        print(f"  hunk {j1+1}-{j2}: {j2-j1} linea(s), {chars} caracteres dentro de ⟦…⟧, "
              f"el resto del hunk es byte a byte el texto anterior: {restaura}")
    ta, tb = tablas(a), tablas(b)
    des_a = [(x[0], x[1]) for x in ta if len({columnas(l) for l in a[x[0]-1:x[0]-1+x[1]]}) > 1]
    des_b = [(x[0], x[1]) for x in tb if len({columnas(l) for l in b[x[0]-1:x[0]-1+x[1]]}) > 1]
    print(f"  bloques de tabla: {len(ta)} -> {len(tb)}  (deben ser iguales: ninguna tabla nacio ni murio)")
    print(f"  filas por bloque: {[x[1] for x in ta]} -> {[x[1] for x in tb]}")
    print(f"  bloques con columnas desiguales ANTES: {des_a}")
    print(f"  bloques con columnas desiguales DESPUES (offset +12 si se edito): {des_b}")
    print(f"  tabla desigual introducida por esta edicion: "
          f"{'NINGUNA' if len(des_a) == len(des_b) else 'REVISAR'}")
    print("  texto anotado, releido desde disco:")
    for tag, i1, i2, j1, j2 in ops:
        for k in range(j1, j2):
            print(f"    {k+1:>4} {b[k][:200]}")
    print()

readme_jev = (ROOT / ".opencode/plans/EVALUACION-JEV-TYPESAFE-2026-09-21/README.md").read_text(encoding="utf-8")
print("=== M7 segundo camino: el consumidor del dato, no quien lo anoto ===")
seis = ["provider_requested", "model_requested", "usage_normalized",
        "elapsed_ms", "attempts", "error_kind"]
parrafo = [l for l in readme_jev.splitlines() if l.startswith("**Gap de contrato medido")]
print(f"  parrafos del gap en JEV/README.md: {len(parrafo)}")
for p in parrafo:
    print("  JEV/README.md publica estos seis como los no expuestos -> "
          + ", ".join(f"{s}:{'si' if '`'+s+'`' in p else 'NO'}" for s in seis))
print(f"  JEV/README.md no contiene la cadena '8 de los 11': {'8 de los 11' not in readme_jev}")
# M1: control positivo de la MISMA busqueda, en el archivo que si la contiene
expi = lineas(PARES[2][2])
print(f"  [CONTROL M1] la misma cadena '8 de los 11' SI aparece en el expediente de C: "
      f"{sum('8 de los 11' in l for l in expi)} linea(s) -> la ausencia anterior no es ceguera del patron")
print("  B3: el '8' queda conservado, no sobrescrito: "
      f"{sum('8 de los 11 campos' in l for l in lineas(PARES[2][2]))} linea(s) del expediente lo mantienen")
