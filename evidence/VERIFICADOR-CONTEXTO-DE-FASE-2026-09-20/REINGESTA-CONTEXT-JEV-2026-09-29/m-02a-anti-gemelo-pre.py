#!/usr/bin/env python3
"""Instrumento m-02a: control anti-gemelo sobre el listado PRE.

No imprime campos con URL firmada: solo id, title, status y metadata.fileSha256.
"""
import json
import sys
from collections import Counter

E = "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/REINGESTA-CONTEXT-JEV-2026-09-29"
SRC = "01a0e4d9-e442-7d1b-bde5-7e9b669a2701"
STEM = "CONTEXT: CONTEXT-JEV-TYPESAFE-CASOS-DE-USO-2026-09-21"

with open(E + "/02-source-list-pre.json", encoding="utf-8") as fh:
    data = json.load(fh)

items = data if isinstance(data, list) else data.get("items") or data.get("sources") or data.get("data")
print("type_raiz=%s  clave_items=%s" % (type(data).__name__, "raiz" if isinstance(data, list) else "items/sources/data"))
print("total_items=%d" % len(items))
if not isinstance(data, list):
    print("otras_claves_raiz=%s" % sorted(k for k in data if k not in ("items", "sources", "data")))

hitos = [s for s in items if STEM in (s.get("title") or "")]
print("coincidencias_del_stem=%d" % len(hitos))
for s in hitos:
    md = s.get("metadata") or {}
    print("  id=%s" % s.get("id"))
    print("  title=%s" % s.get("title"))
    print("  status=%s" % s.get("status"))
    print("  fileSha256=%s" % md.get("fileSha256"))

cont = Counter((s.get("title") or "") for s in items)
dupes = {t: c for t, c in cont.items() if c > 1}
print("titulos_repetidos=%d" % len(dupes))
for t, c in sorted(dupes.items()):
    print("  %d x %s" % (c, t))

print("fuente_objetivo_presenta=%s" % any(s.get("id") == SRC for s in items))
sys.exit(0)
