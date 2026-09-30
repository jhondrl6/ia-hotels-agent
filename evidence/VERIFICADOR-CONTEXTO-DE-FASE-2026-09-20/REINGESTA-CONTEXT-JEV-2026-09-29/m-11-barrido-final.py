#!/usr/bin/env python3
"""Instrumento m-11: barrido de residuos y de fugas, sobre la carpeta de evidencia y los dos archivos sellados.

Cuatro preguntas, cada una con su unidad declarada:
  (a) la fecha mal escrita que se corrigio en un sello, cuantas veces queda y donde
  (b) CJK en los archivos que se van a commitear
  (c) crudos con extension `.log`, que el .gitignore excluye en silencio
  (d) cualquier forma de credencial en TODA la carpeta, no solo en los JSON
"""
import glob
import os
import re
import subprocess

E = "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/REINGESTA-CONTEXT-JEV-2026-09-29"
SELLADOS = [
    "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VEREDICTO-VCF-JEV-2026-09-29/00-expediente.md",
    "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VERIFICACION-VCF-JEV-2026-09-28/00-expediente.md",
]
FECHA_MALA = "2022-" + "09-29"
CJK = re.compile("[" + chr(0x3000) + "-" + chr(0x303F) + chr(0x4E00) + "-" + chr(0x9FFF)
                 + chr(0x3040) + "-" + chr(0x30FF) + chr(0xFF00) + "-" + chr(0xFFEF) + "]")
FORM = "x-os" + "s-" + "(signature|credential|date|expires)="
ANCHO = r"(?i)(?:signature|expires|credential|security[-_]token|access[-_]key|x[-_]oss[-_]acl)=|//[^\"'\s)]*\?[^\"'\s)]*="

print("== (a) la fecha mal escrita ==")
for r in SELLADOS:
    print("  %s -> %d" % (os.path.basename(os.path.dirname(r)), open(r, encoding="utf-8").read().count(FECHA_MALA)))
en_carpeta = 0
for fp in sorted(glob.glob(E + "/*")):
    if os.path.isfile(fp):
        try:
            n = open(fp, encoding="utf-8", errors="replace").read().count(FECHA_MALA)
        except Exception as exc:
            n = "ERROR:%s" % exc
        if n:
            print("  %s -> %s" % (fp.split("/")[-1], n))
            en_carpeta += n if isinstance(n, int) else 0
print("  total_en_la_carpeta_de_esta_tanda=%d" % en_carpeta)
d = subprocess.run(["git", "grep", "-c", FECHA_MALA, "HEAD"], capture_output=True, text=True)
print("  en_HEAD (lineas con la cadena, archivo:conteo)=%s" % (d.stdout.strip() or "0 coincidencias"))
print("  EXIT_GREP_HEAD=%d (1 = sin coincidencias)" % d.returncode)

print()
print("== (b) CJK en lo que se commitea ==")
tot = 0
for fp in sorted(glob.glob(E + "/*")) + SELLADOS:
    if os.path.isfile(fp):
        n = len(CJK.findall(open(fp, encoding="utf-8", errors="replace").read()))
        tot += n
print("  archivos_barridos=%d  CJK_total=%d" % (len([f for f in glob.glob(E + "/*") if os.path.isfile(f)]) + len(SELLADOS), tot))

print()
print("== (c) crudos con extension .log ==")
logs = [f for f in glob.glob(E + "/*") if f.endswith(".log")]
print("  en_esta_carpeta=%d %s" % (len(logs), [os.path.basename(x) for x in logs]))
regla = subprocess.run(["git", "check-ignore", "-v", E + "/prueba.log"], capture_output=True, text=True)
print("  git_check_ignore_vuelve=%r EXIT=%d (confirma que la regla sigue activa)" % (regla.stdout.strip(), regla.returncode))

print()
print("== (d) credenciales en TODA la carpeta ==")
forma = ancho = 0
for fp in sorted(glob.glob(E + "/*")):
    if not os.path.isfile(fp):
        continue
    t = open(fp, encoding="utf-8", errors="replace").read()
    f = len(re.findall(FORM, t))
    a = len(re.findall(ANCHO, t))
    forma += f
    ancho += a
    if f or a:
        print("  %s forma=%d ancho=%d" % (os.path.basename(fp), f, a))
print("  TOTAL_forma=%d  TOTAL_ancho=%d" % (forma, ancho))
md = glob.glob(E + "/descarga-*.md")
print("  descargas_guardadas=%d bytes=%s" % (len(md), [os.path.getsize(x) for x in md]))
for x in md:
    print("     %s forma=%d" % (os.path.basename(x), len(re.findall(FORM, open(x, encoding="utf-8").read()))))
