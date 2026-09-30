#!/bin/bash
# Instrumento m-19: bateria antes de stagear (la practica de la casa antes de cada commit).
E="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/REINGESTA-CONTEXT-JEV-2026-09-29"

python scripts/validate_qmind_writeback.py --strict > "$E/29a-strict.txt" 2>&1; W=$?
python scripts/build_phase_briefing.py --plan Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 --check > "$E/29b-packs.txt" 2>&1; P=$?
python scripts/build_lesson_index.py --check > "$E/29c-indice.txt" 2>&1; I=$?
python scripts/run_all_validations.py --quick > "$E/29d-quick.txt" 2>&1; Q=$?
git diff --check > "$E/29e-diff-check.txt" 2>&1; D=$?
ls evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/REINGESTA-CONTEXT-JEV-2026-09-29/ | grep -c "\.log$" > "$E/29f-conteo-log.txt" 2>&1; L=$?

{
  echo "fecha_bateria=$(date +%F)  hora=$(date -Iseconds)"
  echo "EXIT_STRICT=$W"
  cat "$E/29a-strict.txt"
  echo "EXIT_PACKS=$P"
  tail -2 "$E/29b-packs.txt"
  echo "EXIT_INDICE=$I"
  tail -2 "$E/29c-indice.txt"
  echo "EXIT_QUICK=$Q"
  grep -E "TOTAL:|STATUS:|GUARDA" "$E/29d-quick.txt"
  echo "EXIT_DIFF_CHECK=$D  lineas=$(wc -l < "$E/29e-diff-check.txt")"
  echo "EXIT_CONTEO_LOG=$L  (grep -c devuelve 1 cuando el conteo es 0: el numero de arriba es el que vale)"
  cat "$E/29f-conteo-log.txt"
} > "$E/29-bateria-pre-commit.txt" 2>&1
cat "$E/29-bateria-pre-commit.txt"
