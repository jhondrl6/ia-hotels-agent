#!/bin/bash
# Pasada de los comandos de §7 del mandato, en su orden literal y con el codigo de salida
# PROPIO de cada uno (no el de la cadena shell). PYTHONIOENCODING=utf-8 y el venv del proyecto.
export PYTHONIOENCODING=utf-8
cd "$(dirname "$0")/../../../.." || exit 9
D=evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-REMEDIACION-2026-09-24
PY=./venv/Scripts/python.exe

run() {
  echo "\$ $*"
  "$@"
  echo "EXIT=$?"
  echo
}

echo "### $(date -u +%FT%TZ)  HEAD=$(git rev-parse --short HEAD)"
echo "### 1) indice --check (PRE de la regeneracion)"
run $PY scripts/build_lesson_index.py --check
echo "### 2) regenerador unico del par indice (una sola vez, sobre el arbol final ya editado)"
run $PY scripts/build_lesson_index.py
echo "### 3) indice --check (POST)"
run $PY scripts/build_lesson_index.py --check
echo "### 4) validate_plan_citations"
run $PY scripts/validate_plan_citations.py
echo "### 5) validate_lesson_capitalization"
run $PY scripts/validate_lesson_capitalization.py
echo "### 6) validate_document_integration"
run $PY scripts/validate_document_integration.py
echo "### 7) validate_opencode_refs"
run $PY scripts/validate_opencode_refs.py
echo "### 8) validate_plan_closure"
run $PY scripts/validate_plan_closure.py
echo "### 9) validate_governance_numbers --report  (SIN destino: la unica forma permitida)"
run $PY scripts/validate_governance_numbers.py --report
echo "### 10) run_all_validations --quick --check"
run $PY scripts/run_all_validations.py --quick --check
echo "### 11) git diff --check"
run git diff --check
echo "### 12) suite acotada documental (las seis rutas que us6 C, sin la suite global)"
run $PY -m pytest -q --no-header \
  tests/test_build_lesson_index.py \
  tests/test_validate_plan_citations.py \
  tests/test_validate_plan_closure.py \
  tests/test_validate_lesson_capitalization.py \
  tests/test_validate_document_integration.py \
  tests/quality_gates/governance_numbers/
echo "### fin"
