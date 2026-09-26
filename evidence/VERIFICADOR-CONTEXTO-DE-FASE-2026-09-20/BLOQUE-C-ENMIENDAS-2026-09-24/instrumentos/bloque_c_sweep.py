import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TARGETS = []
for p in sorted(Path(".opencode/plans").glob("*/*.md")):
    TARGETS.append(p)
TARGETS.append(Path(".opencode/context/ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md"))
TARGETS += sorted(Path("evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24").glob("*.md"))

CJK = re.compile(r"[\u3000-\u30ff\u4e00-\u9fff\uac00-\ud7af\uff00-\uffef]")
MOJI = re.compile(r"[ÂÃ]\w|â€|Ã³|Ã¡|Ã­|Ã±")
DOBLE = re.compile(r"\b(que|de|la|el|en|los|las|se|y|no|un|una)\s+\1\b", re.I)

hits = 0
for f in TARGETS:
    t = f.read_text(encoding="utf-8", errors="replace")
    for i, ln in enumerate(t.splitlines(), 1):
        for tag, rx in (("CJK", CJK), ("MOJI", MOJI), ("DOBLE", DOBLE)):
            m = rx.search(ln)
            if m:
                hits += 1
                print(f"[{tag}] {f}:{i} -> {m.group(0)!r} :: {ln.strip()[:120]}")
print("---")
print(f"revisados: {len(TARGETS)} archivos | coincidencias: {hits}")
