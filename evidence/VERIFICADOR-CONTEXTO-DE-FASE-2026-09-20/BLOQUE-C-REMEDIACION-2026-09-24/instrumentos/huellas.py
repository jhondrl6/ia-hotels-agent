"""Firmas sha256 sobre un manifiesto determinista, y comparacion PRE/POST por diccionarios.

Uso:
  huellas.py emit                      -> imprime "sha256  ruta" por archivo, orden sorted()
  huellas.py compare PRE.txt POST.txt  -> imprime altas/bajas/cambios por ruta (dict, no comm)

Leer en binario: open(..., "rb") evita que la conversion de texto de Windows re-codifique
y falsee la huella (lecciones del plan: sha de blob git vs disco es artefacto CRLF).
"""
import hashlib
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[4]

PLAN_DIRS = [
    "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20",
    "REFACTOR-WHATSAPP-ENTREGA-2026-09-18",
    "EVALUACION-JEV-TYPESAFE-2026-09-21",
    "VERIFICADOR-ESCRITURA-QMIND-2026-09-20",
]

EXTRA = [
    ".opencode/context/ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md",
    ".opencode/LECCIONES-INDEX.md",
    ".opencode/lecciones_index.json",
    ".opencode/plans/plan_citations_baseline.json",
    ".opencode/refs_baseline.txt",
    "scripts/decision_client.py",
    "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/02-resultados-bloque-c.md",
]


def manifiesto():
    rutas = []
    for d in PLAN_DIRS:
        p = ROOT / ".opencode" / "plans" / d
        for md in p.glob("*.md"):
            rutas.append(md.relative_to(ROOT).as_posix())
    rutas += EXTRA
    out = []
    for r in sorted(set(rutas)):
        f = ROOT / r
        if f.is_file():
            out.append(r)
        else:
            out.append(r + "  [AUSENTE]")
    return out


def sha256(rel):
    f = ROOT / rel
    if not f.is_file():
        return "AUSENTE"
    h = hashlib.sha256()
    with open(f, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def emit():
    for r in manifiesto():
        if r.endswith("[AUSENTE]"):
            print(f"{'-'*64}  {r}")
        else:
            print(f"{sha256(r)}  {r}")


def parse(path):
    d = {}
    with open(path, encoding="utf-8") as fh:
        for ln in fh:
            parts = ln.rstrip("\n").split("  ", 1)
            if len(parts) == 2 and len(parts[0]) == 64:
                d[parts[1]] = parts[0]
    return d


def compare(a, b):
    da, db = parse(a), parse(b)
    solo_a = sorted(set(da) - set(db))
    solo_b = sorted(set(db) - set(da))
    movidos = sorted(k for k in set(da) & set(db) if da[k] != db[k])
    iguales = len(set(da) & set(db) - set(movidos))
    print(f"manifiesto A: {len(da)} | manifiesto B: {len(db)}")
    print(f"solo en A (bajas): {len(solo_a)}")
    for k in solo_a:
        print(f"  - {k}")
    print(f"solo en B (altas): {len(solo_b)}")
    for k in solo_b:
        print(f"  + {k}")
    print(f"cambiados: {len(movidos)}")
    for k in movidos:
        print(f"  ~ {k}")
    print(f"identicos: {iguales}")


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "emit":
        emit()
    elif mode == "compare":
        compare(sys.argv[2], sys.argv[3])
    else:
        raise SystemExit(f"modo desconocido: {mode}")
