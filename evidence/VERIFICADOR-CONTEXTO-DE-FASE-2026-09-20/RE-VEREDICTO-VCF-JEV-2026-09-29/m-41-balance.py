import io
import os
import re
import subprocess
import sys

D = sys.argv[1]
APERTURA = u"\u27e6"
CIERRE = u"\u27e7"

R = []
R.append("== Balance de marcadores de nota datada en los archivos tocados ==")
R.append("comando logico: contar por archivo las aperturas y los cierres (U+27E6 / U+27E7) sobre el texto UTF-8")
R.append("")
objetivos = [
    "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VERIFICACION-VCF-JEV-2026-09-28/00-expediente.md",
    "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/SESION-SCRIPTS-CURAS-2026-09-28/00-resumen.md",
    os.path.join(D, "00-expediente.md"),
]
for p in objetivos:
    c = io.open(p, encoding="utf-8").read()
    a, b = c.count(APERTURA), c.count(CIERRE)
    R.append("%-96s aperturas=%d cierres=%d balance=%+d  CR=%d" % (p, a, b, a - b, c.count("\r")))

R.append("")
R.append("== Control de inclusion pura: lo versionado no se perdio al anotar ==")
R.append("comando: git diff -U0 sobre las dos rutas anotadas, y lectura de que hay en cada linea '-'.")
for p in objetivos[:2]:
    d = subprocess.run(["git", "diff", "-U0", "--", p], stdout=subprocess.PIPE)
    texto = d.stdout.decode("utf-8", errors="replace")
    mas = [l for l in texto.split("\n") if l.startswith("+") and not l.startswith("+++")]
    menos = [l for l in texto.split("\n") if l.startswith("-") and not l.startswith("---")]
    R.append("")
    R.append("%s : %d lineas anadidas, %d suprimidas (git diff --numstat abajo)" % (p, len(mas), len(menos)))
    for l in menos:
        R.append("   SUPRIMIDA: %s" % l[:200])
        # La supresion debe volver a aparecer dentro de una de las anadidas (misma celda, re-escrita entera)
        interior = any(l[1:].strip() in x[1:] for x in mas)
        R.append("     esa linea reaparece intacta dentro de alguna anadida: %s" % interior)
R.append("")
R.append("== numstat por archivo ==")
for p in objetivos[:2]:
    d = subprocess.run(["git", "diff", "--numstat", "--", p], stdout=subprocess.PIPE)
    R.append("   " + d.stdout.decode("utf-8", errors="replace").strip())

R.append("")
R.append("== CJK barrido (la familia que ya costo dos commits en esta casa) ==")
CJK = re.compile(u"[\u3000-\u303f\u4e00-\u9fff\uff00-\uffef]")
for p in objetivos:
    c = io.open(p, encoding="utf-8").read()
    hall = CJK.findall(c)
    R.append("   %-96s CJK=%d %s" % (p, len(hall), "".join(hall[:10])))

with open(os.path.join(D, "41-balance-y-inclusion-pura.txt"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(R) + "\n")
print("ESCRITO 41-balance-y-inclusion-pura.txt")
