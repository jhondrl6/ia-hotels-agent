#!/usr/bin/env python3
"""Instrumento m-06: estado POST del notebook.

Cuenta Total, coincidencias del stem y titulos repetidos (control anti-gemelo).
No imprime originUrl ni metadata.originalFileUri.
"""
import json
from collections import Counter

E = "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/REINGESTA-CONTEXT-JEV-2026-09-29"
NB = "01a04d98-b7bd-778c-8441-26fdc7e35f45"
SRC_OLD = "01a0e4d9-e442-7d1b-bde5-7e9b669a2701"
STEM = "CONTEXT: CONTEXT-JEV-TYPESAFE-CASOS-DE-USO-2026-09-21"
with open(E + "/04a-id-nueva.txt", encoding="utf-8") as fh:
    SRC_NEW = fh.read().strip()

with open(E + "/06-source-list-post.json", encoding="utf-8") as fh:
    data = json.load(fh)
print("claves_raiz=%s" % sorted(data.keys()))
items = data.get("sources") or data.get("items") or data.get("data")
print("totalSize_json=%s  currentPage=%s  pageSize=%s" % (data.get("totalSize"), data.get("currentPage"), data.get("pageSize")))
print("total_items=%d" % len(items))

hitos = [s for s in items if STEM in (s.get("title") or "")]
print("coincidencias_del_stem=%d" % len(hitos))


def _created(s):
    c = s.get("createdAt")
    if isinstance(c, dict):
        return c.get("seconds", 0)
    return c or ""


for s in sorted(hitos, key=_created):
    md = s.get("metadata") or {}
    print("  id=%s  status=%s  fileSha256=%s" % (s.get("id"), s.get("status"), md.get("fileSha256")))
    print("     title=%s" % s.get("title"))

cont = Counter((s.get("title") or "") for s in items)
dupes = {t: c for t, c in cont.items() if c > 1}
print("titulos_repetidos=%d" % len(dupes))
for t, c in sorted(dupes.items()):
    print("  %d x %s" % (c, t))

ids = {s.get("id") for s in items}
print("fuente_anterior_presente=%s (debe ser True: esta orden NO borra)" % (SRC_OLD in ids))
print("fuente_nueva_presente=%s" % (SRC_NEW in ids))

# la vieja sigue vencida y la nueva casa con el disco: se afirma por sha publicado
by_id = {s.get("id"): s for s in items}
for label, sid in (("anterior", SRC_OLD), ("nueva", SRC_NEW)):
    md = (by_id.get(sid) or {}).get("metadata") or {}
    print("%s.fileSha256=%s" % (label, md.get("fileSha256")))
