"""Instrumento de la ronda: suma la tercera columna de la tabla de Cobertura por Modulo.

Imprime fila por fila lo que parsea, para que un desvio sea adjudicable a una fila y no a la cuenta.
"""
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(r"C:/Users/Jhond/Github/iah-cli")
AGENTS = RAIZ / "AGENTS.md"
CANON = ["bash", "-c", 'grep -rE "^\\s*def test_" tests --include=*.py | wc -l']
VERSIONADO = ["bash", "-c", 'git grep -c -E "^\\s*def test_" HEAD -- tests | '
                            'awk -F: \'{s+=$NF} END {print s}\'']

fila = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|")

lineas = AGENTS.read_text(encoding="utf-8").splitlines()
i0 = next(n for n, l in enumerate(lineas) if "Funciones test" in l and l.startswith("|"))
i1 = next(n for n, l in enumerate(lineas) if l.startswith("| root test files"))

total = 0
n = 0
for l in lineas[i0 + 2: i1 + 1]:
    m = fila.match(l)
    if not m:
        print(f"SIN-PARSEO: {l[:60]}")
        continue
    n += 1
    total += int(m.group(2))
    print(f"{n:2d} {m.group(1):<32} {m.group(2):>5}")

disco = int(subprocess.run(CANON, cwd=RAIZ, capture_output=True, text=True,
                           encoding="utf-8", errors="replace").stdout.strip())
head = int(subprocess.run(VERSIONADO, cwd=RAIZ, capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout.strip())
cabecera = next(l for l in lineas if l.startswith("### Cobertura por Modulo"))
cifra_cabecera = int(re.search(r"\(([\d,]+) funciones", cabecera).group(1).replace(",", ""))

print(f"FILAS={n}")
print(f"SUMA_FILAS={total}")
print(f"CIFRA_CABECERA={cifra_cabecera}")
print(f"CANONICO_DISCO={disco}")
print(f"VERSIONADO_HEAD={head}")
print("TODO_CASA" if total == cifra_cabecera == disco == head else "NO_CASA")
sys.exit(0 if total == cifra_cabecera == disco == head else 1)
