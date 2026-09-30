#!/usr/bin/env python3
"""Re-mide el par del parte 19- (numerador/denominador) y lo que normalizan los patrones vigentes.

Solo lectura: no escribe en el arbol gobernado. Imprime por stdout.
Uso: python m-01-par-parte-19.py <raiz-del-repo>
"""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
PACKS = sorted((ROOT / ".opencode" / "plans" / "Archives" /
                "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20" / "briefing").glob("FASE-*.md"))

PATRONES = (
    ("p1 generado-prosa", re.compile(r"· generado `[0-9TZ:.+-]+`")),
    ("p2 generated_at-json", re.compile(r'"generated_at": "[0-9TZ:.+-]+"')),
    ("p3 HEAD-prosa", re.compile(r"HEAD `[0-9a-f]{7,40}`")),
    ("p4 head-json", re.compile(r'"head": "[0-9a-f]{7,}"')),
    ("p5 generado_por_sha-json", re.compile(r'"generado_por_sha": "[0-9a-f]{7,}"')),
)

por_patron = {}
tocadas4 = 0
tocadas5 = 0
total_lineas = 0
por_pack = []
for p in PACKS:
    lineas = p.read_text(encoding="utf-8", errors="replace").splitlines()
    total_lineas += len(lineas)
    t4 = sum(1 for l in lineas if any(rx.search(l) for _, rx in PATRONES[:4]))
    t5 = sum(1 for l in lineas if any(rx.search(l) for _, rx in PATRONES))
    tocadas4 += t4
    tocadas5 += t5
    por_pack.append((p.name, len(lineas), t4, t5))
    for nombre, rx in PATRONES:
        por_patron[nombre] = por_patron.get(nombre, 0) + sum(1 for l in lineas if rx.search(l))

print("=== packs medidos (nombre, lineas, tocadas-4, tocadas-5) ===")
for nombre, n, t4, t5 in por_pack:
    print(f"  {nombre}: {n} lineas, {t4} tocadas con los cuatro patrones, {t5} con los cinco")

print("=== por patron (lineas que casan, sumando los cinco packs) ===")
for nombre, _ in PATRONES:
    print(f"  {nombre}: {por_patron[nombre]}")

print("=== el par, como lo publica el parte 19- ===")
numerador = por_patron["p1 generado-prosa"] + por_patron["p2 generated_at-json"]
print(f"  numerador (lineas con sello UTC = p1 + p2) = {numerador}")
print(f"  denominador (lineas totales de los cinco packs) = {total_lineas}")
print(f"  lineas que normalizan los CUATRO patrones vigentes = {tocadas4}")
print(f"  lineas que normalizarian los CINCO = {tocadas5}")
print(f"  ratio numerador/denominador = {numerador / total_lineas * 100:.2f} %")

print("=== clave generado_por_sha: publicada en el meta o solo prosa ajena? ===")
for p in PACKS:
    texto = p.read_text(encoding="utf-8", errors="replace")
    en_meta = bool(re.search(r'^\s*"generado_por_sha":', texto, re.M))
    print(f"  {p.name}: clave_en_bloque_meta={'SI' if en_meta else 'NO'} "
          f"menciones_en_todo_el_pack={texto.count('generado_por_sha')}")
