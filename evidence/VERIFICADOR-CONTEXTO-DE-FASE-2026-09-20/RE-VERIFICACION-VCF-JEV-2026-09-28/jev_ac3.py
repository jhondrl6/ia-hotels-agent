import io, json, subprocess, sys

DEST = "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VERIFICACION-VCF-JEV-2026-09-28/12-jev-ac3-muestra.txt"
out = io.open(DEST, "w", encoding="utf-8", newline="\n")

out.write("### JEV AC3: rastro de sha en la muestra versionada\n\n")
for f in ["evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/muestra.json",
          "evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/etiquetas.json",
          "evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/protocolo.json",
          "evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-A/muestra_check.json"]:
    out.write("-- %s\n" % f)
    p = subprocess.run(["git", "ls-files", "-z", "--", f], stdout=subprocess.PIPE)
    versionado = bool(p.stdout.strip())
    out.write("   versionado en HEAD: %s\n" % ("SI" if versionado else "NO"))
    try:
        d = json.load(io.open(f, encoding="utf-8"))
    except Exception as exc:
        out.write("   lectura: ERROR %s\n\n" % exc)
        continue
    if isinstance(d, dict):
        keys = sorted(d.keys())
    elif isinstance(d, list):
        keys = sorted({k for item in d if isinstance(item, dict) for k in item.keys()})
    else:
        keys = []
    out.write("   claves: %s\n" % keys)
    flat = json.dumps(d, ensure_ascii=False)
    for token in ["sha", "sha256", "original_sha256", "fuente", "ruta_original"]:
        out.write("   menciones de %r en el JSON: %d\n" % (token, flat.count(token)))
    n = len(d) if isinstance(d, list) else len(d.get("pares", d)) if isinstance(d, dict) else 0
    out.write("   elementos de primer nivel: %d\n\n" % n)

out.write("### Busqueda del token original_sha256 en todo el repo versionado\n")
r = subprocess.run(["git", "grep", "-c", "-F", "original_sha256", "HEAD"],
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
hits = r.stdout.decode("utf-8", "replace").splitlines()
out.write("   archivos con >=1 linea que lo contienen: %d\n" % len(hits))
for h in hits[:20]:
    out.write("   %s\n" % h)
if not hits:
    out.write("   (sin coincidencias en todo HEAD)\n")

out.write("\n### Que exige AC3 (texto integro de la clausula)\n")
t = io.open(".opencode/plans/Archives/EVALUACION-JEV-TYPESAFE-2026-09-21/01-plan-maestro.md",
            encoding="utf-8").read()
for ln in t.split("\n"):
    if ln.startswith("| AC3"):
        out.write("   %s\n" % ln)

out.write("\n### Estado declarado de la muestra (BORRADOR) en el manifiesto/etiquetas\n")
for f in ["evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/etiquetas.json"]:
    try:
        d = json.load(io.open(f, encoding="utf-8"))
        s = json.dumps(d, ensure_ascii=False)[:1200]
        out.write("   %s -> %s\n" % (f, s))
    except Exception as exc:
        out.write("   %s -> ERROR %s\n" % (f, exc))
out.close()
sys.stdout.write("OK %s\n" % DEST)
