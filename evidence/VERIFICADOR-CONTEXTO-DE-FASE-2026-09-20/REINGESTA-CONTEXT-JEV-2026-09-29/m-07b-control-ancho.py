#!/usr/bin/env python3
"""Instrumento m-07b: control ancho post-redaccion.

La forma de la casa es x-oss-(...)= . Aqui se barre ademas cualquier parametro de consulta que
huela a credencial, en cualquier grafia, para no commitear firma por ninguna otra via.
No imprime valores: solo rutas de clave y conteos.
"""
import glob
import json
import re

E = "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/REINGESTA-CONTEXT-JEV-2026-09-29"
FORM_CASA = "x-os" + "s-" + "(signature|credential|date|expires)="
ANCHO = r"(?i)(signature|expires|credential|security[-_]token|access[-_]key|x[-_]oss[-_]acl|oids|acl)=|//[^\"\s]*\?[^\"\s]*="
MARK = "REDACTADA"


def walk(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, "%s.%s" % (path, k) if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, "%s[%d]" % (path, i))
    elif isinstance(node, str):
        yield path, node


for fp in sorted(glob.glob(E + "/*.json")):
    t = open(fp, encoding="utf-8").read()
    d = json.loads(t)
    hojas = list(walk(d))
    ancho = []
    for ruta, val in hojas:
        hits = len(re.findall(ANCHO, val))
        if hits:
            ancho.append((ruta.split("[")[0], hits))
    print("%s bytes=%d forma_casa=%d marcadores=%d" % (
        fp.split("/")[-1], len(t.encode("utf-8")), len(re.findall(FORM_CASA, t)),
        t.count('"%s"' % MARK)))
    acum = {}
    for r, h in ancho:
        acum[r] = acum.get(r, 0) + h
    print("  coincidencias_anchas_por_ruta=%s" % (acum or "ninguna"))
    # que hoja sigue siendo larga: una URL sin firma de credencial
    largas = sorted({ruta.split("[")[0] for ruta, val in hojas if len(val) > 200})
    print("  hojas_largas_quedan_en=%s" % (largas or "ninguna"))
