#!/bin/bash
# Instrumento m-18: pasada final de los cuatro controles, sobre el expediente ya terminado.
E="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/REINGESTA-CONTEXT-JEV-2026-09-29"

python "$E/m-15-rectifica-y-barrer.py" > "$E/27a-barrido-final.txt" 2>&1
A=$?
python "$E/m-17-citas-del-expediente.py" > "$E/27b-citas-final.txt" 2>&1
B=$?
python "$E/m-08-controles-sellos.py" > "$E/27c-sellos-final.txt" 2>&1
C=$?
git diff --check > "$E/27d-diff-check.txt" 2>&1
D=$?
git status --porcelain > "$E/27e-status.txt" 2>&1
F=$?
git rev-parse HEAD > "$E/27f-head.txt" 2>&1
G=$?

{
  echo "fecha_cierre_definitivo=$(date +%F)  hora=$(date -Iseconds)"
  echo "EXIT_BARRIDO=$A  EXIT_CITAS=$B  EXIT_SELLOS=$C  EXIT_DIFF=$D  EXIT_STATUS=$F  EXIT_HEAD=$G"
  echo
  echo "== 1. barrido y self-control =="
  tail -6 "$E/27a-barrido-final.txt"
  echo
  echo "== 2. citas del expediente =="
  grep -E "citados_sin_archivo|crudos_reales_sin_nombrar|citas_rotas|marcadores=|CR=" "$E/27b-citas-final.txt"
  echo
  echo "== 3. sellos: lo que importa de los dos archivos =="
  grep -E "^== |numstat=|delta=|marcadores_crudo|marcadores_sin_inline|CR_head|CJK_head" "$E/27c-sellos-final.txt"
  echo
  echo "== 4. arbol =="
  echo "lineas_diff_check=$(wc -l < "$E/27d-diff-check.txt")"
  echo "lineas_status=$(wc -l < "$E/27e-status.txt")"
  cat "$E/27e-status.txt"
  echo "HEAD=$(cat "$E/27f-head.txt")"
} > "$E/27-pasada-final.txt" 2>&1
cat "$E/27-pasada-final.txt"
