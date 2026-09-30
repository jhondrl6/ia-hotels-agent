#!/bin/sh
# T1 - D-E(a): re-ingesta del snapshot VENCIDO (unico de la poblacion que el Paso 0 midio vencido).
# Con titulo NUEVO que conserva el stem: el --upload responde SKIP por titulo y dejaria la version vieja
# como verdad publicada. Verificacion por DESCARGA + sha256, nunca por titulo.
D="evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VEREDICTO-VCF-JEV-2026-09-29"
NB="01a04d98-b7bd-778c-8441-26fdc7e35f45"
F=".opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/10-analisis-post-implementacion.md"
TITULO="10-analisis: VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 (cierre formal 2026-09-27, lecciones finales 2026-09-29)"

sha256sum "$F" > "$D/07-t1-local-sha.txt" 2>&1
wc -c "$F" >> "$D/07-t1-local-sha.txt"

qmind source upload --non-interactive --format json --nb "$NB" --file "$F" --title "$TITULO" > "$D/08-t1-upload.json" 2> "$D/08b-t1-upload-stderr.log"
echo "EXIT_UPLOAD=$?" > "$D/08c-t1-upload-exit.txt"

qmind source list --nb "$NB" --all --format json > "$D/09-source-list-post-t1.json" 2> "$D/09b-list-post-stderr.log"
echo "EXIT_LIST_POST=$?" > "$D/09c-list-post-exit.txt"

python "$D/m-09-verifica-subida.py" "$D" "$NB" "$TITULO" > "$D/10-t1-verificacion.txt" 2>&1
echo "EXIT_VERIFICACION=$?" >> "$D/10-t1-verificacion.txt"
