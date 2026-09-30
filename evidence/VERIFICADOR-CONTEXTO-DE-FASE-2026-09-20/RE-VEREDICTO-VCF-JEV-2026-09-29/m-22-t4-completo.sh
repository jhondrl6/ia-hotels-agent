#!/bin/sh
# T4 - modo completo: los 17 checks, incluida la suite de pytest completa (larga).
# EXIT del proceso capturado sin tuberia. Los verificadores de arbol se AUTOCLONAN y no toman
# --check: se corren sin argumento dentro del runner.
D="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VEREDICTO-VCF-JEV-2026-09-29"
python scripts/run_all_validations.py > "$D/22-t4-modo-completo.txt" 2>&1
echo "EXIT_T4_COMPLETO=$?" >> "$D/22-t4-modo-completo.txt"
