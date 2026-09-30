#!/usr/bin/env bash
# Baseline POR POBLACION: las baterias de cada T, con su EXIT real escrito sin tuberia.
# Uso: bash m-02-baseline-por-poblacion.sh <salida>
set -u
OUT="$1"
{
  echo "# baseline por poblacion — revision leida: $(git rev-parse HEAD)"
  echo "# fecha: $(date -Iseconds)"
  for sel in \
    "tests/test_registry_fecha_documental.py|T1_log_phase_completion" \
    "tests/test_verify_packs_in_committed_tree.py|T2_verificador_de_packs" \
    "tests/quality_gates/phase_briefing/|T2T3_fase_briefing" \
    "tests/test_validate_lesson_capitalization.py|T4_capitalizacion_lecciones" \
    "tests/test_run_all_validations_denominador_por_modo.py|T3_denominador_por_modo" \
    "tests/test_validate_wiring.py|T5c_wiring_check" \
    "tests/test_verify_index_in_committed_tree.py|hermano_indice_committed_tree" \
    "tests/quality_gates/governance_numbers/|T3_gobernanza_numeros" \
    "tests/test_qmind_writeback.py|T3_hermano_writeback" \
    ; do
    ruta="${sel%%|*}"
    etiqueta="${sel#*|}"
    echo ""
    echo "=== $etiqueta :: $ruta ==="
    if [ ! -e "$ruta" ]; then
      echo "RUTA-AUSENTE (no es poblacion esta sesion)"
      continue
    fi
    python -m pytest "$ruta" -q 2>&1
    echo "EXIT_$etiqueta=$?"
  done
} > "$OUT"
