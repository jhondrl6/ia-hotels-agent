#!/usr/bin/env python3
"""Instrumento m-08: controles de los sellos fechados, HEAD contra disco.

Cuatro controles por archivo: CR, delta de marcadores ⟦⟧ (en crudo y excluyendo codigo inline),
CJK, y las citas nuevas de la linea añadida. Los dos numeros de cada par son HEAD y disco.
"""
import re
import subprocess

FILES = {
    "E1": "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VEREDICTO-VCF-JEV-2026-09-29/00-expediente.md",
    "E2": "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VERIFICACION-VCF-JEV-2026-09-28/00-expediente.md",
}
APERTURA = chr(0x27E6)
CIERRE = chr(0x27E7)
CJK = re.compile(chr(0x3000) + "-" + chr(0x303F) + chr(0x4E00) + "-" + chr(0x9FFF) + chr(0x3040) + "-" + chr(0x30FF) + chr(0xFF00) + "-" + chr(0xFFEF))
RUTA = re.compile(r"[\w./-]*(?:evidence|\.opencode|scripts|tests|docs)/[\w./-]+|REINGESTA-CONTEXT-JEV-[\w-]+")


def head_text(path):
    r = subprocess.run(["git", "show", "HEAD:" + path], capture_output=True)
    return r.stdout.decode("utf-8"), r.returncode


def sin_inline(texto):
    """Quit el codigo inline `...` por linea. Con backticks impares el filtro come texto de mas:
    se mide y se declara, no se fía."""
    pares = sum(1 for l in texto.split("\n") if l.count("`") % 2 == 1)
    filtrado = re.sub(r"`[^`\n]*`", "", texto)
    return filtrado, pares


for etiqueta, ruta in FILES.items():
    viejo, ex = head_text(ruta)
    assert ex == 0, (ruta, ex)
    nuevo = open(ruta, encoding="utf-8").read()
    print("== %s : %s" % (etiqueta, ruta))
    print("  CR_head=%d  CR_disco=%d" % (viejo.count("\r"), nuevo.count("\r")))
    print("  CJK_head=%d  CJK_disco=%d" % (len(CJK.findall(viejo)), len(CJK.findall(nuevo))))
    a_v, c_v = viejo.count(APERTURA), viejo.count(CIERRE)
    a_n, c_n = nuevo.count(APERTURA), nuevo.count(CIERRE)
    print("  marcadores_crudo  head=%d/%d balance=%d  disco=%d/%d balance=%d  delta=+%d/+%d" % (
        a_v, c_v, a_v - c_v, a_n, c_n, a_n - c_n, a_n - a_v, c_n - c_v))
    fv, pv = sin_inline(viejo)
    fn, pn = sin_inline(nuevo)
    print("  lineas_backtick_impar  head=%d  disco=%d" % (pv, pn))
    print("  marcadores_sin_inline  head=%d/%d  disco=%d/%d  delta=+%d/+%d" % (
        fv.count(APERTURA), fv.count(CIERRE), fn.count(APERTURA), fn.count(CIERRE),
        fn.count(APERTURA) - fv.count(APERTURA), fn.count(CIERRE) - fv.count(CIERRE)))
    print("  backticks_head=%d  backticks_disco=%d" % (viejo.count("`"), nuevo.count("`")))
    d = subprocess.run(["git", "diff", "--numstat", "--", ruta], capture_output=True)
    print("  numstat=%s" % d.stdout.decode("utf-8").strip())
    dd = subprocess.run(["git", "diff", "-U0", "--", ruta], capture_output=True)
    anadidas = [l for l in dd.stdout.decode("utf-8").split("\n") if l.startswith("+") and not l.startswith("+++")]
    suprimidas = [l for l in dd.stdout.decode("utf-8").split("\n") if l.startswith("-") and not l.startswith("---")]
    print("  lineas_anadidas=%d  lineas_suprimidas=%d" % (len(anadidas), len(suprimidas)))
    for i, l in enumerate(suprimidas):
        print("    suprimida_%d=%s" % (i, l[:160]))
    cuerpo = "".join(l[1:] for l in anadidas)
    print("  marcadores_en_lo_anadido=%d/%d" % (cuerpo.count(APERTURA), cuerpo.count(CIERRE)))
    print("  backticks_en_lo_anadido=%d (par=%s)" % (cuerpo.count("`"), cuerpo.count("`") % 2 == 0))
    citas_viejas = set(RUTA.findall(viejo))
    citas_nuevas = sorted(set(RUTA.findall(cuerpo)) - citas_viejas)
    print("  citas_nuevas_de_rutas=%d %s" % (len(citas_nuevas), citas_nuevas))
    cifras = sorted(set(re.findall(r"\b\d[\d.]{2,}\b", cuerpo)))
    print("  cifras_re_transcritas_en_lo_anadido=%d %s" % (len(cifras), cifras))
    print()
