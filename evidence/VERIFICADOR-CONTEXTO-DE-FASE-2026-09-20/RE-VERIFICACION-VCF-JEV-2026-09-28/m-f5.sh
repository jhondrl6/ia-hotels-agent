#!/bin/bash
# F5 — REGISTRY sin entrada de la FASE-A del plan JEV + estado del escritor
cd /c/Users/Jhond/Github/iah-cli || exit 1

echo "=== 1. Menciones del plan en REGISTRY (ocurrencias, no lineas) ==="
echo "-- git grep -o -F 'EVALUACION-JEV-TYPESAFE-2026-09-21' HEAD -- docs/contributing/REGISTRY.md | wc -l"
git grep -o -F 'EVALUACION-JEV-TYPESAFE-2026-09-21' HEAD -- docs/contributing/REGISTRY.md | wc -l
echo "-- grep -o -F sobre el archivo en disco | wc -l"
grep -o -F 'EVALUACION-JEV-TYPESAFE-2026-09-21' docs/contributing/REGISTRY.md | wc -l
echo "-- grep -n 'EVALUACION-JEV' sobre el archivo en disco"
grep -n 'EVALUACION-JEV' docs/contributing/REGISTRY.md || echo "(sin coincidencias)"

echo
echo "=== 2. Menciones del plan VCF en REGISTRY (contraste: si tiene entradas) ==="
echo "-- ocurrencias de VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"
grep -o -F 'VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20' docs/contributing/REGISTRY.md | wc -l
echo "-- cabeceras de seccion que lo nombran"
grep -n '^## .*VERIFICADOR-CONTEXTO-DE-FASE' docs/contributing/REGISTRY.md || echo "(sin cabecera)"

echo
echo "=== 3. Cabecera de ultima actualizacion del REGISTRY versionado ==="
grep -n 'Ultima actualizacion' docs/contributing/REGISTRY.md | head -3

echo
echo "=== 4. Que soporta el escritor log_phase_completion.py (lectura de su argparse) ==="
python scripts/log_phase_completion.py --help 2>&1 | head -40
echo "EXIT_HELP=$?"

echo
echo "=== 5. Busqueda de soporte de nota datada / entrada tardia en el escritor ==="
grep -n 'add_argument' scripts/log_phase_completion.py

echo
echo "=== 6. Ejemplos de cabeceras de entrada en REGISTRY (formato que emite el escritor) ==="
grep -n '^## ' docs/contributing/REGISTRY.md | tail -8

echo
echo "=== 7. Prueba de la rama 'el escritor soporta entrada tardia con nota datada' ==="
echo "-- se corre con --dry-run (no escribe: verify despues con git status -uno)"
python scripts/log_phase_completion.py --fase "EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-A" \
  --desc "prueba dry-run de entrada tardia" --dry-run 2>&1 | head -14
echo "-- EXIT del dry-run: ver linea siguiente"
echo "-- git status --porcelain -uno despues del dry-run (0 = no escribio nada)"
git status --porcelain -uno | wc -l
echo "-- grep de las opciones del escritor: hay flag de fecha o de nota? (add_argument)"
grep -n 'add_argument' scripts/log_phase_completion.py
echo "-- como se calcula la fecha de la cabecera de la entrada"
grep -n 'fecha = \|## {fase_id}' scripts/log_phase_completion.py
