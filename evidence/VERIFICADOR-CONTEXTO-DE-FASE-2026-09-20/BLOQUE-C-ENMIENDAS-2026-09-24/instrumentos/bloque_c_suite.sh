#!/bin/bash
# Suite acotada del bloque C (2026-09-24): instrumentos que consumen los contratos rectificados.
cd /c/Users/Jhond/Github/iah-cli || exit 9
export PYTHONIOENCODING=utf-8
LOG=evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/12-suite-acotada-final.txt
{
  echo "\$ ./venv/Scripts/python.exe -m pytest -q --no-header \
    tests/test_build_lesson_index.py \
    tests/test_validate_plan_citations.py \
    tests/test_validate_plan_closure.py \
    tests/test_validate_lesson_capitalization.py \
    tests/test_validate_document_integration.py \
    tests/quality_gates/governance_numbers/"
  echo "--- start $(date -u +%Y-%m-%dT%H:%M:%SZ) ---"
  ./venv/Scripts/python.exe -m pytest -q --no-header \
    tests/test_build_lesson_index.py \
    tests/test_validate_plan_citations.py \
    tests/test_validate_plan_closure.py \
    tests/test_validate_lesson_capitalization.py \
    tests/test_validate_document_integration.py \
    tests/quality_gates/governance_numbers/ 2>&1
  echo "EXIT=$?"
  echo "--- end $(date -u +%Y-%m-%dT%H:%M:%SZ) ---"
} > $LOG 2>&1
echo "PYTEST_DONE exit_captured_in_log"
