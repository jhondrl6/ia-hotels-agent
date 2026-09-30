#!/bin/sh
# Instrumento P0-4: lectura del notebook y descarga de los snapshots para medirlos por sha256.
# Solo lectura: no sube ni borra nada. El JSON queda limpio (el exit va a su propio log).
D="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VEREDICTO-VCF-JEV-2026-09-29"
NB="01a04d98-b7bd-778c-8441-26fdc7e35f45"

qmind source list --nb "$NB" --all --format json > "$D/01-source-list.json" 2> "$D/01b-list-stderr.log"
echo "EXIT_LIST_JSON=$?" > "$D/01c-list-exit.txt"

for id in 01a0e464-3331-7684-9742-f64e009fb10b 01a0e0d3-92db-795b-ad7a-48a7c322e8e9 01a0e4d9-b252-7ca0-bf4c-9a9ecc7448f5 01a0e4d9-e442-7d1b-bde5-7e9b669a2701 01a0ef0e-aa1c-7e5d-8486-51d40b8b4f07; do
  qmind source download "$id" --nb "$NB" -o "$D/descarga-$id.md" --overwrite > "$D/02-descarga-$id.log" 2>&1
  echo "EXIT_DOWNLOAD=$?" >> "$D/02-descarga-$id.log"
done

python "$D/m-01-comparacion.py" "$D" > "$D/03b-comparacion-stdout.log" 2>&1
echo "EXIT_COMPARACION=$?" >> "$D/03b-comparacion-stdout.log"
