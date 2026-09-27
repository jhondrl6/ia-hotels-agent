"""Auditoria de prosa del expediente 24-: CJK, paridad de marcadores, CR y citas numericas."""
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = pathlib.Path("evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/CIERRE-ORDEN-2026-09-25")
RUTAS = sorted(BASE.glob("24-*.txt"))
O, C = chr(10214), chr(10215)
CJK = re.compile(r"[\u3000-\u303f\u4e00-\u9fff\uff00-\uffef]")
CITACION = re.compile(
    r"[A-Za-z0-9_\-./\\]+\.(?:py|md|yaml|yml|json|txt|html|csv|lock|toml|ini|sh|bat):"
    r"\d+(?:\s*[-–]\s*\d+)?"
)

for p in RUTAS:
    t = p.read_text(encoding="utf-8")
    print(f"== {p.name}")
    print(f"   bytes={len(t.encode('utf-8'))}  lineas={t.count(chr(10)) + 1}  CR={'SI' if chr(13) in t else 'no'}")
    print(f"   marcadores: abre={t.count(O)} cier={t.count(C)} delta={t.count(O) - t.count(C)}")
    hits = [(m.start(), t[max(0, m.start() - 60):m.start() + 20].replace("\n", " "))
            for m in CJK.finditer(t)]
    print(f"   CJK: {len(hits)}")
    for pos, ctx in hits:
        print(f"     @{pos}: ...{ctx}...")
    print(f"   citas numericas (no gobernadas aqui, pero declaradas): {len(CITACION.findall(t))}")
