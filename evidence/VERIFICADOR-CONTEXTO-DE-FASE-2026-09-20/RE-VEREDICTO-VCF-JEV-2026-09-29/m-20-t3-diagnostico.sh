#!/bin/sh
# T3-diagnostico: el unico rojo de la bateria se reproduce en AISLADO y se atribuye por medicion,
# no por memoria. Hipotesis heredada: contaminacion tmp_test/venv-jev-sdk (declarada en el baseline
# de la casa como uno de los tres rojos preexistentes).
D="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VEREDICTO-VCF-JEV-2026-09-29"

echo "### 1. Poblacion de la corrida T3 (19-t3-pytest-82.txt)" > "$D/20-t3-diagnostico.txt"
tail -3 "$D/19-t3-pytest-82.txt" >> "$D/20-t3-diagnostico.txt"

echo >> "$D/20-t3-diagnostico.txt"
echo "### 2. El archivo completo, en AISLADO (18 funciones de test_validate_wiring.py)" >> "$D/20-t3-diagnostico.txt"
python -m pytest -q -ra tests/test_validate_wiring.py > "$D/20b-aislado-wiring.txt" 2>&1
echo "EXIT_AISLADO_WIRING=$?" >> "$D/20b-aislado-wiring.txt"
tail -6 "$D/20b-aislado-wiring.txt" >> "$D/20-t3-diagnostico.txt"

echo >> "$D/20-t3-diagnostico.txt"
echo "### 3. Solo el test que cae, en AISLADO" >> "$D/20-t3-diagnostico.txt"
python -m pytest -q -ra "tests/test_validate_wiring.py::test_toda_la_poblacion_no_resuelta_queda_fuera_de_produccion" \
  > "$D/20c-aislado-un-test.txt" 2>&1
echo "EXIT_AISLADO_UN_TEST=$?" >> "$D/20c-aislado-un-test.txt"
tail -6 "$D/20c-aislado-un-test.txt" >> "$D/20-t3-diagnostico.txt"

echo >> "$D/20-t3-diagnostico.txt"
echo "### 4. Estado versionado del insumo que ensucia (tmp_test/)" >> "$D/20-t3-diagnostico.txt"
git ls-files tmp_test | wc -l >> "$D/20-t3-diagnostico.txt"
echo "  ^ rutas versionadas bajo tmp_test (0 = no esta en el arbol de git)" >> "$D/20-t3-diagnostico.txt"
git check-ignore -v tmp_test 2>&1 | head -3 >> "$D/20-t3-diagnostico.txt"
echo "  ^ salida de git check-ignore (vacio = NO ignorado por .gitignore)" >> "$D/20-t3-diagnostico.txt"
ls -d tmp_test/venv-jev-sdk 2>&1 >> "$D/20-t3-diagnostico.txt"
echo "### 5. Los 5 receptores no resueltos, leidos del propio reporte" >> "$D/20-t3-diagnostico.txt"
python "$D/m-20-receptores.py" >> "$D/20-t3-diagnostico.txt" 2>&1
echo "EXIT_RECEPTORES=$?" >> "$D/20-t3-diagnostico.txt"
echo "### 6. Que los tres rojos preexistentes de la casa son los mismos nombres" >> "$D/20-t3-diagnostico.txt"
grep -n "test_function_default_flags\|test_diagnostic_includes_geo_metrics\|test_toda_la_poblacion_no_resuelta" \
  evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/CURAS-FUERA-DE-PLANS-2026-09-27/*.txt 2>/dev/null | head -8 >> "$D/20-t3-diagnostico.txt"
echo "HECHO" >> "$D/20-t3-diagnostico.txt"
