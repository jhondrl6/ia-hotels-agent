#!/bin/bash
# Instrumento m-06-sh: listado POST del notebook y su analisis (control anti-gemelo).
E="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/REINGESTA-CONTEXT-JEV-2026-09-29"
NB="01a04d98-b7bd-778c-8441-26fdc7e35f45"

qmind source list --nb "$NB" --all --format json > "$E/06-source-list-post.json" 2>"$E/06b-list-post-stderr.txt"
EXJ=$?
qmind source list --nb "$NB" --all > "$E/06c-list-post-tabla.txt" 2>"$E/06d-list-post-tabla-stderr.txt"
EXT=$?
{
  echo "fecha_post=$(date +%F)  hora=$(date -Iseconds)"
  echo "EXIT_LIST_JSON=$EXJ"
  echo "EXIT_LIST_TABLA=$EXT"
  echo "bytes_json=$(wc -c < "$E/06-source-list-post.json")"
  echo "tabla Total:"
  grep -n "^Total" "$E/06c-list-post-tabla.txt"
  echo "GREP_EXIT=$?"
  echo "stderr:"
  cat "$E/06b-list-post-stderr.txt" "$E/06d-list-post-tabla-stderr.txt"
  echo "== ANALISIS (m-06-post.py) =="
  python "$E/m-06-post.py"
  echo "PY_EXIT=$?"
} > "$E/06e-post-resumen.txt" 2>&1
cat "$E/06e-post-resumen.txt"
