#!/bin/bash
# Pasada POST-regeneración del bloque C (2026-09-24). Solo lectura.
cd /c/Users/Jhond/Github/iah-cli || exit 9
export PYTHONIOENCODING=utf-8
PY=./venv/Scripts/python.exe

run() {
  echo "=============================================================="
  echo "\$ $*"
  echo "--- start $(date -u +%Y-%m-%dT%H:%M:%SZ) ---"
  "$@" 2>&1
  echo "EXIT=$?"
}

run $PY scripts/build_lesson_index.py --check
run $PY scripts/validate_plan_citations.py
run $PY scripts/validate_lesson_capitalization.py --quiet
run $PY scripts/validate_document_integration.py
run $PY scripts/validate_opencode_refs.py
run $PY scripts/validate_governance_numbers.py --report
run $PY scripts/run_all_validations.py --quick --check
echo "=============================================================="
echo "\$ git diff --check"
git diff --check 2>&1
echo "EXIT=$?"
echo "### script finished"
