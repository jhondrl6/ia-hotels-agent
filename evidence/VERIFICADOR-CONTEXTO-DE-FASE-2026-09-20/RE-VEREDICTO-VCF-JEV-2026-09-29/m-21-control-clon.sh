#!/bin/sh
# Control de atribucion: el rojo de test_validate_wiring existe solo en ESTE arbol de trabajo
# porque tmp_test/ esta ignorado por git. Se prueba corriendo el mismo test sobre un clon fiel
# de HEAD, con la receta documentada de la casa (--no-checkout y core.autocrlf=input DENTRO del clon).
D="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VEREDICTO-VCF-JEV-2026-09-29"
CLON="/tmp/clon-control-wiring-$$"
echo "### clon de control en $CLON" > "$D/21-control-clon-wiring.txt"
git clone --no-checkout --quiet "$PWD" "$CLON" >> "$D/21-control-clon-wiring.txt" 2>&1
echo "EXIT_CLONE=$?" >> "$D/21-control-clon-wiring.txt"
git -C "$CLON" config core.longpaths true >> "$D/21-control-clon-wiring.txt" 2>&1
git -C "$CLON" config core.autocrlf input >> "$D/21-control-clon-wiring.txt" 2>&1
git -C "$CLON" checkout --quiet master >> "$D/21-control-clon-wiring.txt" 2>&1
echo "EXIT_CHECKOUT=$?" >> "$D/21-control-clon-wiring.txt"

echo "### HEAD del clon vs HEAD del arbol de trabajo" >> "$D/21-control-clon-wiring.txt"
git -C "$CLON" rev-parse HEAD >> "$D/21-control-clon-wiring.txt" 2>&1
git rev-parse HEAD >> "$D/21-control-clon-wiring.txt" 2>&1

echo "### tmp_test existe en el clon?" >> "$D/21-control-clon-wiring.txt"
ls -d "$CLON/tmp_test" 2>&1 >> "$D/21-control-clon-wiring.txt"
echo "  ^ (no such file = el arbol commiteado no lo lleva)" >> "$D/21-control-clon-wiring.txt"

echo "### el mismo test, corrido dentro del clon" >> "$D/21-control-clon-wiring.txt"
( cd "$CLON" && python -m pytest -q -ra "tests/test_validate_wiring.py::test_toda_la_poblacion_no_resuelta_queda_fuera_de_produccion" ) \
  >> "$D/21-control-clon-wiring.txt" 2>&1
echo "EXIT_CLON_TEST=$?" >> "$D/21-control-clon-wiring.txt"

echo "### y la poblacion del verificador en el clon" >> "$D/21-control-clon-wiring.txt"
( cd "$CLON" && python -c "import importlib.util,sys;from pathlib import Path;R=Path('.').resolve();s=importlib.util.spec_from_file_location('vw','scripts/validate_wiring.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);r=m.construir_reporte(R);print('archivos_en_alcance',r['cobertura']['archivos_en_alcance']);print('archivos_excluidos_por_rol',r['cobertura']['archivos_excluidos_por_rol']);print('receptores_no_resueltos_en_produccion',r['cobertura']['receptores_no_resueltos_en_produccion'])" ) \
  >> "$D/21-control-clon-wiring.txt" 2>&1
echo "EXIT_CLON_POBLACION=$?" >> "$D/21-control-clon-wiring.txt"

rm -rf "$CLON"
echo "### clon retirado (borro solo el directorio que esta instruccion creo)" >> "$D/21-control-clon-wiring.txt"
echo "HECHO" >> "$D/21-control-clon-wiring.txt"
