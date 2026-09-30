#!/usr/bin/env python3
"""Instrumento m-17 (v2): las citas del expediente tienen que resolver, y el indice de crudos tiene que ser completo.

La primera version de este instrumento estaba mal: barria cualquier token entre backticks con forma
`NN-…`, y eso incluye ids de fuente (`01a0efcc-3297-…`), fragmentos de fecha (`09-29`) y nombres de plan.
Salian **7 rutas que no resuelven** que no eran citas rotas sino un predicado equivocado. Ahi estaba el defecto.

Dos controles, cada uno con su unidad:
  (1) prefijos de crudo LOCAL citados en el texto -> tienen que ser prefijo de al menos un archivo de la carpeta
  (2) las citas de RUTAS DE AFUERA, listadas a mano porque son finitas y se pueden nombrar una por una
"""
import os
import re

E = "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/REINGESTA-CONTEXT-JEV-2026-09-29"
MD = E + "/00-expediente.md"
PLANA = os.path.dirname(E)
RAIZ = "C:/Users/Jhond/Github/iah-cli"
texto = open(MD, encoding="utf-8").read()
nombres = sorted(os.listdir(E))

print("== (1) prefijos de crudo LOCAL citados ==")
tallos = sorted({n[:len(m.group(0))] for n in nombres for m in [re.match(r"^\d{2}[a-z]?-", n)] if m})
tallos = sorted({n.split("-")[0] for n in nombres if re.match(r"^\d{2}[a-z]?-", n)})
cit = sorted(set(re.findall(r"`(\d{2}[a-z]?)-", texto)))
print("  tallos_reales=%s" % tallos)
print("  citados=%s" % cit)
huerf = [c for c in cit if c not in tallos]
print("  citados_sin_archivo=%s" % (huerf or "NINGUNO"))
sin = [t for t in tallos if t not in cit]
print("  crudos_reales_sin_nombrar=%s" % (sin or "NINGUNO"))

print()
print("== (2) citas de rutas de afuera, nombradas una por una ==")
FUERA = {
    "hermano citado por los tres sellos": PLANA + "/REINGESTA-CONTEXT-JEV-2026-09-29/00-expediente.md",
    "expediente del RE-VEREDICTO (sello 1 y 3)": PLANA + "/RE-VEREDICTO-VCF-JEV-2026-09-29/00-expediente.md",
    "expediente del RE-VERIFICACION (sello 2)": PLANA + "/RE-VERIFICACION-VCF-JEV-2026-09-28/00-expediente.md",
    "crudo 19 del hermano (82 funciones)": PLANA + "/RE-VEREDICTO-VCF-JEV-2026-09-29/19-t3-pytest-82.txt",
    "crudo 22 del hermano (modo completo)": PLANA + "/RE-VEREDICTO-VCF-JEV-2026-09-29/22-t4-modo-completo.txt",
    "crudo 24 del hermano (suite suelta)": PLANA + "/RE-VEREDICTO-VCF-JEV-2026-09-29/24-t4b-suite-completa.txt",
    "archivo gobernado (el CONTEXT)": RAIZ + "/.opencode/context/CONTEXT-JEV-TYPESAFE-CASOS-DE-USO-2026-09-21.md",
    "plan JEV archivado": RAIZ + "/.opencode/plans/Archives/EVALUACION-JEV-TYPESAFE-2026-09-21",
    "plan del hermano (Archives)": RAIZ + "/.opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20",
    "verificador de write-back": RAIZ + "/scripts/validate_qmind_writeback.py",
    "verificador de packs": RAIZ + "/scripts/build_phase_briefing.py",
    "verificador del indice": RAIZ + "/scripts/build_lesson_index.py",
    "runner": RAIZ + "/scripts/run_all_validations.py",
    "integracion documental": RAIZ + "/scripts/validate_document_integration.py",
}
rotas = []
for etiqueta, ruta in sorted(FUERA.items()):
    ok = os.path.exists(ruta)
    print("  %-42s %s" % (etiqueta, "OK" if ok else "ROTA: " + ruta))
    if not ok:
        rotas.append(etiqueta)
print("  citas_rotas=%d %s" % (len(rotas), rotas or []))

print()
print("== nombres de plan citados, buscados en Archives y en raiz ==")
for plan in ["TRIBUNAL-OFFLINE-2026-09-09"]:
    hit = [p for p in (RAIZ + "/.opencode/plans/Archives/" + plan, RAIZ + "/.opencode/plans/" + plan) if os.path.exists(p)]
    print("  %s -> %s" % (plan, hit or "NO EXISTE"))

print()
print("== self-control final del expediente ==")
AP, CI = chr(0x27E6), chr(0x27E7)
CJK = re.compile("[" + chr(0x3000) + "-" + chr(0x303F) + chr(0x4E00) + "-" + chr(0x9FFF)
                 + chr(0x3040) + "-" + chr(0x30FF) + chr(0xFF00) + "-" + chr(0xFFEF) + "]")
print("bytes=%d  lineas=%d  CR=%d  CJK=%d" % (len(texto.encode("utf-8")), texto.count(chr(10)),
                                               texto.count(chr(13)), len(CJK.findall(texto))))
print("marcadores=%d/%d  backticks=%d par=%s" % (texto.count(AP), texto.count(CI), texto.count("`"),
                                                 texto.count("`") % 2 == 0))
filas = sorted({l.count("|") - l.count("\\|") for l in texto.split(chr(10)) if l.startswith("|")})
escapes = sorted({l.count("\\|") for l in texto.split(chr(10)) if l.startswith("|")})
print("  pipes_reales_por_fila=%s  pipes_escapados_por_fila=%s" % (filas, escapes))
print("  (las tablas son de 3 y 4 columnas: 4 y 5 pipes; los dos escapes de la fila D-E no anchan ninguna celda)")
