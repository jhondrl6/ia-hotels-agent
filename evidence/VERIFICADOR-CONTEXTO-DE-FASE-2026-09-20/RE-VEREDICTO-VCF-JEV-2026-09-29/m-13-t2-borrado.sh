#!/bin/sh
# T2 - D-E(b): borrado del gemelo vencido (IRREVERSIBLE, autorizado por la pegada de la orden).
# Se borra 01a0e0d3-92db-795b-ad7a-48a7c322e8e9: repite TITULO exacto con 01a0e464 y su contenido es
# la version anterior (94.984 B / fd9829dc...). No se toca 01a0e464 (la version original del plan, que
# vive en el notebook con su titulo propio) ni la nueva 01a0ef39 (la de cierre, FRESCA).
D="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VEREDICTO-VCF-JEV-2026-09-29"
NB="01a04d98-b7bd-778c-8441-26fdc7e35f45"
ID="01a0e0d3-92db-795b-ad7a-48a7c322e8e9"

qmind source get "$ID" --nb "$NB" > "$D/13-pre-borrado-get.txt" 2>&1
echo "EXIT_GET_PRE=$?" >> "$D/13-pre-borrado-get.txt"

qmind source delete "$ID" --nb "$NB" --force > "$D/14-t2-delete.txt" 2>&1
echo "EXIT_DELETE=$?" >> "$D/14-t2-delete.txt"

qmind source list --nb "$NB" --all > "$D/15-post-borrado-tabla.txt" 2>&1
echo "EXIT_LIST_TABLA=$?" >> "$D/15-post-borrado-tabla.txt"

qmind source list --nb "$NB" --all --format json > "$D/16-source-list-post-t2.json" 2>&1
echo "EXIT_LIST_JSON=$?" > "$D/16b-list-json-exit.txt"

# El reporte lo escribe el guion en UTF-8 con newline="\n"; su stdout va a otro archivo.
python "$D/m-15-cierre-notebook.py" "$D" "$ID" > "$D/17b-cierre-stdout.log" 2>&1
echo "EXIT_CIERRE=$?" >> "$D/17b-cierre-stdout.log"
