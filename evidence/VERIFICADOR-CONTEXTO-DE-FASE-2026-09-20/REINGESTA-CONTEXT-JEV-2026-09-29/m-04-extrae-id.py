#!/usr/bin/env python3
"""Instrumento m-04: extrae del JSON del upload SOLO los campos sin credencial.

Nunca imprime originUrl ni metadata.originalFileUri: llevan firma x-oss-*.
"""
import json

E = "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/REINGESTA-CONTEXT-JEV-2026-09-29"
SAFE = ("id", "title", "status", "type", "createdAt", "updatedAt", "notebookId", "nbId")

with open(E + "/03-t1-upload.json", encoding="utf-8") as fh:
    raw = fh.read()
print("bytes_json=%d" % len(raw.encode("utf-8")))
data = json.loads(raw)
node = data
if isinstance(node, dict):
    for key in ("data", "source", "result", "item"):
        if key in node and isinstance(node[key], (dict, list)):
            node = node[key]
            break
if isinstance(node, list):
    node = node[0] if node else {}

print("claves_raiz=%s" % sorted(data.keys()) if isinstance(data, dict) else "raiz_no_es_dict")
print("claves_nodo=%s" % sorted(node.keys()))
for k in SAFE:
    if k in node:
        print("%s=%s" % (k, node[k]))
md = node.get("metadata") or {}
print("metadata.fileSha256=%s" % md.get("fileSha256"))
print("metadata.claves=%s" % sorted(md.keys()))

with open(E + "/04a-id-nueva.txt", "w", encoding="utf-8", newline="\n") as fh:
    fh.write(str(node.get("id", "")) + "\n")
print("persistida=04a-id-nueva.txt")
