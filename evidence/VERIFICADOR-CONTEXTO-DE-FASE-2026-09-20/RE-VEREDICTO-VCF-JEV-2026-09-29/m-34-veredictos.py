import io
import json
import os
import sys

D = sys.argv[1]
VCF = ".opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"
JEV = ".opencode/plans/Archives/EVALUACION-JEV-TYPESAFE-2026-09-21"
FC = "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C"

L = []
L.append("### Veredictos heredados, leidos HOY de su fuente (no transcritos del expediente del 2026-09-28)")
L.append("")
L.append("== 1. Fila ⟦E1⟧ / AC12 de `%s/criterios-de-completitud.md`" % (FC + ""))
texto = io.open(os.path.join(FC, "criterios-de-completitud.md"), encoding="utf-8").read()
for i, ln in enumerate(texto.split("\n"), 1):
    if ln.startswith("| ⟦E1⟧") or "AC12" in ln and ln.startswith("|"):
        celdas = [c.strip() for c in ln.strip().strip("|").split("|")]
        L.append("   linea %d, celdas=%d" % (i, len(celdas)))
        for j, c in enumerate(celdas, 1):
            L.append("   [%d] %s" % (j, c[:400]))
        L.append("")
L.append("== 2. Fila AC14 (guard de no-filtrado: verde y rojo del mutante)")
for i, ln in enumerate(texto.split("\n"), 1):
    if "AC14" in ln:
        celdas = [c.strip() for c in ln.strip().strip("|").split("|")]
        L.append("   linea %d, celdas=%d" % (i, len(celdas)))
        for j, c in enumerate(celdas, 1):
            L.append("   [%d] %s" % (j, c[:520]))
        L.append("")
L.append("== 3. Artefactos que sostienen AC14, medidos en disco")
for nombre in ["mutation/verde_baseline.json", "mutation/mutante_M-AC10-guard-aditividad.json",
               "mutation/resumen.txt", "mutation/corrida.txt"]:
    p = os.path.join(FC, nombre)
    if not os.path.exists(p):
        L.append("   %-58s AUSENTE" % nombre)
        continue
    b = io.open(p, encoding="utf-8", errors="replace").read()
    L.append("   %-58s %d bytes" % (nombre, len(b.encode("utf-8"))))
    if nombre.endswith(".json"):
        try:
            dd = json.loads(b)
            L.append("      claves: %s" % ", ".join(sorted(dd.keys())[:12]))
            for k in ("antes", "despues", "removed", "total_antes", "total_despues", "corte", "simbolo"):
                if k in dd:
                    v = dd[k]
                    if isinstance(v, list):
                        v = "%d elementos" % len(v)
                    L.append("      %s = %s" % (k, str(v)[:180]))
        except ValueError as e:
            L.append("      no parseable: %s" % e)
L.append("")
L.append("== 4. coverage.json: aceptacion (AC15) y su motivo")
cov = json.load(io.open(os.path.join(FC, "coverage.json"), encoding="utf-8"))
L.append("   aceptacion = %s" % json.dumps(cov.get("aceptacion"), ensure_ascii=False)[:700])
L.append("   umbral     = %s" % json.dumps(cov.get("umbral"), ensure_ascii=False)[:300])
L.append("")
L.append("== 5. JEV README: estados de FASE-B / FASE-C / FASE-RELEASE (regla 1.c)")
jevr = io.open(os.path.join(JEV, "README.md"), encoding="utf-8").read()
for i, ln in enumerate(jevr.split("\n"), 1):
    if any(t in ln for t in ("FASE-B", "FASE-C", "FASE-RELEASE")) and ln.strip().startswith("|"):
        L.append("   linea %d: %s" % (i, ln.strip()[:260]))
L.append("")
L.append("== 6. JEV AC3: su clausula intacta en el maestro del plan")
m = io.open(os.path.join(JEV, "01-plan-maestro.md"), encoding="utf-8").read()
for ln in m.split("\n"):
    if ln.startswith("| AC3"):
        L.append("   %s" % ln.strip()[:600])
L.append("")
L.append("== 7. Regla 1.b del plan VCF: que afirma y donde vive")
pm = io.open(os.path.join(VCF, "01-plan-maestro.md"), encoding="utf-8").read()
for i, ln in enumerate(pm.split("\n"), 1):
    if "1.b" in ln or "1.a" in ln:
        L.append("   linea %d: %s" % (i, " ".join(ln.split())[:240]))

con = io.open(os.path.join(D, "34-veredictos-ac-re-leidos.txt"), "w", encoding="utf-8", newline="\n")
con.write("\n".join(L) + "\n")
con.close()
sys.stdout.write("OK 34-veredictos-ac-re-leidos.txt\n")
