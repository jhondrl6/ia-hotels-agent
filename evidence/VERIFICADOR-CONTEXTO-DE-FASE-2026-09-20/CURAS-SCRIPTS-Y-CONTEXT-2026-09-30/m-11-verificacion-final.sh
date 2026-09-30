#!/usr/bin/env bash
# Verificacion final de la tanda: cola de writers -> checks -> quick -> estrictos -> suite ->(identity).
# Cada EXIT se lee sin tuberia y queda escrito en el crudo.
set -u
OUT="$1"
RAIZ="$(git rev-parse --show-toplevel)"
cd "$RAIZ" || exit 70
PLAN="VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"

{
  echo "# verificacion final — tanda CURAS-SCRIPTS-Y-CONTEXT-2026-09-30"
  echo "# revision de partida: $(git rev-parse HEAD)"
  echo "# fecha: $(date -Iseconds)"

  echo ""
  echo "== [1/9] packs (regenerados con la cola de la casa) =="
  python scripts/build_phase_briefing.py --plan "$PLAN"
  echo "PACKS_EXIT=$?"

  echo ""
  echo "== [2/9] indice =="
  python scripts/build_lesson_index.py
  echo "INDICE_EXIT=$?"

  echo ""
  echo "== [3/9] packs --check =="
  python scripts/build_phase_briefing.py --plan "$PLAN" --check
  echo "PACKS_CHECK_EXIT=$?"

  echo ""
  echo "== [4/9] indice --check =="
  python scripts/build_lesson_index.py --check
  echo "INDICE_CHECK_EXIT=$?"

  echo ""
  echo "== [5/9] run_all_validations --quick =="
  python scripts/run_all_validations.py --quick
  echo "QUICK_EXIT=$?"

  echo ""
  echo "== [6/9] validate_qmind_writeback --strict =="
  python scripts/validate_qmind_writeback.py --strict
  echo "WRITEBACK_STRICT_EXIT=$?"

  echo ""
  echo "== [7/9] verificador nuevo de frescura de CONTEXT =="
  python scripts/verify_qmind_context_freshness.py
  echo "CONTEXT_FRESHNESS_EXIT=$?"

  echo ""
  echo "== [8/9] git diff --check =="
  git diff --check
  echo "DIFF_CHECK_EXIT=$?"

  echo ""
  echo "== [9/9] suite completa =="
  python -m pytest tests/ -q
  echo "EXIT_SUITE=$?"

  echo ""
  echo "== identidad del arbol =="
  echo "HEAD: $(git rev-parse HEAD)"
  echo "status -uno: $(git status --porcelain -uno | wc -l) lineas"
  echo "paridad: $(git rev-list --left-right --count origin/master...HEAD)"
} > "$OUT" 2>&1
