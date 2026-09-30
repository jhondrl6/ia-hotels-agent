#!/usr/bin/env bash
# Instrumento de baseline: suite completa sobre el arbol intacto, con EXIT real escrito.
# Uso: bash m-00-baseline-suite-completa.sh <salida>
set -u
OUT="$1"
{
  echo "# baseline suite completa — revision leida: $(git rev-parse HEAD)"
  echo "# fecha: $(date -Iseconds)"
  python -m pytest tests/ -q 2>&1
  echo "EXIT_SUITE=$?"
} > "$OUT"
