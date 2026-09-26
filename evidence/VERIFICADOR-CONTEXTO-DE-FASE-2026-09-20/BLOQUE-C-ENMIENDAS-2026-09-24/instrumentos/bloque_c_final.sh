#!/bin/bash
# Pasada FINAL del bloque C (2026-09-24), tras la última edición relevante.
cd /c/Users/Jhond/Github/iah-cli || exit 9
export PYTHONIOENCODING=utf-8
PY=./venv/Scripts/python.exe
LOG=evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/11-verificacion-definitiva.txt

{
  echo "### \$ $PY scripts/build_lesson_index.py --check   (antes de regenerar, con la orden ya editada)"
  $PY scripts/build_lesson_index.py --check 2>&1; echo "EXIT=$?"; echo
  echo "### \$ $PY scripts/build_lesson_index.py   (regeneración autorizada: único escritor de la pareja)"
  $PY scripts/build_lesson_index.py 2>&1; echo "EXIT=$?"; echo
  echo "### \$ $PY scripts/build_lesson_index.py --check   (después)"
  $PY scripts/build_lesson_index.py --check 2>&1; echo "EXIT=$?"; echo
  echo "### \$ git diff --numstat de la pareja"
  git diff --numstat .opencode/LECCIONES-INDEX.md .opencode/lecciones_index.json; echo
  for s in validate_plan_citations validate_lesson_capitalization validate_document_integration validate_opencode_refs validate_plan_closure; do
    echo "### \$ $PY scripts/$s.py"
    $PY scripts/$s.py 2>&1; echo "EXIT=$?"; echo
  done
  echo "### \$ $PY scripts/validate_governance_numbers.py --report   (sin destino: no escribe, S12)"
  $PY scripts/validate_governance_numbers.py --report > evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/09-gobierno-final.txt 2>&1; echo "EXIT=$?"
  echo "(stdout completo en evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/09-gobierno-final.txt; aquí solo las 8 últimas líneas)"
  tail -8 evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/09-gobierno-final.txt; echo
  echo "### \$ $PY scripts/run_all_validations.py --quick --check"
  $PY scripts/run_all_validations.py --quick --check > evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/10-quick-final.txt 2>&1; echo "EXIT=$?"
  echo "(stdout completo en evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/10-quick-final.txt; aquí solo el resumen final)"
  tail -22 evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/10-quick-final.txt; echo
  echo "### \$ git diff --check"
  git diff --check 2>&1; echo "EXIT=$?"; echo
  echo "### \$ git status --porcelain   (final)"
  git status --porcelain 2>&1 | grep -v "^ M" ; echo "(solo rutas no-M: vacío = sin altas ni bajas propias)"
  echo "### fin"
} > $LOG 2>&1
echo "EXIT_SCRIPT=$?"
