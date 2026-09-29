import io, subprocess

DEST = "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VERIFICACION-VCF-JEV-2026-09-28/19-paridad-en-delta-contra-head.txt"
V = ".opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"
J = ".opencode/plans/Archives/EVALUACION-JEV-TYPESAFE-2026-09-21"
files = [J + "/README.md", J + "/04-contrato-ejecucion.md", V + "/01-plan-maestro.md",
         V + "/04-contrato-ejecucion.md", V + "/10-analisis-post-implementacion.md",
         V + "/dependencias-fases.md"]

def stats(s):
    return dict(bt=s.count("`"), left=s.count("\u27e6"), right=s.count("\u27e7"),
                guil=s.count("\u00ab"), guilr=s.count("\u00bb"))

out = io.open(DEST, "w", encoding="utf-8", newline="\n")
out.write("== La paridad absoluta de backticks NO es el criterio: este corpus usa codigo inline anidado\n")
out.write("   (`` `x` `` suma 5 backticks, impar por diseño). Lo que importa es el DELTA que introduce la\n")
out.write("   anotacion de hoy. Se compara HEAD contra disco, archivo por archivo.\n\n")
out.write("%-64s | %s\n" % ("archivo", "HEAD -> disco (delta)"))
for f in files:
    head = subprocess.run(["git", "show", "HEAD:" + f], stdout=subprocess.PIPE).stdout.decode("utf-8")
    disco = io.open(f, encoding="utf-8").read()
    a, b = stats(head), stats(disco)
    parts = []
    for k, nombre in [("bt", "backticks"), ("left", "\u27e6"), ("right", "\u27e7"),
                      ("guil", "\u00ab"), ("guilr", "\u00bb")]:
        parts.append("%s %+d" % (nombre, b[k] - a[k]))
    deseq = (b["left"] - a["left"]) != (b["right"] - a["right"])
    out.write("%-64s | %s   %s\n" % (f.split("Archives/")[1], "  ".join(parts),
                                     "DESEQUILIBRADO POR LA NOTA" if deseq else "delta equilibrado"))
out.write("\n== Y el estado absoluto en HEAD (para no achacar a esta nota lo que ya venia):\n")
for f in files:
    head = subprocess.run(["git", "show", "HEAD:" + f], stdout=subprocess.PIPE).stdout.decode("utf-8")
    a = stats(head)
    out.write("   %-62s backticks=%d(%s) \u27e6=%d \u27e7=%d \u00ab=%d \u00bb=%d\n"
              % (f.split("Archives/")[1], a["bt"], "PAR" if a["bt"] % 2 == 0 else "IMPAR",
                 a["left"], a["right"], a["guil"], a["guilr"]))
out.close()
print("ok")
