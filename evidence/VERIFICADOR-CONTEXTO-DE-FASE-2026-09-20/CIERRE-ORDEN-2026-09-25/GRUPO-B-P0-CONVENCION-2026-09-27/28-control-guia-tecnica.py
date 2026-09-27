"""Medicion de la anotacion en docs/GUIA_TECNICA.md, contra su version en HEAD.

Se escribe como archivo y no como `python -c`: el texto medido lleva backticks, y dentro de la
comilla doble de la shell se convierten en sustitucion de comando (medido: un "delta de backticks"
absurdo de 204785 en la corrida anterior).
"""
import pathlib
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RUTA = "docs/GUIA_TECNICA.md"
O, C = chr(10214), chr(10215)
CITACION = re.compile(
    r"[A-Za-z0-9_\-./\\]+\.(?:py|md|yaml|yml|json|txt|html|csv|lock|toml|ini|sh|bat):"
    r"\d+(?:\s*[-–]\s*\d+)?"
)
CJK = re.compile(r"[\u3000-\u303f\u4e00-\u9fff\uff00-\uffef\u3040-\u30ff]")

ruta = pathlib.Path(RUTA)
bytes_disco = ruta.read_bytes()
t = bytes_disco.decode("utf-8")
head = subprocess.run(
    ["git", "show", f"HEAD:{RUTA}"], capture_output=True, text=True, encoding="utf-8"
).stdout

print(f"archivo: {RUTA}")
print(f"  bytes={len(bytes_disco)}  lineas={t.count(chr(10))}  (HEAD lineas={head.count(chr(10))})")
print(f"  CR en disco = {'SI' if chr(13) in t else 'no'}   (HEAD: {'SI' if chr(13) in head else 'no'})")
print(f"  CJK  HEAD={len(CJK.findall(head))}  disco={len(CJK.findall(t))}  "
      f"nuevos={sorted(set(CJK.findall(t)) - set(CJK.findall(head))) or 'NINGUNO'}")
print(f"  marcadores  abre={t.count(O)} cier={t.count(C)} delta={t.count(O) - t.count(C)}"
      f"   (HEAD {head.count(O)}/{head.count(C)})")
d_ast = t.count("**") - head.count("**")
d_bt = t.count("`") - head.count("`")
print(f"  delta ** = {d_ast} (par={d_ast % 2 == 0})   delta backtick = {d_bt} (par={d_bt % 2 == 0})")
nuevas = sorted(set(CITACION.findall(t)) - set(CITACION.findall(head)))
print(f"  citas numericas nuevas: {nuevas or 'NINGUNA'}")

mal = (
    ("SI" if chr(13) in t else "no") != "no"
    or bool(set(CJK.findall(t)) - set(CJK.findall(head)))
    or t.count(O) != t.count(C)
    or d_ast % 2
    or d_bt % 2
    or bool(nuevas)
)
print(f"\n[{'REVISAR' if mal else 'OK'}] condicion de corte")
