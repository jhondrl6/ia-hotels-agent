"""Control de lo escrito en el grupo A: marcadores, CJK, CR, backticks, asteriscos y citas nuevas."""
import pathlib
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

O, C = chr(10214), chr(10215)
CITACION = re.compile(
    r"[A-Za-z0-9_\-./\\]+\.(?:py|md|yaml|yml|json|txt|html|csv|lock|toml|ini|sh|bat):"
    r"\d+(?:\s*[-–]\s*\d+)?"
)
CJK = re.compile(r"[\u3000-\u303f\u4e00-\u9fff\uff00-\uffef]")
PEGADAS = re.compile(r"[a-záéíóúñ]{2,}(?:[aeiouáéíóú][a-záéíóúñ]{2,}){1,}(?=[ ,.;:])")

RUTAS = [
    ".opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/dependencias-fases.md",
    ".opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/10-analisis-post-implementacion.md",
    ".opencode/context/ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md",
]

mal = 0
for ruta in RUTAS:
    t = pathlib.Path(ruta).read_text(encoding="utf-8")
    head = subprocess.run(
        ["git", "show", f"HEAD:{ruta}"], capture_output=True, text=True, encoding="utf-8"
    ).stdout
    abre, cier = t.count(O), t.count(C)
    citas_nuevas = sorted(set(CITACION.findall(t)) - set(CITACION.findall(head)))
    cjk = sorted(set(CJK.findall(t)))
    delta_ast = t.count("**") - head.count("**")
    delta_bt = t.count("`") - head.count("`")
    cr_disco = "\r" in t
    print(f"== {ruta}")
    print(f"   marcadores  abre={abre} cier={cier} delta={abre - cier}")
    print(f"   CR en disco = {'SI' if cr_disco else 'no'}")
    print(f"   CJK = {len(cjk)} {cjk[:6]}")
    print(f"   delta ** = {delta_ast} (par={delta_ast % 2 == 0})  delta backtick = {delta_bt} (par={delta_bt % 2 == 0})")
    print(f"   citas numericas nuevas: {citas_nuevas if citas_nuevas else 'NINGUNA'}")
    if abre != cier or cr_disco or cjk or delta_ast % 2 or delta_bt % 2 or citas_nuevas:
        mal += 1
print(f"\n[{'REVISAR' if mal else 'OK'}] {mal} archivo(s) con alguna condición de corte")
