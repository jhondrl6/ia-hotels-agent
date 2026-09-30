#!/bin/sh
# T3 - las 82 funciones diferidas de las baterias de los verificadores de gobernanza.
# Poblacion medida con el metodo canonico de la casa (grep -cE '^\s*def test_' por archivo):
#   verify_packs 7 + verify_index 9 + lesson_index_s15 4 + lesson_capitalization 30
#   + validate_wiring 18 + registry_fecha_documental 14 = 82
# Un solo pytest, EXIT del proceso capturado sin tuberia.
D="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VEREDICTO-VCF-JEV-2026-09-29"
python -m pytest -q -ra \
  tests/test_verify_packs_in_committed_tree.py \
  tests/test_verify_index_in_committed_tree.py \
  tests/test_build_lesson_index_s15_fecha_versionada.py \
  tests/test_validate_lesson_capitalization.py \
  tests/test_validate_wiring.py \
  tests/test_registry_fecha_documental.py \
  > "$D/19-t3-pytest-82.txt" 2>&1
echo "EXIT_PYTEST=$?" >> "$D/19-t3-pytest-82.txt"
