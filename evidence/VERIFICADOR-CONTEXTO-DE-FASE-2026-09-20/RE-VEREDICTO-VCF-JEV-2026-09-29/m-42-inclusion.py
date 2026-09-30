import io
import os
import subprocess
import sys

D = sys.argv[1]
A, C = u"\u27e6", u"\u27e7"
RUTAS = [
    "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VERIFICACION-VCF-JEV-2026-09-28/00-expediente.md",
    "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/SESION-SCRIPTS-CURAS-2026-09-28/00-resumen.md",
]

R = []
R.append("== 1. Balance de marcadores: HEAD contra disco, archivo por archivo ==")
R.append("comando: contar U+27E6 y U+27E7 en el blob de HEAD (git cat-file) y en el archivo del arbol de trabajo")
R.append("(la cuenta NO se hace con grep sobre la salida de git show, que normaliza y puede partir multibyte).")
for p in RUTAS:
    blob = subprocess.run(["git", "cat-file", "blob", "HEAD:" + p], stdout=subprocess.PIPE).stdout.decode("utf-8")
    disco = io.open(p, encoding="utf-8").read()
    for etiqueta, txt in (("HEAD ", blob), ("disco", disco)):
        R.append("   %-4s %-96s %d/%d balance=%+d" % (etiqueta, p, txt.count(A), txt.count(C), txt.count(A) - txt.count(C)))
    R.append("   delta introducido por esta sesion: aperturas %+d, cierres %+d"
             % (disco.count(A) - blob.count(A), disco.count(C) - blob.count(C)))
    R.append("")

R.append("== 2. Control de inclusion pura, con el predicado correcto ==")
R.append("La linea vieja y la nueva son la misma celda de tabla, alargada. El control no puede ser")
R.append("'la linea vieja aparece igual' (su cola cambia por construccion); es: el cuerpo viejo, sin su")
R.append("cola de cierre de celda, sigue presente caracter a caracter dentro de la linea nueva.")
for p in RUTAS:
    diff = subprocess.run(["git", "diff", "-U0", "--", p], stdout=subprocess.PIPE).stdout.decode("utf-8", errors="replace")
    viejas = [l[1:] for l in diff.split("\n") if l.startswith("-") and not l.startswith("---")]
    nuevas = [l[1:] for l in diff.split("\n") if l.startswith("+") and not l.startswith("+++")]
    R.append("")
    R.append("   %s : %d lineas suprimidas, %d anadidas" % (p, len(viejas), len(nuevas)))
    for v in viejas:
        cuerpo = v.rstrip()
        for cola in (" ⟧ |", "⟧ |", " |"):
            if cuerpo.endswith(cola):
                cuerpo = cuerpo[: -len(cola)]
                break
        casas = [n for n in nuevas if cuerpo in n]
        R.append("   vieja (%d chars) -> reaparece como prefijo intacto de %d linea(s) nueva(s): %s"
                 % (len(cuerpo), len(casas), "SI" if casas else "NO"))
        if casas:
            for n in casas:
                R.append("      nueva mide %d chars (delta +%d), y empieza igual: %s"
                         % (len(n), len(n) - len(cuerpo), n.startswith(cuerpo)))

R.append("")
R.append("== 3. Las notas nuevas, leídas enteras para revisar su balance propio ==")
for p in RUTAS:
    disco = io.open(p, encoding="utf-8").read()
    trozos = [t for t in disco.split(A) if C in t]
    R.append("   %s : %d bloques entre apertura y cierre" % (os.path.basename(p), len(trozos)))

with open(os.path.join(D, "42-balance-e-inclusion-pura.txt"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("\n".join(R) + "\n")
print("ESCRITO 42-balance-e-inclusion-pura.txt")
