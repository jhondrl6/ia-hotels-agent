import io, json, subprocess, hashlib, sys

DEST = "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VERIFICACION-VCF-JEV-2026-09-28/13-jev-ac3-verificabilidad-sha.txt"
out = io.open(DEST, "w", encoding="utf-8", newline="\n")

d = json.load(io.open("evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/muestra.json", encoding="utf-8"))
pairs = d["pairs"]
out.write("### AC3 del plan JEV: ¿son los originales rastreables por sha?\n\n")
out.write("-- muestra.json: status=%s  corpus_source=%s  pares=%d\n"
          % (d["status"], d["corpus_source"], len(pairs)))
out.write("-- review.human_reviewed=%s reviewer=%r reviewed_at=%r\n\n"
          % (d["review"]["human_reviewed"], d["review"]["reviewer"], d["review"]["reviewed_at"]))

wanted = {}
for p in pairs:
    wanted[p["original_sha256"]] = p["pair_id"]
    out.write("   par %s: original_sha256=%s sanitized_sha256=%s\n"
              % (p["pair_id"], p["original_sha256"], p["sanitized_sha256"]))
    out.write("      input_fragment (%d chars): %s\n"
              % (len(p["input_fragment"]), p["input_fragment"]))
out.write("\n-- sha del propio input_fragment guardado (por si el fragmento fuera el original)\n")
for p in pairs:
    h = hashlib.sha256(p["input_fragment"].encode("utf-8")).hexdigest()
    out.write("   %s  fragmento_sha=%s  ==original? %s  ==sanitized? %s\n"
              % (p["pair_id"], h[:16], h == p["original_sha256"], h == p["sanitized_sha256"]))

out.write("\n### ¿Existe ALGUN fichero versionado cuyo sha256 (bytes crudos del blob) case con un original_sha256?\n")
procs = subprocess.run(["git", "ls-files", "-z"], stdout=subprocess.PIPE)
files = [x.decode() for x in procs.stdout.split(b"\x00") if x]
out.write("-- poblacion: %d ficheros versionados\n" % len(files))
hits_blob = []
hits_worktree = []
for f in files:
    b = subprocess.run(["git", "cat-file", "blob", "HEAD:" + f], stdout=subprocess.PIPE).stdout
    if hashlib.sha256(b).hexdigest() in wanted:
        hits_blob.append((wanted[hashlib.sha256(b).hexdigest()], f))
    try:
        w = io.open(f, "rb").read()
    except OSError:
        continue
    if hashlib.sha256(w).hexdigest() in wanted:
        hits_worktree.append((wanted[hashlib.sha256(w).hexdigest()], f))
out.write("-- coincidencias sobre el BLOB de HEAD: %d %s\n" % (len(hits_blob), hits_blob))
out.write("-- coincidencias sobre los BYTES EN DISCO: %d %s\n" % (len(hits_worktree), hits_worktree))

out.write("\n### ¿Existe algun fichero de candidatos versionado (el insumo que AC3 pidiria)?\n")
r = subprocess.run(["git", "ls-files"], stdout=subprocess.PIPE)
cand = [x.decode() for x in r.stdout.split(b"\n") if "candidat" in x.decode().lower()]
out.write("-- rutas versionadas con 'candidat' en el nombre: %d %s\n" % (len(cand), cand))

out.write("\n### ¿Esta el texto original (pre-saneado) guardado en algun sitio versionado?\n")
frag = [p["input_fragment"] for p in pairs]
g = subprocess.run(["git", "grep", "-l", "-F", frag[0], "HEAD"], stdout=subprocess.PIPE)
out.write("-- busqueda literal del primer fragmento en HEAD: %d archivo(s)\n"
          % len([x for x in g.stdout.split(b"\n") if x]))
for x in [y.decode() for y in g.stdout.split(b"\n") if y][:5]:
    out.write("      %s\n" % x)

out.write("\n### Cláusula AC3 (texto íntegro, para no parafrasearla)\n")
t = io.open(".opencode/plans/Archives/EVALUACION-JEV-TYPESAFE-2026-09-21/01-plan-maestro.md",
            encoding="utf-8").read()
for ln in t.split("\n"):
    if ln.startswith("| AC3"):
        out.write("%s\n" % ln)
out.close()
sys.stdout.write("OK\n")
