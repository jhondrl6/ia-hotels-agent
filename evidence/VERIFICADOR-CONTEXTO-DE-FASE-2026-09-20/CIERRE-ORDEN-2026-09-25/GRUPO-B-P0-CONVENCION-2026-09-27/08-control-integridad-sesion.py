"""Control de integridad de lo escrito en esta tanda: P-0 (anotaciones) y D-b (config central).

Mide por archivo, contra su version en HEAD: paridad de marcadores ⟦/⟧, CR en disco, CJK,
palabras pegadas, paridad del DELTA de `**` y de backticks (no del total del libro, que ya es
impar por antecedentes) y citas numericas nuevas del patron que corta el gate de citas.
"""
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
CJK = re.compile(r"[\u3000-\u303f\u4e00-\u9fff\uff00-\uffef\u3040-\u30ff]")
PEGADAS = re.compile(r"[a-záéíóúñ]{3,}(?:[aeiouáéíóú][a-záéíóúñ]{2,}){1,}(?=[ ,.;:])")

PLAN = ".opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/"
RUTAS = [
    PLAN + "10-analisis-post-implementacion.md",
    PLAN + "dependencias-fases.md",
    PLAN + "00-lecciones-capitalizadas.md",
    ".opencode/context/ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md",
    ".agents/workflows/phased_project_executor.md",
    ".agents/workflows/templates/prompt-fase-template.md",
]

mal = 0
for ruta in RUTAS:
    t = pathlib.Path(ruta).read_text(encoding="utf-8")
    head = subprocess.run(
        ["git", "show", f"HEAD:{ruta}"], capture_output=True, text=True, encoding="utf-8"
    ).stdout
    abre, cier = t.count(O), t.count(C)
    h_abre, h_cier = head.count(O), head.count(C)
    citas_nuevas = sorted(set(CITACION.findall(t)) - set(CITACION.findall(head)))
    cjk = sorted(set(CJK.findall(t)))
    pegadas = sorted(set(m.group(0) for m in PEGADAS.finditer(t)
                         if m.group(0) not in head))
    delta_ast = t.count("**") - head.count("**")
    delta_bt = t.count("`") - head.count("`")
    cr_disco = "\r" in t
    cr_head = "\r" in head
    print(f"== {ruta}")
    print(f"   marcadores  disco abre={abre} cier={cier} delta={abre - cier}"
          f"   (HEAD delta={h_abre - h_cier})")
    print(f"   CR en disco = {'SI' if cr_disco else 'no'}   (HEAD: {'SI' if cr_head else 'no'})")
    print(f"   CJK = {len(cjk)} {cjk[:8]}")
    print(f"   delta ** = {delta_ast} (par={delta_ast % 2 == 0})"
          f"   delta backtick = {delta_bt} (par={delta_bt % 2 == 0})")
    print(f"   citas numericas nuevas: {citas_nuevas if citas_nuevas else 'NINGUNA'}")
    print(f"   palabras pegadas nuevas: {pegadas[:8] if pegadas else 'NINGUNA'}")
    corta = delta_ast % 2 or delta_bt % 2 or cr_disco or cjk or citas_nuevas
    if abre != cier and h_abre == h_cier:
        corta = True
    if corta:
        mal += 1
print(f"\n[{'REVISAR' if mal else 'OK'}] {mal} archivo(s) con alguna condicion de corte")
