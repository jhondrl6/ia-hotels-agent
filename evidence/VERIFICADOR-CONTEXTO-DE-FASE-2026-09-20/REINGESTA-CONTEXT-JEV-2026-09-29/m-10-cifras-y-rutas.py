#!/usr/bin/env python3
"""Instrumento m-10: dos controles que el anterior no aislo.

(a) Las cifras de la linea D-E: se resta el conjunto del HEAD contra el del disco. Lo que sobra es lo que
    la nota nueva publico; lo demas es texto preexistente que el diff re-emite por ser una sola linea.
(b) Las rutas citadas por las notas nuevas tienen que resolver en el arbol.
"""
import os
import re
import subprocess

E1 = "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VEREDICTO-VCF-JEV-2026-09-29/00-expediente.md"
E2 = "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VERIFICACION-VCF-JEV-2026-09-28/00-expediente.md"
CIFRA = re.compile(r"\b\d[\d.]{2,}\b")
EXPEDIENTE_NUEVO = "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/REINGESTA-CONTEXT-JEV-2026-09-29/00-expediente.md"


def fila(ruta_texto, prefijo):
    for l in ruta_texto.split("\n"):
        if l.startswith(prefijo):
            return l
    return ""


head2 = subprocess.run(["git", "show", "HEAD:" + E2], capture_output=True).stdout.decode("utf-8")
disk2 = open(E2, encoding="utf-8").read()
f_head = fila(head2, "| **D-E** |")
f_disk = fila(disk2, "| **D-E** |")
a = set(CIFRA.findall(f_head))
b = set(CIFRA.findall(f_disk))
print("longitud_fila_head=%d  disco=%d" % (len(f_head), len(f_disk)))
print("cifras_head=%d  disco=%d" % (len(a), len(b)))
print("cifras_nuevas_en_la_fila=%s" % sorted(b - a))
print("cifras_perdidas_en_la_fila=%s  (debe ser vacio: la fila no se reescribe, se alarga)" % sorted(a - b))
prefijo_intacto = f_head and f_disk.startswith(f_head[:400])
print("el_head_es_prefijo_del_disco_primeros_400=%s" % prefijo_intacto)

head1 = subprocess.run(["git", "show", "HEAD:" + E1], capture_output=True).stdout.decode("utf-8")
disk1 = open(E1, encoding="utf-8").read()
n1 = set(CIFRA.findall(disk1)) - set(CIFRA.findall(head1))
print("cifras_nuevas_en_E1=%s" % sorted(n1))

print()
print("== resolucion de la ruta apuntada por los tres sellos ==")
print("ruta=%s" % EXPEDIENTE_NUEVO)
print("existe=%s" % os.path.exists(EXPEDIENTE_NUEVO))
print("existe_carpeta=%s" % os.path.isdir(os.path.dirname(EXPEDIENTE_NUEVO)))
print()
print("== donde cayeron los sellos de E1 (cabecera, no numero de linea) ==")
for etiqueta, clave in (("§4", "## 4."), ("§10", "## 10.")):
    i = disk1.index(clave)
    j = disk1.find("\n## ", i + 1)
    trozo = disk1[i:j if j > 0 else len(disk1)]
    print("  %s lleva_marca_del_sello=%s  tamano_trozo=%d" % (
        etiqueta, "REINGESTA-CONTEXT-JEV-2026-09-29" in trozo, len(trozo)))
print("  en_§10_nombra_la_divergencia=%s" % ("Vivas al cerrar" in disk1))
