#!/bin/bash
# 09 — censo de deudas y decisiones de los dos planes, leido de sus fuentes
cd /c/Users/Jhond/Github/iah-cli || exit 1
V=".opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"
J=".opencode/plans/Archives/EVALUACION-JEV-TYPESAFE-2026-09-21"

echo "### A. Filas D1..D10 de la §Deuda registrada del plan VCF (dependencias-fases.md:106-119)"
echo "-- cada fila empieza por '| D' o '| **D' en la tabla de deuda"
awk 'NR>=108 && NR<=119' "$V/dependencias-fases.md" | grep -oE '^\| \*?\*?D[0-9]+' | tr -d '|' | sed 's/^ *//'

echo
echo "### B. Que dice el Cierre formal (dependencias-fases.md:1042-1057) sobre el libro del plan"
sed -n '1042,1057p' "$V/dependencias-fases.md"

echo
echo "### C. Estado explicito de D1 en la matriz §13 (fuente unica, 00-resumen-cierre-B.md:126-130)"
sed -n '126,131p' "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md"

echo
echo "### D. Las dos filas RECHAZADO de §11 (hallazgos 16 y 17)"
grep -n 'RECHAZADO' "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md"

echo
echo "### E. Denominadores VIVOS del verificador hoy (prueba de que la cifra publicada caduca)"
echo "-- etiquetas [N/M] que imprime run_all_validations.py"
grep -oE 'print\("\[[0-9]+/[0-9]+\]' scripts/run_all_validations.py | sed 's/print("//' | sort -u -V | tr '\n' ' '
echo
echo "-- cuantas lineas de quick usan el denominador 13"
grep -oE '\[[0-9]+/13\]' scripts/run_all_validations.py | sort -u -V | wc -l
echo "-- cuantas lineas del modo completo usan el denominador 17"
grep -oE '\[[0-9]+/17\]' scripts/run_all_validations.py | sort -u -V | wc -l

echo
echo "### F. Nota congelada de AC16 (maestro:182), citada textual"
sed -n '182p' "$V/01-plan-maestro.md"

echo
echo "### G. Las tres lineas de validate_governance_numbers.py que apuntan a D1 (deuda D-A)"
grep -n 'D1' scripts/validate_governance_numbers.py

echo
echo "### H. S10 y S14 en el plan VCF (las vivas que nombra el cierre formal)"
grep -rn 'S10\b' "$V/00-lecciones-capitalizadas.md" | head -4 | cut -c1-240
echo "---"
grep -rn 'S14\b' "$V/00-lecciones-capitalizadas.md" | head -4 | cut -c1-240

echo
echo "### I. Filas de decisiones del plan JEV (dependencias-fases.md del plan archivado)"
grep -n '^| \*\*D\|^| D' "$J/dependencias-fases.md" | cut -c1-240

echo
echo "### J. AC3 del plan JEV y su clausula, para la decision D-B"
grep -n 'AC3' "$J/01-plan-maestro.md" | cut -c1-260
