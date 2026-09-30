#!/bin/sh
# Instrumento P0-4a: listado del notebook iah-cli-lecciones (esperado Total: 55)
D="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VEREDICTO-VCF-JEV-2026-09-29"
qmind source list --nb 01a04d98-b7bd-778c-8441-26fdc7e35f45 --all > "$D/00-source-list.txt" 2>&1
echo "EXIT_SOURCE_LIST=$?" >> "$D/00-source-list.txt"
