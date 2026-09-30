#!/usr/bin/env python3
"""Instrumento m-09: colapsa la fila D-E a UNA linea fisica.

La nota anterior se escribio con saltos de linea dentro de la celda y rompio la fila de la tabla
(un fila de markdown es una sola linea fisica). Aqui se une el bloque, se verifica que no se perdió
ni un caracter salvo los saltos, y que ninguna otra fila se movio.
"""
import subprocess

RUTA = "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VERIFICACION-VCF-JEV-2026-09-28/00-expediente.md"
APERTURA = chr(0x27E6)
CIERRE = chr(0x27E7)

lineas = open(RUTA, encoding="utf-8").read().split("\n")
inicio = [i for i, l in enumerate(lineas) if l.startswith("| **D-E** |")]
assert len(inicio) == 1, inicio
i = inicio[0]
j = i
while not lineas[j].rstrip().endswith(CIERRE + " |"):
    j += 1
    assert j - i < 12, "el bloque de la fila no cierra: %s" % lineas[j][:80]
bloque = lineas[i:j + 1]
print("lineas_fisicas_de_la_fila_antes=%d  (i=%d j=%d, base 1: %d-%d)" % (len(bloque), i, j, i + 1, j + 1))
if len(bloque) == 1:
    print("nada_que_colapsar: la fila ya es una linea")
    raise SystemExit(0)

# el colapso: un espacio donde habia un salto de linea. No se comprimen los espacios dobles:
# la identidad se verifica ignorando espacios, y un doble espacio en una celda es inofensivo.
unida = bloque[0]
for pedazo in bloque[1:]:
    unida = unida.rstrip() + " " + pedazo.lstrip()

antes = "".join(bloque)
despues = unida
sig_antes = [c for c in antes if c not in " \n"]
sig_despues = [c for c in despues if c not in " \n"]
print("identico_salvo_espacios=%s" % (sig_antes == sig_despues))
if sig_antes != sig_despues:
    for k, (a, b) in enumerate(zip(sig_antes, sig_despues)):
        if a != b:
            print("  primera_diferencia_en=%d %r vs %r" % (k, "".join(sig_antes[k:k+40]), "".join(sig_despues[k:k+40])))
            break
    raise SystemExit(1)

nuevas = lineas[:i] + [unida] + lineas[j + 1:]
print("lineas_archivo_antes=%d  despues=%d" % (len(lineas), len(nuevas)))
filas = [l for l in nuevas if l.startswith("| ")]
filas_antes = [l for l in lineas if l.startswith("| ")]
print("filas_de_tabla_antes=%d  despues=%d" % (len(filas_antes), len(filas)))
print("marcadores_antes=%d/%d  despues=%d/%d" % (
    "\n".join(lineas).count(APERTURA), "\n".join(lineas).count(CIERRE),
    "\n".join(nuevas).count(APERTURA), "\n".join(nuevas).count(CIERRE)))
print("la_fila_empieza_por_D-E=%s  termina_en_cierra=%s" % (unida.startswith("| **D-E** |"), unida.rstrip().endswith(CIERRE + " |")))
print("longitud_fila=%d" % len(unida))

with open(RUTA, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(nuevas))
print("escrito_con_LF=%s" % True)
d = subprocess.run(["git", "diff", "--numstat", "--", RUTA], capture_output=True)
print("numstat_post=%s" % d.stdout.decode("utf-8").strip())
