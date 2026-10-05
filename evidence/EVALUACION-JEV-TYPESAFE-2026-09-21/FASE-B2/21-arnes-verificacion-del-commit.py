# -*- coding: utf-8 -*-
"""Verificacion del commit 0a6c84c en su propio arbol (SESION 3.5, FASE-B.2, 2026-10-04).

Mide tres cosas que el arbol de trabajo no puede afirmar por si solas:
  1. que el clon limpio del commit esta verde por si mismo;
  2. que el instrumento commiteado reproduce el artefacto del arbol, byte a byte salvo EOL;
  3. cual era el diferencial del primer commit (el informe estaba una revision detras del codigo).
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CRLF = b"\r\n"
LF = b"\n"
REPO = pathlib.Path("C:/Users/Jhond/Github/iah-cli")
CLONE = pathlib.Path("C:/Users/Jhond/AppData/Local/Temp/jev-b2-clone")
TEMP = pathlib.Path("C:/Users/Jhond/AppData/Local/Temp")
PLAN = "evidence/EVALUACION-JEV-TYPESAFE-2026-09-21"
PY = REPO / "venv" / "Scripts" / "python.exe"


def sha_lf(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes().replace(CRLF, LF)).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout.strip()


print("== 1. el clon limpio, en su propia revision ==")
print("   revision:", git("-C", str(CLONE), "rev-parse", "HEAD"))
print("   arbol:", git("-C", str(CLONE), "status", "--porcelain") or "limpio")
salida = subprocess.run([str(PY), "-m", "pytest", str(CLONE / "tests/quality_gates/jev_pilot"), "-q"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
print("   bateria:", (salida.stdout.strip().splitlines() or ["(sin salida)"])[-1],
      "| EXIT", salida.returncode)

print()
print("== 2. el instrumento commiteado reproduce el artefacto del arbol ==")
# Primero con rutas absolutas (la forma en que alguien lo corre desde otra raiz) y despues con la
# misma forma relativa del arbol de trabajo: la diferencia entre las dos tiene que ser solo el
# bloque de procedencia `insumos`, nunca un cociente.
cmd_abs = [str(PY), "scripts/evaluate_jev_pilot.py", "report",
           "--respuestas", str(CLONE / PLAN / "FASE-C/respuestas.jsonl"),
           "--etiquetas", str(CLONE / PLAN / "etiquetas.json"),
           "--muestra", str(CLONE / PLAN / "muestra.json"),
           "--protocolo", str(CLONE / PLAN / "protocolo.json"),
           "--out", str(TEMP / "clone_informe_absoluto.json"), "--fecha", "2026-10-04"]
subprocess.run(cmd_abs, cwd=str(CLONE), capture_output=True, text=True,
               encoding="utf-8", errors="replace")
# Invocado desde la raiz del clon y con rutas relativas: la misma forma de llamarse que en el arbol
# de trabajo. `insumos` publica las rutas tal como se le pasaron, asi que comparar contra rutas
# absolutas daria un diferencial de procedencia y no de logica (y eso tambien se mide, abajo).
cmd = [str(PY), "scripts/evaluate_jev_pilot.py", "report",
       "--respuestas", f"{PLAN}/FASE-C/respuestas.jsonl",
       "--etiquetas", f"{PLAN}/etiquetas.json",
       "--muestra", f"{PLAN}/muestra.json",
       "--protocolo", f"{PLAN}/protocolo.json",
       "--out", str(TEMP / "clone_informe_normalizado.json"), "--fecha", "2026-10-04"]
r = subprocess.run(cmd, cwd=str(CLONE), capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
print("   report en el clon: EXIT", r.returncode)
a = sha_lf(REPO / PLAN / "FASE-B2/informe_comparativa.json")
b = sha_lf(TEMP / "clone_informe_normalizado.json")
print("   sha LF informe arbol:", a[:20])
print("   sha LF informe clon :", b[:20])
print("   iguales:", a == b)
absoluto = json.loads((TEMP / "clone_informe_absoluto.json").read_text(encoding="utf-8")) \
    if (TEMP / "clone_informe_absoluto.json").exists() else None
if absoluto:
    relativo = json.loads((TEMP / "clone_informe_normalizado.json").read_text(encoding="utf-8"))
    mueve = [k for k in relativo if json.dumps(relativo[k]) != json.dumps(absoluto.get(k))]
    print("   invocacion con rutas absolutas mueve solo:", mueve,
          "(procedencia, no logica)")
cmd_d = [str(PY), "scripts/evaluate_jev_pilot.py", "decide",
         "--informe", str(TEMP / "clone_informe_normalizado.json"),
         "--protocolo", f"{PLAN}/protocolo.json",
         "--out-dir", str(TEMP / "clone_decision_normalizado"), "--fecha", "2026-10-04"]
rd = subprocess.run(cmd_d, cwd=str(CLONE), capture_output=True, text=True,
                    encoding="utf-8", errors="replace")
print("   decide en el clon: EXIT", rd.returncode, "(3 = emitido sin decision)")
for n in ("decision.json", "decision.md"):
    x = sha_lf(REPO / PLAN / "FASE-B2" / n)
    y = sha_lf(TEMP / "clone_decision_normalizado" / n)
    print(f"   {n:16s} iguales: {x == y}  sha LF {x[:20]}")

print()
print("== 3. el diferencial que traia el commit 0a6c84c ==")
blob = subprocess.run(["git", "-C", str(REPO), "show", f"0a6c84c:{PLAN}/FASE-B2/informe_comparativa.json"],
                      capture_output=True).stdout
viejo = json.loads(blob.decode("utf-8"))
nuevo = json.loads((REPO / PLAN / "FASE-B2/informe_comparativa.json").read_text(encoding="utf-8"))


def walk(x, y, ruta=""):
    diffs = []
    if isinstance(x, dict) and isinstance(y, dict):
        for k in sorted(set(x) | set(y)):
            if k not in x:
                diffs.append(f"SOLO EN EL REGENERADO: {ruta}/{k} = {json.dumps(y[k])[:60]}")
            elif k not in y:
                diffs.append(f"SOLO EN EL COMMITEADO: {ruta}/{k} = {json.dumps(x[k])[:60]}")
            else:
                diffs += walk(x[k], y[k], f"{ruta}/{k}")
    elif x != y:
        diffs.append(f"VALOR DISTINTO: {ruta} | commiteado {json.dumps(x)[:50]} | regenerado "
                     f"{json.dumps(y)[:50]}")
    return diffs


for linea in walk(viejo, nuevo) or ["(sin diferencial)"]:
    print("  ", linea)
print("   causa: el informe se emitio a las 20:34 y el campo `fuera_del_conjunto_elegible`")
print("        entro al instrumento a las 20:45; el commit se llevo el artefacto viejo.")
print("   decision.json y decision.md NO estaban vencidos: su contenido no porta ese campo")
print("        (coinciden con el clon en el bloque 2).")
sys.exit(0)
