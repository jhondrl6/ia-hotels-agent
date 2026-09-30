#!/bin/bash
# Instrumento m-13: pipeline de cierre, pasos 4 y 5 (quick, integracion documental, git diff --check y estado del arbol).
# Cada EXIT se captura sin tuberia.
E="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/REINGESTA-CONTEXT-JEV-2026-09-29"

python scripts/run_all_validations.py --quick > "$E/14a-quick.txt" 2>&1
Q=$?
python scripts/validate_document_integration.py > "$E/14b-integracion-documental.txt" 2>&1
D=$?
git diff --check > "$E/15a-git-diff-check.txt" 2>&1
G=$?
git status --porcelain > "$E/15b-status-porcelain.txt" 2>&1
S=$?
git status --porcelain -uno > "$E/15c-status-uno.txt" 2>&1
U=$?

{
  echo "fecha_pipeline=$(date +%F)  hora=$(date -Iseconds)"
  echo "== run_all_validations.py --quick =="
  echo "EXIT_QUICK=$Q"
  tail -25 "$E/14a-quick.txt"
  echo
  echo "== validate_document_integration.py =="
  echo "EXIT_DOC=$D"
  tail -20 "$E/14b-integracion-documental.txt"
  echo
  echo "== git diff --check =="
  echo "EXIT_DIFF_CHECK=$G"
  cat "$E/15a-git-diff-check.txt"
  echo "(vacio = sin espacios en blanco al final ni conflictos)"
  echo
  echo "== estado del arbol =="
  echo "EXIT_STATUS=$S  lineas_porcelain=$(wc -l < "$E/15b-status-porcelain.txt")"
  cat "$E/15b-status-porcelain.txt"
  echo "EXIT_STATUS_UNO=$U  lineas_uno=$(wc -l < "$E/15c-status-uno.txt")"
  cat "$E/15c-status-uno.txt"
  echo "(el -uno=0 dice que el arbol VERSIONADO esta limpio: lo unico pendiente es esta carpeta de evidencia)"
  echo
  echo "== archivos tocados por esta sesion =="
  git diff --numstat
  echo "EXIT_NUMSTAT=$?"
} > "$E/15-pipeline-paso4-5.txt" 2>&1
cat "$E/15-pipeline-paso4-5.txt"
