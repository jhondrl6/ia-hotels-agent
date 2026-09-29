import subprocess, sys, io

DEST = sys.argv[1]

PATTERNS = [
    ("ancla-del-mandato / forma sin barra", "`" + ".opencode/plans/Archives"),
    ("ancla-del-mandato / forma con barra", "`" + "/.opencode/plans/Archives"),
    ("ancla-ancha / forma sin barra", "`" + ".opencode"),
    ("ancla-ancha / forma con barra", "`" + "/.opencode"),
]

out = io.open(DEST, "w", encoding="utf-8", newline="\n")
out.write("== F4: reproduccion del par 518/66 que afirma la fila S17 (.opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/dependencias-fases.md:429)\n")
out.write("== Corpus: archivos .md versionados (git ls-files). Poblacion leida del arbol de trabajo,\n")
out.write("   que esta limpio (git status --porcelain = 0 lineas, medido en el crudo 05) y con\n")
out.write("   core.autocrlf=input, asi que disco == HEAD en contenido salvo finales de linea.\n")
out.write("== Patron: el backtick forma parte del literal, como pide la fila. Se cuentan OCURRENCIAS\n")
out.write("   (str.count), no lineas, porque git grep -c cuenta lineas y esa es una de las razones por\n")
out.write("   las que el par no reproduce.\n")
out.write("== Instrumento alternativo (rechazado por la casa, ver S17 quinta instancia): git grep -F con\n")
out.write("   patron que empieza por '/' devuelve 0 falso. Aqui se contrasta igual y se imprime.\n\n")

proc = subprocess.run(["git", "ls-files", "-z"], stdout=subprocess.PIPE)
paths = [p.decode("utf-8") for p in proc.stdout.split(b"\x00") if p]
md = [p for p in paths if p.endswith(".md")]
out.write("== num archivos .md versionados: %d\n\n" % len(md))

totals = {}
for label, pat in PATTERNS:
    per_file = {}
    for p in md:
        with io.open(p, "r", encoding="utf-8", errors="strict") as fh:
            t = fh.read()
        c = t.count(pat)
        if c:
            per_file[p] = c
    totals[label] = sum(per_file.values())
    out.write("-- %s\n   patron literal: %r\n   TOTAL ocurrencias: %d   (archivos con >=1 ocurrencia: %d)\n"
              % (label, pat, totals[label], len(per_file)))
    for p in sorted(per_file, key=lambda k: -per_file[k])[:6]:
        out.write("      %5d  %s\n" % (per_file[p], p))
    out.write("\n")

sinb = totals["ancla-del-mandato / forma sin barra"]
conb = totals["ancla-del-mandato / forma con barra"]
w1 = totals["ancla-ancha / forma sin barra"]
w2 = totals["ancla-ancha / forma con barra"]
out.write("== PARES RE-MEDIDOS HOY\n")
out.write("ancla del mandato (`.opencode/plans/Archives): %d contra %d\n" % (sinb, conb))
out.write("ancla ancha       (`.opencode):                %d contra %d\n" % (w1, w2))
out.write("par declarado en la fila S17:                  518 contra 66\n")
out.write("REPRODUCIBLE con alguna de las dos anclas: %s\n"
          % ("SI" if (sinb, conb) == (518, 66) or (w1, w2) == (518, 66) else "NO"))
out.close()
sys.stdout.write("MANDATO=%d/%d ANCHA=%d/%d DECLARADO=518/66 MD=%d\n" % (sinb, conb, w1, w2, len(md)))
