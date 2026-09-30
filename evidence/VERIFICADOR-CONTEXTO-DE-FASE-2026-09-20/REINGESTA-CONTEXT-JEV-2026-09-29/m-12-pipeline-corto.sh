#!/bin/bash
# Instrumento m-12: pipeline de cierre, pasos 1 a 3 (write-back estricto, packs, indice).
# Cada EXIT se captura sin tuberia. Ningun paso regenera nada: son --check.
E="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/REINGESTA-CONTEXT-JEV-2026-09-29"

python scripts/validate_qmind_writeback.py --strict > "$E/12-writeback-strict.txt" 2>&1
W=$?

python scripts/build_phase_briefing.py --plan Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 --check > "$E/13a-packs-check.txt" 2>&1
P=$?
python scripts/build_lesson_index.py --check > "$E/13b-indice-check.txt" 2>&1
I=$?

{
  echo "fecha_pipeline=$(date +%F)  hora=$(date -Iseconds)"
  echo "== validate_qmind_writeback.py --strict =="
  echo "EXIT=$W"
  cat "$E/12-writeback-strict.txt"
  echo
  echo "== build_phase_briefing.py --check (no se regenero nada) =="
  echo "EXIT=$P"
  cat "$E/13a-packs-check.txt"
  echo
  echo "== build_lesson_index.py --check =="
  echo "EXIT=$I"
  cat "$E/13b-indice-check.txt"
} > "$E/13-pipeline-paso1-3.txt" 2>&1
cat "$E/13-pipeline-paso1-3.txt"
