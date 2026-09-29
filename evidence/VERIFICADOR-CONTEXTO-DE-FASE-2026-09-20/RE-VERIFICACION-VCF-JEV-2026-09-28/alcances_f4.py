import io, subprocess, sys

DEST = sys.argv[1]
PATS = [("forma sin barra", "`" + ".opencode/plans/Archives"),
        ("forma con barra", "`" + "/.opencode/plans/Archives"),
        ("ancla ANCHA sin barra", "`" + ".opencode"),
        ("ancla ANCHA con barra", "`" + "/.opencode")]

def tracked_md():
    p = subprocess.run(["git", "ls-files", "-z"], stdout=subprocess.PIPE)
    return [x.decode() for x in p.stdout.split(b"\x00") if x and x.endswith(b".md")]

def tracked_all():
    p = subprocess.run(["git", "ls-files", "-z"], stdout=subprocess.PIPE)
    return [x.decode() for x in p.stdout.split(b"\x00") if x]

def untracked():
    p = subprocess.run(["git", "ls-files", "-z", "--others", "--exclude-standard"],
                       stdout=subprocess.PIPE)
    return [x.decode() for x in p.stdout.split(b"\x00") if x]

def count(pop):
    t = {k: 0 for k, _ in PATS}
    n_read = 0
    for f in pop:
        try:
            s = io.open(f, encoding="utf-8", errors="strict").read()
        except (UnicodeDecodeError, OSError):
            continue
        n_read += 1
        for label, pat in PATS:
            t[label] += s.count(pat)
    return t, n_read

out = io.open(DEST, "w", encoding="utf-8", newline="\n")
out.write("== F4: el par 518/66 de la fila S17 medido bajo los TRES alcances posibles\n")
out.write("== Patron: backtick + ruta, como pide la fila. Se cuentan OCURRENCIAS (str.count).\n")
out.write("== Poblacion: ficheros versionados por `git ls-files` (los dos primeros) y ademas los no\n")
out.write("   versionados por `git ls-files --others --exclude-standard` (el tercero).\n")
out.write("== Un archivo que no decodifica UTF-8 se omite y se declara en la columna leidos.\n\n")

md = tracked_md()
al = tracked_all()
ot = untracked()
for label, pop in [(".md versionados (el 'corpus marcado versionado' de la fila)", md),
                   ("todos los ficheros versionados (cualquier extension)", al),
                   ("versionados + no versionados (arbol de trabajo completo visible a git)", al + ot)]:
    t, n = count(pop)
    out.write("-- ALCANCE: %s\n" % label)
    out.write("   poblacion=%d  leidos=%d\n" % (len(pop), n))
    for lbl, _ in PATS:
        out.write("   %-24s %6d\n" % (lbl, t[lbl]))
    out.write("   PAR: %d contra %d    |    ANCHO: %d contra %d\n\n"
              % (t["forma sin barra"], t["forma con barra"],
                 t["ancla ANCHA sin barra"], t["ancla ANCHA con barra"]))

out.write("== Par declarado en la fila S17 (dependencias-fases.md:429): 518 contra 66\n")
out.write("== Par citado por la orden de esta sesion: 174 contra 32 (ancla del mandato) y\n")
out.write("   793 contra 77 (ancla ancha)\n")
out.close()
sys.stdout.write("OK\n")
