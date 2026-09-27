"""Cuenta simetrica de las dos formas de ruta: total de '.opencode/' menos las '/.opencode/'."""
import pathlib

raiz = pathlib.Path(".opencode")
total = 0
con_barra = 0
archivos = 0
for p in sorted(raiz.rglob("*.md")):
    t = p.read_text(encoding="utf-8", errors="replace")
    archivos += 1
    total += t.count(".opencode/")
    con_barra += t.count("/.opencode/")
print(f"archivos .md leidos            : {archivos}")
print(f"ocurrencias de '.opencode/'    : {total}")
print(f"  forma '/.opencode/' (minor.) : {con_barra}")
print(f"  forma '.opencode/' a secas   : {total - con_barra}")
