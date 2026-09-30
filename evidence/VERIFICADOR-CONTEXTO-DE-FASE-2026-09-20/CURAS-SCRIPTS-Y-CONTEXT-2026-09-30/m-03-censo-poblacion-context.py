#!/usr/bin/env python3
"""Censo de la poblacion del verificador de frescura de CONTEXT (T3), ANTES de escribirlo.

Mide tres cosas por separado:
  1. los CONTEXT que autodeclaran una leccion durable (dos grafias: linea suelta y encabezado);
  2. los CONTEXT que cita cada plan archivado (10-analisis y 00-lecciones), resueltos contra disco;
  3. para cada miembro de la union, si existe una fuente publicada cuyo metadata.fileSha256 case
     (corroboracion barata; el criterio de la casa seguira siendo descarga + sha256).

Solo lectura. Uso: python m-03-censo-poblacion-context.py <listado-qmind.json>
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(".")
CONTEXT_DIR = ROOT / ".opencode" / "context"
ARCHIVES = ROOT / ".opencode" / "plans" / "Archives"

# Las dos grafias vivas: `Lección durable:` a inicio de linea (template) y como encabezado
# (forma que el CONTEXT de JEV escribe, medida 2026-09-27: el detector viejo la perdio).
MARCA_DURABLE = re.compile(r"(?m)^\s*(?:#{1,6}\s*)?Lecci[oó]n (?:durable|de forma)\s*:")
MARCA_CAPITALIZADAS = re.compile(r"(?m)^\s*(?:#{1,6}\s*)?Lecciones capitalizadas")
NOMBRE_CONTEXT = re.compile(r"CONTEXT-[A-Za-z0-9._-]+")

listado = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
fuentes = listado["sources"]
shas_publicados = {}
for f in fuentes:
    sha = (f.get("metadata") or {}).get("fileSha256")
    if sha:
        shas_publicados.setdefault(sha, []).append(f["id"])

declarados = []
for ruta in sorted(CONTEXT_DIR.glob("CONTEXT-*.md")):
    texto = ruta.read_text(encoding="utf-8", errors="replace")
    if MARCA_DURABLE.search(texto) or MARCA_CAPITALIZADAS.search(texto):
        declarados.append(ruta)

citados = set()
for plan in sorted(p for p in ARCHIVES.iterdir() if p.is_dir()):
    for nombre in ("10-analisis-post-implementacion.md", "00-lecciones-capitalizadas.md",
                   "dependencias-fases.md"):
        doc = plan / nombre
        if not doc.is_file():
            continue
        texto = doc.read_text(encoding="utf-8", errors="replace")
        for m in NOMBRE_CONTEXT.findall(texto):
            citados.add(m)

print("=== 1. CONTEXT autodeclarados (raiz de .opencode/context/, no recursivo) ===")
for ruta in declarados:
    print(f"  {ruta.name}")
print(f"  total declarados = {len(declarados)}")

print("=== 2. nombres CONTEXT-* citados por los planes archivados ===")
print(f"  distintos citados = {len(citados)}")
resueltos = []
for nombre in sorted(citados):
    candidatas = list(CONTEXT_DIR.rglob(f"{nombre}.md"))
    resueltos.append((nombre, candidatas))
    donde = ", ".join(str(c.relative_to(ROOT)).replace("\\", "/") for c in candidatas) or "AUSENTE-EN-DISCO"
    print(f"  {nombre} -> {donde}")

print("=== 3. union gobernada: sha en disco vs metadata.fileSha256 publicado ===")
gobernados = sorted({r.name: r for r in declarados}.values(), key=lambda p: p.name)
extra = []
for nombre, candidatas in resueltos:
    for c in candidatas:
        if c.name not in {g.name for g in gobernados}:
            extra.append(c)
for ruta in gobernados + sorted(set(extra), key=lambda p: p.name):
    sha = hashlib.sha256(ruta.read_bytes()).hexdigest()
    match = shas_publicados.get(sha, [])
    fuente = str(ruta.relative_to(ROOT)).replace("\\", "/")
    print(f"  {fuente}")
    print(f"     sha_disco={sha[:16]}…  tam={ruta.stat().st_size}  "
          f"fuentes_que_casan_por_metadata={len(match)} {match}")

print("=== 4. poblacion medida: raiz de context/ (sin Historico) ===")
solo_raiz = sorted(p.name for p in CONTEXT_DIR.glob("CONTEXT-*.md"))
print(f"  ficheros CONTEXT-* en raiz = {len(solo_raiz)}: {solo_raiz}")
print(f"  ficheros CONTEXT-* bajo Historico/ = {len(list((CONTEXT_DIR / 'Historico').rglob('CONTEXT-*.md')))}")
