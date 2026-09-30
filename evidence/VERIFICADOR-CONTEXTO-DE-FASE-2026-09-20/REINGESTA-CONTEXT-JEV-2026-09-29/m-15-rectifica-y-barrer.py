#!/usr/bin/env python3
"""Instrumento m-15: rectifica el cero falso del instrumento anterior y cierra el barrido de toda la carpeta.

El m-14 contaba los marcadores con `grep -o "$AP"` donde AP salia de `python -c print(chr(0x27E6))`. Bajo cp1252
ese print **reventa** y la variable queda vacia: el `0` publicado era un cero de instrumento roto, no una medida.
Aqui se mide leyendo el archivo en UTF-8. Y se repite el barrido de credenciales y CJK con TODOS los archivos que
existen al cerrar, incluidos los que el propio m-14 creo despues de su pase.
"""
import glob
import os
import re

E = "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/REINGESTA-CONTEXT-JEV-2026-09-29"
AP, CI = chr(0x27E6), chr(0x27E7)
CJK = re.compile("[" + chr(0x3000) + "-" + chr(0x303F) + chr(0x4E00) + "-" + chr(0x9FFF)
                 + chr(0x3040) + "-" + chr(0x30FF) + chr(0xFF00) + "-" + chr(0xFFEF) + "]")
FORM = "x-os" + "s-" + "(signature|credential|date|expires)="
ANCHO = r"(?i)(?:signature|expires|credential|security[-_]token|access[-_]key|x[-_]oss[-_]acl)=|//[^\"'\s)]*\?[^\"'\s)]*="
FECHA_MALA = "2022-" + "09-29"

md = E + "/00-expediente.md"
t = open(md, encoding="utf-8").read()
print("== self-control del expediente nuevo, medido en UTF-8 ==")
print("bytes=%d  lineas=%d" % (len(t.encode("utf-8")), t.count(chr(10))))
print("CR=%d" % t.count(chr(13)))
print("marcadores=%d/%d  balance=%d  (los dos citan la FORMA de la casa dentro de codigo inline)" % (
    t.count(AP), t.count(CI), t.count(AP) - t.count(CI)))
print("backticks=%d  par=%s" % (t.count("`"), t.count("`") % 2 == 0))
print("CJK=%d" % len(CJK.findall(t)))
print("lineas_con_backtick_impar=%d" % sum(1 for l in t.split(chr(10)) if l.count("`") % 2 == 1))
print("menciones_de_la_fecha_mala=%d" % t.count(FECHA_MALA))
print("menciones_de_la_cadena_partida=%d (la forma en que se cita aqui, para no autocontaminar el barrido)" % t.count(FECHA_MALA[:5] + "` + `"))

print()
print("== barrido de TODA la carpeta al cerrar ==")
arch = [f for f in sorted(glob.glob(E + "/*")) if os.path.isfile(f)]
forma = ancho = cjk = logs = fecha = 0
for fp in arch:
    txt = open(fp, encoding="utf-8", errors="replace").read()
    f = len(re.findall(FORM, txt))
    a = len(re.findall(ANCHO, txt))
    forma += f
    ancho += a
    cjk += len(CJK.findall(txt))
    logs += 1 if fp.endswith(".log") else 0
    n = txt.count(FECHA_MALA)
    fecha += n
    if f or a:
        print("  FUGA %s forma=%d ancho=%d" % (os.path.basename(fp), f, a))
print("archivos=%d  forma=%d  ancho=%d  CJK=%d  con_extension_log=%d  menciones_fecha_mala=%d" % (
    len(arch), forma, ancho, cjk, logs, fecha))
print("los dos unicos md que llevan la cadena partida son este expediente y el crudo 11:")
for fp in arch:
    txt = open(fp, encoding="utf-8", errors="replace").read()
    if FECHA_MALA in txt:
        print("  %s -> %d" % (os.path.basename(fp), txt.count(FECHA_MALA)))
