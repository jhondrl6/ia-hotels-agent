#!/usr/bin/env python3
"""Instrumento m-07a: sonda previa a la redaccion.

Cuenta la forma de credencial, las secuencias \\uXXXX escapadas y los caracteres no ASCII de cada JSON,
sin imprimir ningun valor.
"""
import glob
import re

FORM = "x-os" + "s-" + "(signature|credential|date|expires)="
BS = chr(92) + "u"
# re no admite \u en un patron sin sus cuatro digitos hexadecimales: se cuenta por subcadena literal
E = "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/REINGESTA-CONTEXT-JEV-2026-09-29"

for fp in sorted(glob.glob(E + "/*.json")):
    t = open(fp, encoding="utf-8").read()
    no_ascii = [c for c in t if ord(c) > 127]
    print("%s bytes=%d forma=%d secuencias_u=%d no_ascii=%d" % (
        fp.split("\\")[-1].split("/")[-1], len(t.encode("utf-8")),
        len(re.findall(FORM, t)),
        t.count(BS),
        len(no_ascii)))
