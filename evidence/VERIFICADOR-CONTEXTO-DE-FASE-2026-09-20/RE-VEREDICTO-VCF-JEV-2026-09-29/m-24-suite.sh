#!/bin/sh
# T4b - la suite completa con su detalle, porque [16/17] del runner trunca la salida de pytest.
# Mismo comando que el runner usa; EXIT del proceso capturado sin tuberia.
D="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VEREDICTO-VCF-JEV-2026-09-29"
python -m pytest -q -ra > "$D/24-t4b-suite-completa.txt" 2>&1
echo "EXIT_SUITE=$?" >> "$D/24-t4b-suite-completa.txt"
