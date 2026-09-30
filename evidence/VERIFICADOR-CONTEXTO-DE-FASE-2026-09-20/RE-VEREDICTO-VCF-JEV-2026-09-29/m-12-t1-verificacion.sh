#!/bin/sh
# T1 - verificacion por DESCARGA + sha256 (la descarga la hace la shell: 'qmind' no resuelve desde
# subprocess de Python en Windows). El id se resuelve por titulo exacto contra el listado, no transcrito.
D="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VEREDICTO-VCF-JEV-2026-09-29"
NB="01a04d98-b7bd-778c-8441-26fdc7e35f45"
TITULO="10-analisis: VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 (cierre formal 2026-09-27, lecciones finales 2026-09-29)"

python "$D/m-12a-id-nueva.py" "$D" "$TITULO" > "$D/12a-id-nueva.txt" 2>&1
echo "EXIT_ID=$?" >> "$D/12a-id-nueva.txt"
ID=$(head -1 "$D/12a-id-nueva.txt")

case "$ID" in
  01a0*)
    qmind source download "$ID" --nb "$NB" -o "$D/descarga-$ID.md" --overwrite > "$D/12b-descarga-nueva.log" 2>&1
    echo "EXIT_DOWNLOAD_NUEVA=$?" >> "$D/12b-descarga-nueva.log"
    ;;
  *)
    echo "SIN-DESCARGA: la primera linea de 12a-id-nueva.txt no es un source_id ($ID)" > "$D/12b-descarga-nueva.log"
    ;;
esac

# El reporte lo escribe el propio guion en UTF-8 con newline="\n"; stdout (ASCII) va a su propio log.
python "$D/m-12b-verifica.py" "$D" "$TITULO" > "$D/12c-verifica-stdout.log" 2>&1
echo "EXIT_VERIFICACION=$?" >> "$D/12c-verifica-stdout.log"
