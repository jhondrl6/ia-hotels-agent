import io, re

DEST = "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VERIFICACION-VCF-JEV-2026-09-28/18-paridad-de-delimitadores.txt"
V = ".opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"
J = ".opencode/plans/Archives/EVALUACION-JEV-TYPESAFE-2026-09-21"
files = [J + "/README.md", J + "/04-contrato-ejecucion.md", V + "/01-plan-maestro.md",
         V + "/04-contrato-ejecucion.md", V + "/10-analisis-post-implementacion.md",
         V + "/dependencias-fases.md"]

out = io.open(DEST, "w", encoding="utf-8", newline="\n")
out.write("== Control de delimitadores y EOL despues de las anotaciones del 2026-09-28\n")
out.write("== Porque una comilla o un backtick impares convierten un filtro por contexto en un\n")
out.write("   anotador huerfano (y un CR de mas es la familia S17).\n\n")
todo_ok = True
for f in files:
    raw = io.open(f, "rb").read()
    s = raw.decode("utf-8")
    cr = raw.count(b"\r")
    bt = s.count("`")
    left, right = s.count("\u27e6"), s.count("\u27e7")
    guil = s.count("\u00ab"), s.count("\u00bb")
    notas = len(re.findall(r"Nota datada 2026-09-28", s))
    ok = (bt % 2 == 0) and (left == right) and (guil[0] == guil[1]) and (cr == 0)
    todo_ok = todo_ok and ok
    out.write("%-72s CR=%d backticks=%d(%s) \u27e6=%d \u27e7=%d \u00ab=%d \u00bb=%d notas_hoy=%d -> %s\n"
              % (f.split("Archives/")[1], cr, bt, "PAR" if bt % 2 == 0 else "IMPAR",
                 left, right, guil[0], guil[1], notas, "OK" if ok else "REVISION"))
out.write("\n== TOTAL: %s\n" % ("TODO OK" if todo_ok else "HAY ARCHIVOS A REVISAR"))
out.write("== Cada nota datada debe quedar dentro del par \u27e6\u2026\u27e7 y no partir una ruta: se comprueba\n")
out.write("   ademas que ninguna ruta de evidencia quede cortada por un salto de linea.\n\n")
for f in files:
    s = io.open(f, encoding="utf-8").read()
    broken = []
    for i, ln in enumerate(s.split("\n"), 1):
        for m in re.finditer(r"(\.opencode|evidence)/[^\s`\u27e6\u27e7]*[^\s`.,;:]", ln):
            tok = m.group(0)
            if tok.endswith("/"):
                broken.append((i, tok))
    out.write("%-72s rutas partidas al final de linea: %d %s\n"
              % (f.split("Archives/")[1], len(broken), broken[:3]))
out.close()
print("ok")
