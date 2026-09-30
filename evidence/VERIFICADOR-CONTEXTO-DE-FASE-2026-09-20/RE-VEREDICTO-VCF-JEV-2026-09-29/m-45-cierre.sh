#!/bin/sh
# Cierre: re-corrida de la verificacion DESPUES de las ultimas anotaciones. No conmuta nada.
D="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VEREDICTO-VCF-JEV-2026-09-29"

python "$D/m-41-balance.py" "$D" > "$D/45b-rebalance-stdout.log" 2>&1
echo "EXIT_REBALANCE=$?" >> "$D/45b-rebalance-stdout.log"
python "$D/m-42-inclusion.py" "$D" > "$D/45c-reinclusion-stdout.log" 2>&1
echo "EXIT_REINCLUSION=$?" >> "$D/45c-reinclusion-stdout.log"

python scripts/run_all_validations.py --quick > "$D/46-cierre-quick.txt" 2>&1
echo "EXIT_QUICK_FINAL=$?" >> "$D/46-cierre-quick.txt"

{
  echo "### numstat y diff --check del estado final"
  git diff --check
  echo "EXIT_DIFF_CHECK=$?"
  git diff --numstat
  echo "EXIT_NUMSTAT=$?"
  echo "### porcelain"
  git status --porcelain
  echo "### conteos"
  git status --porcelain | wc -l
  git status --porcelain -uno | wc -l
  echo "### inventario de este expediente"
  ls -1 "$D" | wc -l
  ls -1 "$D" | grep -c '^m-'
  ls -1 "$D" | grep -c '^descarga-'
  echo "### cifras canonicas de tests (disco y arbol versionado)"
  grep -rE "^\s*def test_" tests --include=*.py | wc -l
  git grep -c -E "^\s*def test_" HEAD -- tests | awk -F: '{t+=$NF} END {print t+0}'
} > "$D/45-cierre-final.txt" 2>&1
