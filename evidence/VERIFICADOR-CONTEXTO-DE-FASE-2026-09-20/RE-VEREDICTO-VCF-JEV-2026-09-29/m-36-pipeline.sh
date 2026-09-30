#!/bin/sh
# PIPELINE DE CIERRE (orden de la casa): sellos fechados -> packs -> indice -> --check de ambos ->
# quick -> git diff --check. Ningun paso commitea. Cada EXIT se captura sin tuberia.
D="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VEREDICTO-VCF-JEV-2026-09-29"
V=".opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"

echo "### 1. Estado de los archivos tocados: finales de linea y balance de marcadores" > "$D/36-pipeline-sellos-y-eol.txt"
for f in "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VERIFICACION-VCF-JEV-2026-09-28/00-expediente.md" "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/SESION-SCRIPTS-CURAS-2026-09-28/00-resumen.md" "$D/00-expediente.md"; do
  printf "%s\n  CR=%s  LF=%s  aperturas=%s  cierres=%s\n" "$f" \
    "$(tr -cd '\r' < "$f" | wc -c)" "$(tr -cd '\n' < "$f" | wc -c)" \
    "$(grep -o -F "$(printf '\xe2\x9d\xa6')" "$f" | wc -l)" "$(grep -o -F "$(printf '\xe2\x9d\xa7')" "$f" | wc -l)" >> "$D/36-pipeline-sellos-y-eol.txt"
done
python scripts/validate_document_integration.py > "$D/37-pipeline-integracion-documental.txt" 2>&1
echo "EXIT_INTEGRACION=$?" >> "$D/37-pipeline-integracion-documental.txt"

echo "### 2. Packs: primero --check (sin escribir). Solo se regeneran si corta rojo." > "$D/38-pipeline-packs-e-indice.txt"
python scripts/build_phase_briefing.py --plan "Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20" --check >> "$D/38-pipeline-packs-e-indice.txt" 2>&1
echo "EXIT_PACKS_CHECK=$?" >> "$D/38-pipeline-packs-e-indice.txt"
python scripts/build_lesson_index.py --check >> "$D/38-pipeline-packs-e-indice.txt" 2>&1
echo "EXIT_INDICE_CHECK=$?" >> "$D/38-pipeline-packs-e-indice.txt"
sha256sum .opencode/LECCIONES-INDEX.md .opencode/lecciones_index.json >> "$D/38-pipeline-packs-e-indice.txt" 2>&1
echo "  ^ par del indice, para probar si esta intacto contra lo versionado" >> "$D/38-pipeline-packs-e-indice.txt"
sha256sum "$V"/briefing/*.md >> "$D/38-pipeline-packs-e-indice.txt" 2>&1
echo "  ^ los cinco packs" >> "$D/38-pipeline-packs-e-indice.txt"

echo "### 3. Quick (13 checks)" > "$D/39-pipeline-quick.txt"
python scripts/run_all_validations.py --quick >> "$D/39-pipeline-quick.txt" 2>&1
echo "EXIT_QUICK=$?" >> "$D/39-pipeline-quick.txt"

echo "### 4. git diff --check y poblacion del arbol" > "$D/40-pipeline-diff-y-poblacion.txt"
git diff --check >> "$D/40-pipeline-diff-y-poblacion.txt" 2>&1
echo "EXIT_DIFF_CHECK=$?" >> "$D/40-pipeline-diff-y-poblacion.txt"
git diff --stat >> "$D/40-pipeline-diff-y-poblacion.txt" 2>&1
echo "EXIT_DIFF_STAT=$?" >> "$D/40-pipeline-diff-y-poblacion.txt"
git status --porcelain >> "$D/40-pipeline-diff-y-poblacion.txt" 2>&1
echo "EXIT_PORCELAIN=$?" >> "$D/40-pipeline-diff-y-poblacion.txt"
echo "### 5. Conteos de la evidencia de esta sesion" >> "$D/40-pipeline-diff-y-poblacion.txt"
echo -n "archivos totales: " >> "$D/40-pipeline-diff-y-poblacion.txt"; ls -1 "$D" | wc -l >> "$D/40-pipeline-diff-y-poblacion.txt"
echo -n "instrumentos m-*: " >> "$D/40-pipeline-diff-y-poblacion.txt"; ls -1 "$D" | grep -c '^m-' >> "$D/40-pipeline-diff-y-poblacion.txt"
echo -n "descargas: " >> "$D/40-pipeline-diff-y-poblacion.txt"; ls -1 "$D" | grep -c '^descarga-' >> "$D/40-pipeline-diff-y-poblacion.txt"
echo "HECHO-PIPELINE" >> "$D/36-pipeline-sellos-y-eol.txt"
