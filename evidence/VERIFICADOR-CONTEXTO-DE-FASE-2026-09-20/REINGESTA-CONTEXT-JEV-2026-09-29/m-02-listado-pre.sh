#!/bin/bash
# Instrumento m-02: listado PRE del notebook (Paso 0.4) y control anti-gemelo del stem del CONTEXT.
# El EXIT de qmind se captura sin tuberia; el conteo de titulos lo hace un instrumento propio (m-02a.py) sobre el JSON persistido.
E="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/REINGESTA-CONTEXT-JEV-2026-09-29"
NB="01a04d98-b7bd-778c-8441-26fdc7e35f45"

qmind source list --nb "$NB" --all --format json > "$E/02-source-list-pre.json" 2>"$E/02b-list-pre-stderr.txt"
EX1=$?
qmind source list --nb "$NB" --all > "$E/02c-list-pre-tabla.txt" 2>"$E/02d-list-pre-tabla-stderr.txt"
EX2=$?

{
  echo "fecha_medicion=$(date +%F)  hora=$(date -Iseconds)"
  echo "notebook=$NB"
  echo "-- listado json --"
  echo "EXIT_LIST_JSON=$EX1"
  echo "bytes_json=$(wc -c < "$E/02-source-list-pre.json")"
  echo "-- listado tabla --"
  echo "EXIT_LIST_TABLA=$EX2"
  echo "Total impresos por la tabla (linea que empieza por Total):"
  grep -n "^Total" "$E/02c-list-pre-tabla.txt"
  echo "GREP_TOTAL_EXIT=$?"
  echo "stderr json:"
  cat "$E/02b-list-pre-stderr.txt"
  echo "stderr tabla:"
  cat "$E/02d-list-pre-tabla-stderr.txt"
} > "$E/02e-list-pre-resumen.txt" 2>&1
echo "EXIT_RESUMEN=$?"
cat "$E/02e-list-pre-resumen.txt"
