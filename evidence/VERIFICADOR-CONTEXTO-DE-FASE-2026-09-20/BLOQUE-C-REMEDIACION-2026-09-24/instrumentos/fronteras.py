"""Comprobaciones de fronteras (§3 del mandato), ejecutadas sobre los artefactos de esta sesion.

Dos cosas que hay que medir y no afirmar:
  1. que `validate_governance_numbers.py` se invoco **sin destino** (la unica forma permitida),
     distinguiendo la linea de comando real de los comentarios y del texto que el propio informe imprime;
  2. que ninguna instruccion de esta sesion toco red, con **control positivo** sobre un archivo que si
     menciona una URL y un `--upload` (un patron que no casa nada tambien daria "cero").
"""
import glob
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[4]
D = ROOT / "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-REMEDIACION-2026-09-24"

print("=== 1) lineas de comando REALES del report (prefijo '$ ' de la pasada) ===")
for ln in (D / "04-validaciones.txt").read_text(encoding="utf-8").splitlines():
    if ln.startswith("$ ") and "governance_numbers.py" in ln:
        print(f"  {ln!r}")
        print(f"  termina en '--report' sin argumento detras: {ln.rstrip().endswith('--report')}")
print("  y en el generador del script:")
for ln in (D / "instrumentos/pasada_siete.sh").read_text(encoding="utf-8").splitlines():
    if "governance_numbers" in ln and ln.lstrip().startswith("run"):
        print(f"    {ln.strip()!r}")

print()
print("=== 2) el propio informe declara que no escribio (S12) ===")
txt = (D / "04-validaciones.txt").read_text(encoding="utf-8")
for m in re.finditer(r"[^\n]*no se escribi[oó] ning[uú]n archivo[^\n]*", txt):
    print("  " + m.group(0).strip()[:160])

print()
print("=== 3) flags que ESCRIBEN, buscados solo en lineas de comando ejecutadas ===")
comandos = [ln for ln in txt.splitlines() if ln.startswith("$ ")]
vetados = ["--fix", "--update-baseline", "--write-baseline"]
for v in vetados + ["--report <destino>"]:
    if v.startswith("--report"):
        hits = [c for c in comandos if "--report" in c and not c.rstrip().endswith("--report")]
    else:
        hits = [c for c in comandos if v in c]
    print(f"  {v:<20} usos en comandos ejecutados: {len(hits)} {hits[:2]}")
rara = [c for c in comandos if "run_all_validations" in c
        and not re.search(r"--quick --check\s*$", c.rstrip())]
print(f"  run_all_validations con flags distintos de --quick --check: {len(rara)} {rara}")
gen = [c for c in comandos if "scripts/build_lesson_index.py" in c and "--check" not in c]
print(f"  build_lesson_index.py SIN --check (el escritor autorizado, debe ser 1): {len(gen)}")
print(f"    {gen}")
print("    (ojo: 'build_lesson_index.py' a secas tambien casa la RUTA DE TEST de pytest; se exige el")
print("     prefijo 'scripts/' para contar solo la ejecucion del generador)")

print()
print("=== 4) red, con control positivo ===")
pat = re.compile(r"https?://|--upload|fetch_source_titles|urllib\.request|requests\.get|requests\.post")
rutas = sorted(glob.glob(str(D / "instrumentos" / "*"))) + sorted(glob.glob(str(D / "[0-9][0-9]-*")))
total = 0
for a in rutas:
    try:
        t = Path(a).read_text(encoding="utf-8", errors="replace")
    except OSError:
        continue
    h = sorted(set(pat.findall(t)))
    if h:
        print(f"    {Path(a).name}: {h}")
        total += len(h)
print(f"  coincidencias en los {len(rutas)} artefactos de esta sesion: {total}")
ctrl = sorted(set(pat.findall(
    (ROOT / ".opencode/plans/EVALUACION-JEV-TYPESAFE-2026-09-21/01-plan-maestro.md")
    .read_text(encoding="utf-8"))))
print(f"  CONTROL POSITIVO (archivo que si menciona API y subidas): {ctrl}")
