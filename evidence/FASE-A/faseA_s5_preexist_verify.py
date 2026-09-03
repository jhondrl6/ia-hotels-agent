"""Verifica S5: los 2 tests rojos de test_proposal_dynamic.py ya fallaban ANTES de FASE-A.

Compara el estado pre-cambio (faseA_predinamico.txt, capturado antes de editar nada) contra el
estado final (faseA_dynamic_final.txt). Normaliza ruido de corrida: direcciones de objeto,
duraciones y numeros de linea del propio archivo de tests (FASE-A lo edito al invertir 6
aserciones fosilizadas, ver L-A5), que desplazan la cita sin cambiar lo asertado.
"""

import difflib
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRE = HERE / "faseA_predinamico.txt"
POST = HERE / "faseA_dynamic_final.txt"

# pytest trunca/estira la barra de guiones bajos segun el largo del nombre del test.
_BLOCK = re.compile(r"(?m)^_{1,}\s+(\S+)\s+_{1,}$")

_NOISE = [
    (r"object at 0x[0-9A-Fa-f]+", "object at 0xADDR"),
    (r"in \d+\.\d+s", "in T"),
    (r"test_proposal_dynamic\.py:\d+", "test_proposal_dynamic.py:LN"),
    (r"v4_proposal_generator\.py:\d+", "v4_proposal_generator.py:LN"),
]

# El ultimo bloque de POST absorbe el "warnings summary" y el "short test summary" que le siguen.
_TAIL = re.compile(r"(?ms)^=+ warnings summary =+$.*\Z")


def blocks(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    parts = _BLOCK.split(text)
    out = {}
    for i in range(1, len(parts) - 1, 2):
        out.setdefault(parts[i].strip(), parts[i + 1])
    return out


def normalize(body):
    for pattern, repl in _NOISE:
        body = re.sub(pattern, repl, body)
    return _TAIL.sub("", body).strip()


def summary(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    return [ln for ln in text.splitlines() if ln.startswith("FAILED") or " failed," in ln]


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if not PRE.exists() or not POST.exists():
        print(f"FALTA EVIDENCIA: {PRE.name}={PRE.exists()} {POST.name}={POST.exists()}")
        return 1

    pre, post = blocks(PRE), blocks(POST)
    print(f"PRE  ({PRE.name}): {len(pre)} bloques de fallo")
    print(f"POST ({POST.name}): {len(post)} bloques de fallo")
    print()

    failures = 0
    for name in sorted(post):
        if name not in pre:
            print(f"[REGRESION] {name} -- rojo en POST, ausente en PRE")
            failures += 1
            continue
        a, b = normalize(pre[name]), normalize(post[name])
        if a == b:
            print(f"[PREEXISTENTE] {name} -- asercion identica pre y post FASE-A")
        else:
            print(f"[MODO-CAMBIADO] {name} -- rojo antes y despues, pero el fallo difiere:")
            for line in difflib.unified_diff(
                a.splitlines(), b.splitlines(), "PRE", "POST", lineterm="", n=1
            ):
                print("    " + line[:200])
            failures += 1
        print()

    print("=== Sumario PRE (antes de tocar nada) ===")
    for line in summary(PRE):
        print("  " + line)
    print()
    print("=== Sumario POST (cierre de FASE-A) ===")
    for line in summary(POST):
        print("  " + line)
    print()

    n_pre = len([ln for ln in summary(PRE) if ln.startswith("FAILED")])
    n_post = len([ln for ln in summary(POST) if ln.startswith("FAILED")])
    print(f"Rojos: PRE={n_pre}  POST={n_post}  (FASE-A cerro {n_pre - n_post} fosilizados)")
    print("VEREDICTO:", "S5 confirmado" if failures == 0 else "S5 NO confirmado")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
