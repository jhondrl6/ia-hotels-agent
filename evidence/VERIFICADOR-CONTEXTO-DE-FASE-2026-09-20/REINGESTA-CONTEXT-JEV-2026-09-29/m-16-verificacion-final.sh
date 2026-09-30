#!/bin/bash
# Instrumento m-16: pasada final de verificacion, ya con el expediente corregido.
E="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/REINGESTA-CONTEXT-JEV-2026-09-29"

python "$E/m-15-rectifica-y-barrer.py" > "$E/21-self-control-final.txt" 2>&1
A=$?
git diff --check > "$E/22a-git-diff-check-final.txt" 2>&1
G=$?
git status --porcelain > "$E/22b-status-final.txt" 2>&1
S=$?
git rev-parse HEAD > "$E/22c-head-final.txt" 2>&1
H=$?

{
  echo "fecha_final=$(date +%F)  hora=$(date -Iseconds)"
  echo "== self-control del expediente y barrido de la carpeta =="
  echo "EXIT_SELF_CONTROL=$A"
  cat "$E/21-self-control-final.txt"
  echo
  echo "== git diff --check =="
  echo "EXIT=$G  lineas=$(wc -l < "$E/22a-git-diff-check-final.txt") (0 = vacio)"
  echo "== estado del arbol =="
  echo "EXIT_STATUS=$S  lineas_porcelain=$(wc -l < "$E/22b-status-final.txt")"
  cat "$E/22b-status-final.txt"
  echo "EXIT_HEAD=$H  head=$(cat "$E/22c-head-final.txt")"
  echo
  echo "== numstat de los dos archivos sellados =="
  git diff --numstat
  echo "EXIT_NUMSTAT=$?"
} > "$E/22-cierre-de-verificacion.txt" 2>&1
cat "$E/22-cierre-de-verificacion.txt"
