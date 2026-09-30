#!/usr/bin/env python3
"""Instrumento m-33: cada ruta que el registro unico cita tiene que resolver en el arbol.

El redactor (yo) corrompe nombres largos bajo carga: este control existe porque ya paso con
`RE-VEREDICTO`/`RE-VERIFICACION` y con los crudos `19-`/`24-` de la tanda anterior.
"""
import os
import re

RAIZ = "C:/Users/Jhond/Github/iah-cli"
MD = RAIZ + "/evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/REINGESTA-CONTEXT-JEV-2026-09-29/33-registro-unificado-de-pendientes-2026-09-29.md"
texto = open(MD, encoding="utf-8").read()

# candidatos: todo token con forma de ruta del repo o de crudo numerado
rutas = set(re.findall(r"(?:\.opencode|docs|evidence|scripts)/[\w./-]+", texto))
crudos = set(re.findall(r"`(\d{2}[a-z]?-[\w.-]+)`", texto))

print("== rutas tipo arbol citadas ==")
rotas = []
for r in sorted(rutas):
    p = (r if r.startswith("/") else RAIZ + "/" + r).replace("\\", "/")
    ok = os.path.exists(p)
    if not ok:
        rotas.append(r)
    print("  %-95s %s" % (r[:95], "OK" if ok else "NO RESUELVE"))

print()
print("== crudos numerados citados: se buscan por nombre entre las carpetas de evidencia del plan ==")
base = RAIZ + "/evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"
hallados = {}
for c in sorted(crudos):
    hit = []
    for raiz, _dirs, files in os.walk(base):
        for f in files:
            if f.startswith(c.split("-")[0]) and c.split("-", 1)[1] in f:
                hit.append(os.path.join(raiz, f).replace(RAIZ + "/", ""))
    hallados[c] = hit
    print("  %-28s %s" % (c, "OK: " + hit[0] if hit else "NO RESUELVE"))

print()
print("RESUMEN: rutas_rotas=%d  crudos_sin_resolver=%d" % (
    len(rotas), sum(1 for v in hallados.values() if not v)))
for r in rotas:
    print("  ROTA:", r)
