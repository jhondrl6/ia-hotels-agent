"""Balance medido para el expediente: suma de la tabla de cobertura y anotaciones nuevas."""
import pathlib
import re
import subprocess

O = chr(10214)

t = pathlib.Path("AGENTS.md").read_text(encoding="utf-8")
filas = re.findall(r"^\|\s*([^|]+?)\s*\|\s*([\d.]+)\s*\|\s*[^|]*tests/", t, re.M)
suma = sum(int(v.replace(".", "")) for _, v in filas)
print(f"tabla de cobertura: {len(filas)} filas, suma = {suma}")

RUTAS = [
    ".opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/dependencias-fases.md",
    ".opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/10-analisis-post-implementacion.md",
    ".opencode/context/ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md",
]
total = 0
for r in RUTAS:
    h = subprocess.run(["git", "show", f"HEAD:{r}"], capture_output=True, text=True,
                       encoding="utf-8").stdout.count(O)
    d = pathlib.Path(r).read_text(encoding="utf-8").count(O)
    total += d - h
    print(f"{r.split('/')[-1]:44} HEAD={h:3} disco={d:3} anotaciones_nuevas={d - h}")
print(f"TOTAL anotaciones del grupo A: {total}")
