import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(".")
FILES = []
for p in sorted(ROOT.glob(".opencode/plans/*/*.md")):
    FILES.append(p)
FILES.append(Path(".opencode/context/ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md"))
FILES += sorted(Path("evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24").glob("*.md"))


def cells(line: str) -> int:
    body = line.strip()
    body = re.sub(r"^\|", "", body)
    body = re.sub(r"\|$", "", body)
    # contar pipes no escapados
    n = len(re.findall(r"(?<!\\)\|", body))
    return n + 1


problemas = 0
for f in FILES:
    lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
    fence = False
    table = None  # (start_line, ncols)
    for i, ln in enumerate(lines, 1):
        if ln.lstrip().startswith("```"):
            fence = not fence
            table = None
            continue
        if fence:
            continue
        s = ln.strip()
        is_row = s.startswith("|") and s.endswith("|")
        if is_row:
            n = cells(s)
            if table is None:
                table = (i, n)
            elif n != table[1]:
                problemas += 1
                print(f"[TABLA] {f}:{i}  columnas={n} esperado={table[1]} (cabecera en {table[0]})")
                print(f"        {s[:150]}")
        else:
            table = None
    if s.endswith("|") and not s.startswith("|"):
        print(f"[SUERTE] {f}: ultima linea termina en |")

print("---")
print(f"archivos revisados: {len(FILES)} | problemas de tablas: {problemas}")
